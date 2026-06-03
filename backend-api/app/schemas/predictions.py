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


DurationPredictionPayload = dict[str, Any]
