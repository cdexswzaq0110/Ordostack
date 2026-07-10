"""Compare candidate duration models with cross-validation.

Answers "why the multiplier table and not something bigger?" with numbers
instead of opinions. Each candidate is fit per fold and scored on held-out
rows, so the table shows out-of-sample MAE at the current data size.

Requires the optional training dependencies:

    python -m pip install -r ml-service/training/requirements-training.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, pstdev

sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def encode_features(rows: list[dict], categories: list[str]) -> list[list[float]]:
    return [
        [
            float(row["estimated_minutes"]),
            float(row["priority"]),
            float(row["difficulty"]),
            1.0 if row["requires_focus"] else 0.0,
            *[1.0 if row["category"] == category else 0.0 for category in categories],
        ]
        for row in rows
    ]


def build_candidates(seed: int) -> dict:
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import Ridge

    def naive_estimate(train_rows, test_rows):
        return [float(row["estimated_minutes"]) for row in test_rows]

    def multiplier_table(train_rows, test_rows):
        model = fit_multiplier_table(train_rows)
        return [float(predict_row(row, model)) for row in test_rows]

    def sklearn_candidate(estimator_factory):
        def predict(train_rows, test_rows):
            categories = sorted({row["category"] for row in train_rows})
            estimator = estimator_factory()
            estimator.fit(
                encode_features(train_rows, categories),
                [float(row["actual_minutes"]) for row in train_rows],
            )
            predictions = estimator.predict(encode_features(test_rows, categories))
            return [clamp(float(value), 1, 480) for value in predictions]

        return predict

    return {
        "naive-estimate": naive_estimate,
        "multiplier-table (production)": multiplier_table,
        "ridge-regression": sklearn_candidate(lambda: Ridge(alpha=1.0)),
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
    fold_errors: dict[str, list[float]] = {name: [] for name in candidates}

    for train_index, test_index in splitter.split(rows):
        train_rows = [rows[i] for i in train_index]
        test_rows = [rows[i] for i in test_index]
        for name, predict in candidates.items():
            predictions = predict(train_rows, test_rows)
            errors = [
                abs(prediction - row["actual_minutes"])
                for prediction, row in zip(predictions, test_rows)
            ]
            fold_errors[name].append(mean(errors))

    results = {
        name: {
            "mae_mean": round(mean(errors), 2),
            "mae_std": round(pstdev(errors), 2),
        }
        for name, errors in fold_errors.items()
    }
    return {
        "dataset": str(input_path.name),
        "rows": len(rows),
        "folds": fold_count,
        "seed": seed,
        "metric": "mean absolute error (minutes), lower is better",
        "results": results,
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
    for name, stats in sorted(comparison["results"].items(), key=lambda item: item[1]["mae_mean"]):
        print(f"  {name.ljust(width)}  MAE {stats['mae_mean']:6.2f} +/- {stats['mae_std']:.2f}")
    print(f"written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
