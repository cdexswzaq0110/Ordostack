from datetime import date

from fastapi import APIRouter, Query

from app.schemas.schedules import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleDiffResponse,
    ScheduleHistoryDeleteResponse,
    ScheduleHistoryItem,
    ScheduleHistoryUpdate,
)
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


@router.patch("/history/{schedule_run_id}", response_model=ScheduleHistoryItem)
def update_schedule_history_title(
    schedule_run_id: int,
    payload: ScheduleHistoryUpdate,
    user_id: int = 1,
) -> ScheduleHistoryItem:
    return schedule_service.update_schedule_history_title(
        user_id=user_id,
        schedule_run_id=schedule_run_id,
        payload=payload,
    )


@router.delete("/history/{schedule_run_id}", response_model=ScheduleHistoryDeleteResponse)
def delete_schedule_history_item(schedule_run_id: int, user_id: int = 1) -> ScheduleHistoryDeleteResponse:
    return schedule_service.delete_schedule_history_item(user_id=user_id, schedule_run_id=schedule_run_id)


@router.get("/history/{schedule_run_id}/diff", response_model=ScheduleDiffResponse)
def get_schedule_history_diff(
    schedule_run_id: int,
    against_run_id: int,
    user_id: int = 1,
) -> ScheduleDiffResponse:
    return schedule_service.get_schedule_history_diff(
        user_id=user_id,
        compare_run_id=schedule_run_id,
        base_run_id=against_run_id,
    )
