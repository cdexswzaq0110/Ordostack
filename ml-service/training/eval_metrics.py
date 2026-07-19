"""Shared error metrics for duration-model training and comparison.

All values are minutes. Kept stdlib-only so the metrics used in reports are
the same ones unit tests can verify without scikit-learn.
"""

from __future__ import annotations

from math import sqrt
from statistics import mean, median

# Below this many evaluation rows no metric difference is trustworthy enough
# to auto-promote a model; the pipeline must say so instead of pretending.
MIN_EVALUATION_ROWS_FOR_EVIDENCE = 10
INSUFFICIENT_EVIDENCE_MESSAGE = "insufficient evidence for automatic promotion"

# A candidate comparison needs more rows than a single promotion check before
# its ranking stops being noise; below this the table is directional only.
MIN_ROWS_FOR_COMPARISON_EVIDENCE = 30


def absolute_errors(predictions: list[float], actuals: list[float]) -> list[float]:
    if len(predictions) != len(actuals):
        raise ValueError(f"length mismatch: {len(predictions)} predictions vs {len(actuals)} actuals")
    return [abs(prediction - actual) for prediction, actual in zip(predictions, actuals)]


def error_summary(predictions: list[float], actuals: list[float]) -> dict[str, float | int]:
    """MAE / Median AE / RMSE plus the sample count they were computed on."""
    errors = absolute_errors(predictions, actuals)
    if not errors:
        return {"mae": 0.0, "median_ae": 0.0, "rmse": 0.0, "sample_count": 0}
    return {
        "mae": round(mean(errors), 2),
        "median_ae": round(median(errors), 2),
        "rmse": round(sqrt(mean(error * error for error in errors)), 2),
        "sample_count": len(errors),
    }


def improvement_ratio(model_mae: float, baseline_mae: float) -> float:
    """Positive = model beats baseline; 0.0 when the baseline is degenerate."""
    if baseline_mae <= 0:
        return 0.0
    return round(1 - (model_mae / baseline_mae), 4)


def has_sufficient_evidence(evaluation_rows: int) -> bool:
    return evaluation_rows >= MIN_EVALUATION_ROWS_FOR_EVIDENCE
