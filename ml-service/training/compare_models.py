"""Compare candidate duration models with cross-validation.

Answers "why this model and not something bigger?" with numbers instead of
opinions. Each candidate is fit per fold and scored on held-out rows, so the
table shows out-of-sample error at the current data size. Row-level errors
are pooled across folds for Median AE / RMSE; MAE is also reported per fold.

`servable: true` marks candidates the runtime can actually serve today —
multiplier table and coefficient-exported linear models. Tree ensembles would
require shipping scikit-learn inside the serving image, so they are compared
for evidence but not selectable for production.

Requires the optional training dependencies:

    python -m pip install -r ml-service/training/requirements-training.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, pstdev

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.data_contract import PREDICTION_MAX_MINUTES, PREDICTION_MIN_MINUTES, encode_features, normalize_category
from eval_metrics import (
    INSUFFICIENT_EVIDENCE_MESSAGE,
    MIN_ROWS_FOR_COMPARISON_EVIDENCE,
    error_summary,
    improvement_ratio,
)
from train_duration_model import (
    DEFAULT_INPUT_PATH,
    DIFFICULTY_WEIGHT,
    FOCUS_MULTIPLIER,
    PRIORITY_WEIGHT,
    build_category_multipliers,
    clamp,
    load_training_rows,
    predict_row,
)

DEFAULT_SEED = 42
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "artifacts" / "model_comparison.json"

# Candidates the serving path can load without scikit-learn at runtime.
SERVABLE_CANDIDATES = {"naive-estimate", "dummy-mean", "multiplier-table (production)", "ridge-regression", "elastic-net"}


def fit_multiplier_table(train_rows: list[dict]) -> dict:
    return {
        "global_multiplier": round(
            mean(row["actual_minutes"] / row["estimated_minutes"] for row in train_rows), 4
        ),
        "category_multipliers": build_category_multipliers(train_rows),
        "difficulty_weight": DIFFICULTY_WEIGHT,
        "priority_weight": PRIORITY_WEIGHT,
        "focus_multiplier": FOCUS_MULTIPLIER,
    }


def build_candidates(seed: int) -> dict:
    from sklearn.dummy import DummyRegressor
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import ElasticNet, Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    def naive_estimate(train_rows, test_rows):
        return [float(row["estimated_minutes"]) for row in test_rows]

    def multiplier_table(train_rows, test_rows):
        model = fit_multiplier_table(train_rows)
        return [float(predict_row(row, model)) for row in test_rows]

    def sklearn_candidate(estimator_factory):
        def predict(train_rows, test_rows):
            categories = sorted({normalize_category(row["category"]) for row in train_rows})
            estimator = estimator_factory()
            estimator.fit(
                encode_features(train_rows, categories),
                [float(row["actual_minutes"]) for row in train_rows],
            )
            predictions = estimator.predict(encode_features(test_rows, categories))
            return [clamp(float(value), PREDICTION_MIN_MINUTES, PREDICTION_MAX_MINUTES) for value in predictions]

        return predict

    return {
        "naive-estimate": naive_estimate,
        "dummy-mean": sklearn_candidate(lambda: DummyRegressor(strategy="mean")),
        "multiplier-table (production)": multiplier_table,
        "ridge-regression": sklearn_candidate(lambda: make_pipeline(StandardScaler(), Ridge(alpha=1.0))),
        "elastic-net": sklearn_candidate(
            lambda: make_pipeline(StandardScaler(), ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=5000))
        ),
        "gradient-boosting": sklearn_candidate(
            lambda: GradientBoostingRegressor(n_estimators=100, max_depth=2, random_state=seed)
        ),
    }


def compare_models(input_path: Path = DEFAULT_INPUT_PATH, seed: int = DEFAULT_SEED, folds: int = 5) -> dict:
    from sklearn.model_selection import KFold

    rows = load_training_rows(input_path)
    fold_count = min(folds, len(rows))
    splitter = KFold(n_splits=fold_count, shuffle=True, random_state=seed)
    candidates = build_candidates(seed)
    fold_maes: dict[str, list[float]] = {name: [] for name in candidates}
    pooled_predictions: dict[str, list[float]] = {name: [] for name in candidates}
    pooled_actuals: list[float] = []

    for train_index, test_index in splitter.split(rows):
        train_rows = [rows[i] for i in train_index]
        test_rows = [rows[i] for i in test_index]
        pooled_actuals.extend(float(row["actual_minutes"]) for row in test_rows)
        for name, predict in candidates.items():
            predictions = predict(train_rows, test_rows)
            pooled_predictions[name].extend(predictions)
            fold_maes[name].append(
                mean(abs(p - row["actual_minutes"]) for p, row in zip(predictions, test_rows))
            )

    naive_mae = error_summary(pooled_predictions["naive-estimate"], pooled_actuals)["mae"]
    results = {}
    for name in candidates:
        summary = error_summary(pooled_predictions[name], pooled_actuals)
        results[name] = {
            "mae_mean": round(mean(fold_maes[name]), 2),
            "mae_std": round(pstdev(fold_maes[name]), 2),
            "pooled_mae": summary["mae"],
            "median_ae": summary["median_ae"],
            "rmse": summary["rmse"],
            "fold_mae": [round(value, 2) for value in fold_maes[name]],
            "improvement_vs_naive": improvement_ratio(summary["mae"], naive_mae),
            "servable": name in SERVABLE_CANDIDATES,
        }

    sufficient = len(rows) >= MIN_ROWS_FOR_COMPARISON_EVIDENCE
    return {
        "dataset": str(input_path.name),
        "rows": len(rows),
        "folds": fold_count,
        "seed": seed,
        "metric": "absolute error (minutes), lower is better; pooled across folds",
        "sufficient_evidence": sufficient,
        "evidence_note": (
            f"comparison over {len(rows)} rows is directional only "
            f"(needs >= {MIN_ROWS_FOR_COMPARISON_EVIDENCE}); {INSUFFICIENT_EVIDENCE_MESSAGE}"
            if not sufficient
            else f"comparison over {len(rows)} rows meets the minimum sample threshold"
        ),
        "results": results,
        "recommended_candidate": select_candidate(results),
    }


def select_candidate(results: dict[str, dict]) -> dict:
    """Best servable candidate by pooled MAE, with the reasoning recorded.

    Tree ensembles are excluded even if they score well: at this data size
    their variance is high and serving them would force scikit-learn into the
    runtime image. Ranking uses pooled MAE with Median AE as tie context.
    """
    servable = {name: stats for name, stats in results.items() if stats["servable"]}
    best_name = min(servable, key=lambda name: servable[name]["pooled_mae"])
    return {
        "name": best_name,
        "pooled_mae": servable[best_name]["pooled_mae"],
        "reason": (
            "lowest pooled out-of-sample MAE among candidates the runtime can serve "
            "without adding scikit-learn to the serving image"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-validated comparison of duration-model candidates.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    comparison = compare_models(input_path=args.input, seed=args.seed, folds=args.folds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    width = max(len(name) for name in comparison["results"])
    print(f"{comparison['rows']} rows, {comparison['folds']}-fold CV, seed {comparison['seed']}")
    for name, stats in sorted(comparison["results"].items(), key=lambda item: item[1]["pooled_mae"]):
        marker = "*" if name == comparison["recommended_candidate"]["name"] else " "
        print(
            f" {marker}{name.ljust(width)}  MAE {stats['pooled_mae']:6.2f}  "
            f"MedAE {stats['median_ae']:6.2f}  RMSE {stats['rmse']:6.2f}  "
            f"vs naive {stats['improvement_vs_naive']:+.2%}"
        )
    print(f"evidence: {comparison['evidence_note']}")
    print(f"written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
