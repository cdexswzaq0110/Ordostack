from datetime import date

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from app.services import tasks as task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status: str | None = None,
    category: str | None = None,
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> list[TaskRead]:
    return task_service.list_tasks(
        user_id=current_user.id,
        task_status=status,
        category=category,
        target_date=target_date,
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, current_user: UserRead = Depends(get_current_user)) -> TaskRead:
    return task_service.create_task(user_id=current_user.id, payload=payload)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> TaskRead:
    return task_service.update_task(user_id=current_user.id, task_id=task_id, payload=payload)


@router.post("/{task_id}/reopen", response_model=TaskRead)
def reopen_task(task_id: int, current_user: UserRead = Depends(get_current_user)) -> TaskRead:
    return task_service.reopen_task(user_id=current_user.id, task_id=task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: UserRead = Depends(get_current_user)) -> Response:
    task_service.delete_task(user_id=current_user.id, task_id=task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
