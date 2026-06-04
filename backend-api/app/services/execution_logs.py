from datetime import UTC, date, datetime

from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.execution_logs import ExecutionEventType, TaskExecutionEventRequest, TaskExecutionLogRead


def list_execution_logs(
    user_id: int,
    target_date: date | None = None,
    task_id: int | None = None,
) -> list[TaskExecutionLogRead]:
    store = get_store()
    logs = store.list_execution_logs(
        user_id=user_id,
        target_date=target_date,
        task_id=task_id,
    )
    return [TaskExecutionLogRead.model_validate(log) for log in logs]


def record_execution_event(
    user_id: int,
    task_id: int,
    event_type: ExecutionEventType,
    payload: TaskExecutionEventRequest,
) -> TaskExecutionLogRead:
    store = get_store()
    task = store.get_task(task_id)
    if task is None or task["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    validate_execution_transition(task, event_type)

    occurred_at = payload.occurred_at or datetime.now(UTC)
    execution_log = store.create_execution_log(
        {
            "user_id": user_id,
            "task_id": task_id,
            "event_type": event_type,
            "occurred_at": occurred_at,
        }
    )
    next_status = status_for_event(event_type)
    store.update_task(task_id, {"status": next_status})

    return TaskExecutionLogRead.model_validate(execution_log)


def validate_execution_transition(task: dict, event_type: ExecutionEventType) -> None:
    current_status = task["status"]

    if event_type == "start" and current_status == "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task is already in progress")

    if event_type == "start" and current_status in {"completed", "skipped"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task must be reopened before starting")

    if event_type == "pause" and current_status != "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only in-progress tasks can be paused")

    if event_type in {"complete", "skip"} and current_status in {"completed", "skipped"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Task is already closed")


def status_for_event(event_type: ExecutionEventType) -> str:
    if event_type == "start":
        return "in_progress"
    if event_type == "pause":
        return "pending"
    if event_type == "complete":
        return "completed"
    return "skipped"
