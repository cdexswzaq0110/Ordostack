from datetime import date
from typing import Any

from pydantic import BaseModel


class PredictionFactorRead(BaseModel):
    name: str
    impact_minutes: float


class DurationPredictionRead(BaseModel):
    task_id: int
    predicted_minutes: int
    confidence: float
    model_name: str
    reason: str
    raw_predicted_minutes: int | None = None
    model_version: str | None = None
    lower_bound: int | None = None
    upper_bound: int | None = None
    # "high" | "medium" | "low" | "insufficient-data" — historical error band
    # label from the ml-service, not a calibrated probability.
    reliability: str = "insufficient-data"
    sample_count: int | None = None
    fallback: bool = False
    out_of_distribution: bool = False
    factors: list[PredictionFactorRead] = []


class DurationPredictionResponse(BaseModel):
    user_id: int
    target_date: date
    model_name: str
    model_version: str
    predictions: list[DurationPredictionRead]
    calibration_factor: float | None = None
    calibration_samples: int = 0


class DurationFeedbackExportResponse(BaseModel):
    filename: str
    content_type: str
    row_count: int
    content: str


class PredictionAccuracyDay(BaseModel):
    target_date: date
    paired_count: int
    model_mae: float
    estimate_mae: float


class PredictionAccuracyResponse(BaseModel):
    user_id: int
    window_days: int
    logged_count: int
    paired_count: int
    model_mae: float | None
    estimate_mae: float | None
    improvement_ratio: float | None
    # False until enough paired samples exist for the model-vs-estimate
    # comparison to mean anything; the dashboard must not show a percentage
    # as a verdict below this threshold.
    sufficient_data: bool = False
    min_paired_required: int = 10
    daily: list[PredictionAccuracyDay]


DurationPredictionPayload = dict[str, Any]
