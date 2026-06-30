from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.execution_logs import TaskExecutionEventRequest, TaskExecutionLogRead
from app.services import execution_logs as execution_log_service

router = APIRouter(prefix="/api", tags=["execution-logs"])


@router.get("/task-execution-logs", response_model=list[TaskExecutionLogRead])
def list_execution_logs(
    target_date: date | None = None,
    task_id: int | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> list[TaskExecutionLogRead]:
    return execution_log_service.list_execution_logs(
        user_id=current_user.id,
        target_date=target_date,
        task_id=task_id,
    )


@router.post("/tasks/{task_id}/execution/start", response_model=TaskExecutionLogRead)
def start_task(
    task_id: int,
    payload: TaskExecutionEventRequest,
    current_user: UserRead = Depends(get_current_user),
) -> TaskExecutionLogRead:
    return execution_log_service.record_execution_event(current_user.id, task_id, "start", payload)


@router.post("/tasks/{task_id}/execution/pause", response_model=TaskExecutionLogRead)
def pause_task(
    task_id: int,
    payload: TaskExecutionEventRequest,
    current_user: UserRead = Depends(get_current_user),
) -> TaskExecutionLogRead:
    return execution_log_service.record_execution_event(current_user.id, task_id, "pause", payload)


@router.post("/tasks/{task_id}/execution/complete", response_model=TaskExecutionLogRead)
def complete_task(
    task_id: int,
    payload: TaskExecutionEventRequest,
    current_user: UserRead = Depends(get_current_user),
) -> TaskExecutionLogRead:
    return execution_log_service.record_execution_event(current_user.id, task_id, "complete", payload)


@router.post("/tasks/{task_id}/execution/skip", response_model=TaskExecutionLogRead)
def skip_task(
    task_id: int,
    payload: TaskExecutionEventRequest,
    current_user: UserRead = Depends(get_current_user),
) -> TaskExecutionLogRead:
    return execution_log_service.record_execution_event(current_user.id, task_id, "skip", payload)
