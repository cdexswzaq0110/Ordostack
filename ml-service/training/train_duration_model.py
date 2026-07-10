import argparse
import csv
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clearml_utils import track_training_run

MODEL_NAME = "local-duration-regressor"
MODEL_VERSION = "0.2.0"
DIFFICULTY_WEIGHT = 0.04
PRIORITY_WEIGHT = 0.015
FOCUS_MULTIPLIER = 1.05
DEFAULT_SEED = 42
HOLDOUT_RATIO = 0.2
MIN_ROWS_FOR_HOLDOUT = 10

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "training" / "data" / "duration_training_samples.csv"
DEFAULT_FEEDBACK_PATH = PROJECT_ROOT / "training" / "data" / "duration_feedback.csv"
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "training" / "artifacts"


def train_duration_model(
    input_path: Path = DEFAULT_INPUT_PATH,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    feedback_path: Path | None = None,
    seed: int = DEFAULT_SEED,
) -> dict:
    rows = load_training_rows(input_path)
    feedback_rows: list[dict] = []
    if feedback_path is not None and feedback_path.exists():
        # An exported feedback file with zero data rows means "no feedback yet".
        feedback_rows = load_training_rows(feedback_path, allow_empty=True)

    train_rows, evaluation_rows, evaluation_mode = split_rows(rows + feedback_rows, seed)
    category_multipliers = build_category_multipliers(train_rows)
    global_multiplier = round(mean(row["actual_minutes"] / row["estimated_minutes"] for row in train_rows), 4)

    model = {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "source": "local-artifact",
        "trained_at": datetime.now(UTC).isoformat(),
        "seed": seed,
        "training_rows": len(train_rows),
        "feedback_rows": len(feedback_rows),
        "global_multiplier": global_multiplier,
        "category_multipliers": category_multipliers,
        "difficulty_weight": DIFFICULTY_WEIGHT,
        "priority_weight": PRIORITY_WEIGHT,
        "focus_multiplier": FOCUS_MULTIPLIER,
    }
    metrics = evaluate_model(evaluation_rows, model, evaluation_mode, seed)

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


def split_rows(rows: list[dict], seed: int) -> tuple[list[dict], list[dict], str]:
    """Deterministic holdout split so reported MAE is out-of-sample, not training error."""
    if len(rows) < MIN_ROWS_FOR_HOLDOUT:
        return rows, rows, "in-sample"

    shuffled = list(rows)
    random.Random(seed).shuffle(shuffled)
    holdout_count = max(1, round(len(shuffled) * HOLDOUT_RATIO))
    return shuffled[holdout_count:], shuffled[:holdout_count], "holdout"


def load_training_rows(input_path: Path, allow_empty: bool = False) -> list[dict]:
    with input_path.open("r", encoding="utf-8", newline="") as training_file:
        reader = csv.DictReader(training_file)
        rows = [
            {
                "category": row["category"],
                "estimated_minutes": int(row["estimated_minutes"]),
                "priority": int(row["priority"]),
                "difficulty": int(row["difficulty"]),
                "requires_focus": row["requires_focus"].strip().lower() == "true",
                "actual_minutes": int(row["actual_minutes"]),
            }
            for row in reader
            if int(row["estimated_minutes"]) > 0 and int(row["actual_minutes"]) > 0
        ]

    if not rows and not allow_empty:
        raise ValueError("training dataset is empty")
    return rows


def build_category_multipliers(rows: list[dict]) -> dict[str, float]:
    ratios_by_category: dict[str, list[float]] = {}
    for row in rows:
        ratios_by_category.setdefault(row["category"], []).append(
            row["actual_minutes"] / row["estimated_minutes"]
        )

    return {
        category: round(clamp(mean(ratios), 0.75, 1.45), 4)
        for category, ratios in sorted(ratios_by_category.items())
    }


def evaluate_model(rows: list[dict], model: dict, evaluation_mode: str, seed: int) -> dict:
    baseline_errors = []
    model_errors = []
    for row in rows:
        baseline_errors.append(abs(row["estimated_minutes"] - row["actual_minutes"]))
        model_errors.append(abs(predict_row(row, model) - row["actual_minutes"]))

    baseline_mae = round(mean(baseline_errors), 2)
    model_mae = round(mean(model_errors), 2)
    return {
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "seed": seed,
        "evaluation_mode": evaluation_mode,
        "training_rows": model["training_rows"],
        "feedback_rows": model["feedback_rows"],
        "evaluation_rows": len(rows),
        "baseline_mae": baseline_mae,
        "model_mae": model_mae,
        "improvement_ratio": round(1 - (model_mae / baseline_mae), 4) if baseline_mae > 0 else 0.0,
    }


def predict_row(row: dict, model: dict) -> int:
    category_multiplier = model["category_multipliers"].get(
        row["category"],
        model["global_multiplier"],
    )
    prediction = row["estimated_minutes"] * category_multiplier
    prediction *= 1 + ((row["difficulty"] - 3) * model["difficulty_weight"])
    prediction *= 1 + max(0, row["priority"] - 3) * model["priority_weight"]
    if row["requires_focus"]:
        prediction *= model["focus_multiplier"]

    return round(clamp(prediction, 1, 480))


def clamp(value: float, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the local duration model with holdout evaluation.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument(
        "--feedback",
        type=Path,
        default=DEFAULT_FEEDBACK_PATH,
        help="Optional execution-feedback CSV merged into training data when the file exists.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    result = train_duration_model(
        input_path=args.input,
        artifact_dir=args.artifact_dir,
        feedback_path=args.feedback,
        seed=args.seed,
    )
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
