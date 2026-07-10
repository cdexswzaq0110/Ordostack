from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.predictions import (
    DurationFeedbackExportResponse,
    DurationPredictionResponse,
    PredictionAccuracyResponse,
)
from app.services import predictions as prediction_service

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.get("/duration-predictions", response_model=DurationPredictionResponse)
def get_duration_predictions(
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> DurationPredictionResponse:
    if target_date is None:
        target_date = date.today()
    return prediction_service.get_duration_predictions(user_id=current_user.id, target_date=target_date)


@router.get("/duration-feedback", response_model=DurationFeedbackExportResponse)
def export_duration_feedback(
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> DurationFeedbackExportResponse:
    if target_date is None:
        target_date = date.today()
    return prediction_service.export_duration_feedback(user_id=current_user.id, target_date=target_date)


@router.get("/prediction-accuracy", response_model=PredictionAccuracyResponse)
def get_prediction_accuracy(
    days: int = 90,
    current_user: UserRead = Depends(get_current_user),
) -> PredictionAccuracyResponse:
    days = min(max(days, 1), 365)
    return prediction_service.get_prediction_accuracy(user_id=current_user.id, days=days)
