from datetime import date

from fastapi import APIRouter

from app.schemas.schedules import ScheduleGenerateRequest, ScheduleGenerateResponse
from app.services import schedules as schedule_service

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.post("/generate")
def generate_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    return schedule_service.generate_schedule(payload)


@router.get("/latest")
def get_latest_schedule(target_date: date, user_id: int = 1) -> ScheduleGenerateResponse:
    return schedule_service.get_latest_schedule(user_id=user_id, target_date=target_date)
