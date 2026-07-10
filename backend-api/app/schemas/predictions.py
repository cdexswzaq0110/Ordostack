from datetime import date
from typing import Any

from pydantic import BaseModel


class DurationPredictionRead(BaseModel):
    task_id: int
    predicted_minutes: int
    confidence: float
    model_name: str
    reason: str


class DurationPredictionResponse(BaseModel):
    user_id: int
    target_date: date
    model_name: str
    model_version: str
    predictions: list[DurationPredictionRead]


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
    daily: list[PredictionAccuracyDay]


DurationPredictionPayload = dict[str, Any]
