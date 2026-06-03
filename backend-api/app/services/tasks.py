from datetime import date

from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.tasks import TaskCreate, TaskRead, TaskUpdate


def list_tasks(
    user_id: int,
    task_status: str | None = None,
    category: str | None = None,
    target_date: date | None = None,
) -> list[TaskRead]:
    store = get_store()
    tasks = store.list_tasks(
        user_id=user_id,
        status=task_status,
        category=category,
        target_date=target_date,
    )
    return [TaskRead.model_validate(task) for task in tasks]


def create_task(payload: TaskCreate) -> TaskRead:
    store = get_store()
    task = store.create_task(payload.model_dump())
    return TaskRead.model_validate(task)


def update_task(task_id: int, payload: TaskUpdate) -> TaskRead:
    store = get_store()
    current_task = store.get_task(task_id)
    if current_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_payload = payload.model_dump(exclude_unset=True)
    if current_task["status"] == "completed" and update_payload.get("status") == "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Completed tasks must be reopened through the reopen endpoint",
        )

    updated_task = store.update_task(task_id, update_payload)
    if updated_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskRead.model_validate(updated_task)


def reopen_task(task_id: int) -> TaskRead:
    store = get_store()
    current_task = store.get_task(task_id)
    if current_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated_task = store.update_task(task_id, {"status": "pending"})
    if updated_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskRead.model_validate(updated_task)


def delete_task(task_id: int) -> None:
    store = get_store()
    if not store.soft_delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
