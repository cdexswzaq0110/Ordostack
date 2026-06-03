from datetime import date

from fastapi import APIRouter

from app.schemas.predictions import DurationPredictionResponse
from app.services import predictions as prediction_service

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.get("/duration-predictions", response_model=DurationPredictionResponse)
def get_duration_predictions(user_id: int = 1, target_date: date | None = None) -> DurationPredictionResponse:
    if target_date is None:
        target_date = date.today()
    return prediction_service.get_duration_predictions(user_id=user_id, target_date=target_date)
