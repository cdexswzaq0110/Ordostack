from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.schedules import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleDiffResponse,
    ScheduleExportResponse,
    ScheduleHistoryDeleteResponse,
    ScheduleHistoryItem,
    ScheduleHistoryUpdate,
    ScheduleItemLockUpdate,
    ScheduleItemTimeUpdate,
)
from app.services import schedules as schedule_service

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.post("/generate")
def generate_schedule(
    payload: ScheduleGenerateRequest,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleGenerateResponse:
    scoped_payload = payload.model_copy(update={"user_id": current_user.id})
    return schedule_service.generate_schedule(scoped_payload)


@router.get("/latest")
def get_latest_schedule(
    target_date: date,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleGenerateResponse:
    return schedule_service.get_latest_schedule(user_id=current_user.id, target_date=target_date)


@router.get("/history", response_model=list[ScheduleHistoryItem])
def list_schedule_history(
    target_date: date,
    limit: int = Query(default=5, ge=1, le=20),
    current_user: UserRead = Depends(get_current_user),
) -> list[ScheduleHistoryItem]:
    return schedule_service.list_schedule_history(user_id=current_user.id, target_date=target_date, limit=limit)


@router.patch("/history/{schedule_run_id}", response_model=ScheduleHistoryItem)
def update_schedule_history_title(
    schedule_run_id: int,
    payload: ScheduleHistoryUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleHistoryItem:
    return schedule_service.update_schedule_history_title(
        user_id=current_user.id,
        schedule_run_id=schedule_run_id,
        payload=payload,
    )


@router.patch("/history/{schedule_run_id}/items/{item_key}/lock", response_model=ScheduleHistoryItem)
def update_schedule_item_lock(
    schedule_run_id: int,
    item_key: str,
    payload: ScheduleItemLockUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleHistoryItem:
    return schedule_service.update_schedule_item_lock(
        user_id=current_user.id,
        schedule_run_id=schedule_run_id,
        item_key=item_key,
        payload=payload,
    )


@router.patch("/history/{schedule_run_id}/items/{item_key}/time", response_model=ScheduleHistoryItem)
def update_schedule_item_time(
    schedule_run_id: int,
    item_key: str,
    payload: ScheduleItemTimeUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleHistoryItem:
    return schedule_service.update_schedule_item_time(
        user_id=current_user.id,
        schedule_run_id=schedule_run_id,
        item_key=item_key,
        payload=payload,
    )


@router.delete("/history/{schedule_run_id}", response_model=ScheduleHistoryDeleteResponse)
def delete_schedule_history_item(
    schedule_run_id: int,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleHistoryDeleteResponse:
    return schedule_service.delete_schedule_history_item(user_id=current_user.id, schedule_run_id=schedule_run_id)


@router.get("/history/{schedule_run_id}/diff", response_model=ScheduleDiffResponse)
def get_schedule_history_diff(
    schedule_run_id: int,
    against_run_id: int,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleDiffResponse:
    return schedule_service.get_schedule_history_diff(
        user_id=current_user.id,
        compare_run_id=schedule_run_id,
        base_run_id=against_run_id,
    )


@router.get("/history/{schedule_run_id}/export", response_model=ScheduleExportResponse)
def export_schedule_history_item(
    schedule_run_id: int,
    export_format: str = Query(default="markdown", alias="format", pattern="^(markdown|csv|pdf)$"),
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleExportResponse:
    return schedule_service.export_schedule_history_item(
        user_id=current_user.id,
        schedule_run_id=schedule_run_id,
        export_format=export_format,
    )
