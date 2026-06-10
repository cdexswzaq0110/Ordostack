from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.analytics import CompletionForecastRead, DailyAnalyticsRead
from app.services import analytics as analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/daily", response_model=DailyAnalyticsRead)
def get_daily_analytics(
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> DailyAnalyticsRead:
    if target_date is None:
        target_date = date.today()
    return analytics_service.get_daily_analytics(user_id=current_user.id, target_date=target_date)


@router.get("/completion-forecast", response_model=CompletionForecastRead)
def get_completion_forecast(
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> CompletionForecastRead:
    if target_date is None:
        target_date = date.today()
    return analytics_service.get_completion_forecast(user_id=current_user.id, target_date=target_date)
