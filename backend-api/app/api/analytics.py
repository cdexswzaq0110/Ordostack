from datetime import date

from fastapi import APIRouter

from app.schemas.analytics import DailyAnalyticsRead
from app.services import analytics as analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/daily", response_model=DailyAnalyticsRead)
def get_daily_analytics(user_id: int = 1, target_date: date | None = None) -> DailyAnalyticsRead:
    if target_date is None:
        target_date = date.today()
    return analytics_service.get_daily_analytics(user_id=user_id, target_date=target_date)
