"""Train a regularized linear duration model and export it as pure JSON.

Pipeline stages: load -> validate (data contract) -> encode features ->
split -> fit StandardScaler + linear estimator -> evaluate against the naive
baseline -> write artifact + metrics. Promotion and reload stay in their own
CLIs (promote_duration_model.py, POST /model/reload).

The artifact stores scaler statistics and coefficients as plain JSON
(`model_type: "linear-json"`), so the serving path reproduces the exact
sklearn pipeline with stdlib arithmetic — no scikit-learn in the runtime
image, no pickle, human-inspectable weights. The cost is that only linear
models can ship this way; tests/test_training_serving_parity.py guards the
re-implementation.

Requires the optional training dependencies:

    python -m pip install -r ml-service/training/requirements-training.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.data_contract import (
    encode_features,
    feature_names,
    linear_predict,
    normalize_category,
    validate_rows,
)
from artifact_meta import build_artifact_metadata
from clearml_utils import track_training_run
from eval_metrics import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    error_summary,
    has_sufficient_evidence,
    improvement_ratio,
)
from train_duration_model import (
    DEFAULT_ARTIFACT_DIR,
    DEFAULT_FEEDBACK_PATH,
    DEFAULT_INPUT_PATH,
    DEFAULT_SEED,
    load_training_rows,
    split_rows,
    write_json,
)

MODEL_NAME = "duration-linear"
MODEL_VERSION = "0.3.0"

ESTIMATOR_NAMES = ("ridge", "elastic-net")


def make_estimator(estimator_name: str):
    from sklearn.linear_model import ElasticNet, Ridge

    if estimator_name == "ridge":
        return Ridge(alpha=1.0)
    return ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000)


class DatasetValidationError(Exception):
    """Raised when the training dataset violates the data contract."""


def train_linear_model(
    input_path: Path = DEFAULT_INPUT_PATH,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    feedback_path: Path | None = None,
    seed: int = DEFAULT_SEED,
    estimator_name: str = "elastic-net",
) -> dict:
    if estimator_name not in ESTIMATOR_NAMES:
        raise ValueError(f"unknown estimator {estimator_name!r}; choose from {sorted(ESTIMATOR_NAMES)}")

    rows = load_training_rows(input_path)
    feedback_rows: list[dict] = []
    if feedback_path is not None and feedback_path.exists():
        feedback_rows = load_training_rows(feedback_path, allow_empty=True)

    all_rows = rows + feedback_rows
    report = validate_rows(all_rows)
    if not report.ok:
        raise DatasetValidationError("; ".join(report.errors))

    train_rows_list, evaluation_rows_list, evaluation_mode = split_rows(all_rows, seed)
    model = fit_linear_artifact(train_rows_list, estimator_name)
    model["seed"] = seed
    model["feedback_rows"] = len(feedback_rows)
    model.update(
        build_artifact_metadata(
            dataset_paths=[input_path] + ([feedback_path] if feedback_path is not None else []),
            training_rows=len(train_rows_list),
            evaluation_rows=len(evaluation_rows_list),
            evaluation_strategy=evaluation_mode,
        )
    )
    metrics = evaluate_linear_model(evaluation_rows_list, model, evaluation_mode, seed)
    metrics["feedback_rows"] = len(feedback_rows)
    # Large corpora produce thousands of duplicate/ratio warnings; keep the
    # metrics file readable and store the full count.
    metrics["validation_warning_count"] = len(report.warnings)
    metrics["validation_warnings"] = report.warnings[:10]

    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "duration_model.json", model)
    write_json(artifact_dir / "duration_metrics.json", metrics)
    clearml_task_id = track_training_run(
        model,
        metrics,
        artifact_dir,
        dataset_paths=[input_path] + ([feedback_path] if feedback_path is not None else []),
    )
    return {"model": model, "metrics": metrics, "clearml_task_id": clearml_task_id}


def fit_linear_artifact(train_rows: list[dict], estimator_name: str) -> dict:
    from sklearn.preprocessing import StandardScaler

    categories = sorted({normalize_category(row["category"]) for row in train_rows})
    features = encode_features(train_rows, categories)
    targets = [float(row["actual_minutes"]) for row in train_rows]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    estimator = make_estimator(estimator_name)
    estimator.fit(scaled, targets)

    model = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "model_type": "linear-json",
        "estimator": estimator_name,
        "source": "local-artifact",
        "seed": None,
        "categories": categories,
        "feature_names": feature_names(categories),
        "scaler_mean": [round(float(v), 6) for v in scaler.mean_],
        "scaler_scale": [round(float(v), 6) for v in scaler.scale_],
        "coefficients": [round(float(v), 6) for v in estimator.coef_],
        "intercept": round(float(estimator.intercept_), 6),
        "estimated_minutes_range": [
            min(row["estimated_minutes"] for row in train_rows),
            max(row["estimated_minutes"] for row in train_rows),
        ],
    }
    model["category_mae"], model["global_mae"], model["category_sample_counts"] = build_linear_error_profile(
        train_rows, model
    )
    return model


def predict_linear_row(row: dict, model: dict) -> float:
    """Training-side alias for the shared contract inference (single source)."""
    return linear_predict(row, model)


def build_linear_error_profile(rows: list[dict], model: dict) -> tuple[dict[str, float], float, dict[str, int]]:
    """Per-category training residuals; serving derives reliability from these.

    Training residuals understate true error (the model has seen these rows);
    holdout metrics in duration_metrics.json are the honest generalization
    numbers. Sample counts ship alongside so serving can say how much data
    backs each category.
    """
    errors_by_category: dict[str, list[float]] = {}
    for row in rows:
        error = abs(predict_linear_row(row, model) - row["actual_minutes"])
        errors_by_category.setdefault(normalize_category(row["category"]), []).append(error)

    category_mae = {category: round(mean(errors), 2) for category, errors in sorted(errors_by_category.items())}
    global_mae = round(mean(error for errors in errors_by_category.values() for error in errors), 2)
    sample_counts = {category: len(errors) for category, errors in sorted(errors_by_category.items())}
    return category_mae, global_mae, sample_counts


def evaluate_linear_model(rows: list[dict], model: dict, evaluation_mode: str, seed: int) -> dict:
    model_predictions = [predict_linear_row(row, model) for row in rows]
    naive_predictions = [float(row["estimated_minutes"]) for row in rows]
    actuals = [float(row["actual_minutes"]) for row in rows]

    model_summary = error_summary(model_predictions, actuals)
    baseline_summary = error_summary(naive_predictions, actuals)
    sufficient = has_sufficient_evidence(len(rows)) and evaluation_mode == "holdout"

    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "estimator": model["estimator"],
        "seed": seed,
        "evaluation_mode": evaluation_mode,
        "training_rows": model["training_rows"],
        "evaluation_rows": len(rows),
        "model_mae": model_summary["mae"],
        "model_median_ae": model_summary["median_ae"],
        "model_rmse": model_summary["rmse"],
        "baseline_mae": baseline_summary["mae"],
        "baseline_median_ae": baseline_summary["median_ae"],
        "baseline_rmse": baseline_summary["rmse"],
        "improvement_ratio": improvement_ratio(model_summary["mae"], baseline_summary["mae"]),
        "sufficient_evidence": sufficient,
        "evidence_note": (
            f"holdout of {len(rows)} rows meets the evidence threshold"
            if sufficient
            else f"{len(rows)} {evaluation_mode} rows; {INSUFFICIENT_EVIDENCE_MESSAGE}"
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the linear duration model exported as pure JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument(
        "--feedback",
        type=Path,
        default=DEFAULT_FEEDBACK_PATH,
        help="Optional execution-feedback CSV merged into training data when the file exists.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--estimator", choices=sorted(ESTIMATOR_NAMES), default="elastic-net")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = train_linear_model(
        input_path=args.input,
        artifact_dir=args.artifact_dir,
        feedback_path=args.feedback,
        seed=args.seed,
        estimator_name=args.estimator,
    )
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
