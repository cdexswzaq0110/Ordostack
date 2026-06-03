from datetime import date

from fastapi import APIRouter, Query

from app.schemas.schedules import ScheduleGenerateRequest, ScheduleGenerateResponse, ScheduleHistoryItem
from app.services import schedules as schedule_service

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.post("/generate")
def generate_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    return schedule_service.generate_schedule(payload)


@router.get("/latest")
def get_latest_schedule(target_date: date, user_id: int = 1) -> ScheduleGenerateResponse:
    return schedule_service.get_latest_schedule(user_id=user_id, target_date=target_date)


@router.get("/history", response_model=list[ScheduleHistoryItem])
def list_schedule_history(
    target_date: date,
    user_id: int = 1,
    limit: int = Query(default=5, ge=1, le=20),
) -> list[ScheduleHistoryItem]:
    return schedule_service.list_schedule_history(user_id=user_id, target_date=target_date, limit=limit)
