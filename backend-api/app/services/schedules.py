import os
from datetime import date
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.schedules import (
    ScheduleGenerateRequest,
    ScheduleGenerateResponse,
    ScheduleDiffItem,
    ScheduleDiffResponse,
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


def get_schedule_history_diff(user_id: int, compare_run_id: int, base_run_id: int) -> ScheduleDiffResponse:
    base_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=base_run_id)
    compare_run = get_store().get_generated_schedule_history_item(user_id=user_id, schedule_run_id=compare_run_id)

    if base_run is None or compare_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated schedule not found")

    return build_schedule_diff(base_run=base_run, compare_run=compare_run)


def build_schedule_diff(base_run: dict[str, Any], compare_run: dict[str, Any]) -> ScheduleDiffResponse:
    base_items = {schedule_item_key(item): item for item in base_run["schedule"].get("items", [])}
    compare_items = {schedule_item_key(item): item for item in compare_run["schedule"].get("items", [])}
    item_keys = sorted(base_items.keys() | compare_items.keys())
    changes: list[ScheduleDiffItem] = []
    unchanged_count = 0

    for item_key in item_keys:
        base_item = base_items.get(item_key)
        compare_item = compare_items.get(item_key)

        if base_item is None and compare_item is not None:
            changes.append(build_diff_item(item_key=item_key, change_type="added", base_item=None, compare_item=compare_item))
            continue

        if base_item is not None and compare_item is None:
            changes.append(build_diff_item(item_key=item_key, change_type="removed", base_item=base_item, compare_item=None))
            continue

        if base_item is None or compare_item is None:
            continue

        if schedule_item_changed(base_item, compare_item):
            changes.append(
                build_diff_item(item_key=item_key, change_type="changed", base_item=base_item, compare_item=compare_item),
            )
        else:
            unchanged_count += 1

    total_delta_minutes = schedule_minutes(compare_items.values()) - schedule_minutes(base_items.values())
    return ScheduleDiffResponse(
        base_run_id=base_run["id"],
        compare_run_id=compare_run["id"],
        added_count=sum(1 for change in changes if change.change_type == "added"),
        removed_count=sum(1 for change in changes if change.change_type == "removed"),
        changed_count=sum(1 for change in changes if change.change_type == "changed"),
        unchanged_count=unchanged_count,
        total_delta_minutes=total_delta_minutes,
        changes=changes,
    )


def schedule_item_key(item: dict[str, Any]) -> str:
    if item.get("type") == "task" and item.get("task_id") is not None:
        return f"task:{item['task_id']}"
    if item.get("type") == "fixed_event" and item.get("fixed_event_id") is not None:
        return f"fixed_event:{item['fixed_event_id']}"
    return f"{item.get('type', 'item')}:{item.get('title', '')}:{item.get('order_index', 0)}"


def schedule_item_changed(base_item: dict[str, Any], compare_item: dict[str, Any]) -> bool:
    fields = ("title", "start_time", "end_time", "planned_minutes", "order_index")
    return any(base_item.get(field) != compare_item.get(field) for field in fields)


def build_diff_item(
    item_key: str,
    change_type: str,
    base_item: dict[str, Any] | None,
    compare_item: dict[str, Any] | None,
) -> ScheduleDiffItem:
    item = compare_item or base_item or {}
    return ScheduleDiffItem(
        item_key=item_key,
        change_type=change_type,
        title=str(item.get("title", "Untitled")),
        previous_start_time=base_item.get("start_time") if base_item else None,
        next_start_time=compare_item.get("start_time") if compare_item else None,
        previous_planned_minutes=base_item.get("planned_minutes") if base_item else None,
        next_planned_minutes=compare_item.get("planned_minutes") if compare_item else None,
    )


def schedule_minutes(items: Any) -> int:
    return sum(int(item.get("planned_minutes", 0)) for item in items if item.get("type") == "task")


def extract_scheduler_error(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        return response.text

    return payload.get("detail", payload)
