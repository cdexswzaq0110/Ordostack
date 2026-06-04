import os
from datetime import date
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.schedules import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleHistoryDeleteResponse,
    ScheduleHistoryItem,
    ScheduleHistoryUpdate,
)
from app.services import fixed_events as fixed_event_service
from app.services import predictions as prediction_service
from app.services import tasks as task_service

DEFAULT_SCHEDULER_SERVICE_URL = "http://scheduler-service:8100"
SCHEDULER_TIMEOUT_SECONDS = 8.0


def generate_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    tasks = task_service.list_tasks(
        user_id=payload.user_id,
        target_date=payload.target_date,
    )
    fixed_events = fixed_event_service.list_fixed_events(
        user_id=payload.user_id,
        target_date=payload.target_date,
    )

    duration_predictions = prediction_service.predict_for_tasks(
        user_id=payload.user_id,
        target_date=payload.target_date,
        tasks=tasks,
    )
    predicted_minutes_by_task = {
        prediction.task_id: prediction.predicted_minutes
        for prediction in duration_predictions.predictions
    }

    scheduler_payload: dict[str, Any] = payload.model_dump(mode="json")
    scheduler_payload["tasks"] = [
        {
            **task.model_dump(mode="json"),
            "predicted_minutes": predicted_minutes_by_task.get(task.id),
        }
        for task in tasks
    ]
    scheduler_payload["fixed_events"] = [event.model_dump(mode="json") for event in fixed_events]

    scheduler_url = os.getenv("SCHEDULER_SERVICE_URL", DEFAULT_SCHEDULER_SERVICE_URL).rstrip("/")
    try:
        response = httpx.post(
            f"{scheduler_url}/schedule/generate",
            json=scheduler_payload,
            timeout=SCHEDULER_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=error.response.status_code,
            detail=extract_scheduler_error(error.response),
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="scheduler-service is unavailable",
        ) from error

    schedule_response = response.json()
    get_store().save_generated_schedule(
        user_id=payload.user_id,
        target_date=payload.target_date,
        request_payload=payload.model_dump(mode="json"),
        schedule=schedule_response,
    )
    return schedule_response


def get_latest_schedule(user_id: int, target_date: date) -> ScheduleGenerateResponse:
    schedule = get_store().get_latest_generated_schedule(user_id=user_id, target_date=target_date)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return schedule


def list_schedule_history(user_id: int, target_date: date, limit: int = 5) -> list[ScheduleHistoryItem]:
    schedules = get_store().list_generated_schedules(user_id=user_id, target_date=target_date, limit=limit)
    return [ScheduleHistoryItem.model_validate(schedule) for schedule in schedules]


def update_schedule_history_title(
    user_id: int,
    schedule_run_id: int,
    payload: ScheduleHistoryUpdate,
) -> ScheduleHistoryItem:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Title is required")

    schedule = get_store().update_generated_schedule_title(
        user_id=user_id,
        schedule_run_id=schedule_run_id,
        title=title,
    )
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return ScheduleHistoryItem.model_validate(schedule)


def delete_schedule_history_item(user_id: int, schedule_run_id: int) -> ScheduleHistoryDeleteResponse:
    deleted = get_store().soft_delete_generated_schedule(user_id=user_id, schedule_run_id=schedule_run_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")
    return ScheduleHistoryDeleteResponse(deleted=True)


def extract_scheduler_error(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        return response.text

    return payload.get("detail", payload)
