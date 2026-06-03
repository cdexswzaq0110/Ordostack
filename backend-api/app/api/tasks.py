from datetime import date

from fastapi import APIRouter, Response, status

from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from app.services import tasks as task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    user_id: int = 1,
    status: str | None = None,
    category: str | None = None,
    target_date: date | None = None,
) -> list[TaskRead]:
    return task_service.list_tasks(
        user_id=user_id,
        task_status=status,
        category=category,
        target_date=target_date,
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskRead:
    return task_service.create_task(payload)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate) -> TaskRead:
    return task_service.update_task(task_id, payload)


@router.post("/{task_id}/reopen", response_model=TaskRead)
def reopen_task(task_id: int) -> TaskRead:
    return task_service.reopen_task(task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    task_service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

