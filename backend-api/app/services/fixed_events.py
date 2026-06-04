from datetime import date

from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.fixed_events import FixedEventCreate, FixedEventRead, FixedEventUpdate


def list_fixed_events(user_id: int, target_date: date | None = None) -> list[FixedEventRead]:
    store = get_store()
    fixed_events = store.list_fixed_events(user_id=user_id, target_date=target_date)
    return [FixedEventRead.model_validate(fixed_event) for fixed_event in fixed_events]


def create_fixed_event(user_id: int, payload: FixedEventCreate) -> FixedEventRead:
    store = get_store()
    fixed_event_payload = payload.model_dump()
    fixed_event_payload["user_id"] = user_id
    fixed_event = store.create_fixed_event(fixed_event_payload)
    return FixedEventRead.model_validate(fixed_event)


def update_fixed_event(user_id: int, fixed_event_id: int, payload: FixedEventUpdate) -> FixedEventRead:
    store = get_store()
    current_fixed_event = store.get_fixed_event(fixed_event_id)
    if current_fixed_event is None or current_fixed_event["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed event not found")

    update_payload = payload.model_dump(exclude_unset=True)
    next_start_time = update_payload.get("start_time", current_fixed_event["start_time"])
    next_end_time = update_payload.get("end_time", current_fixed_event["end_time"])
    if next_end_time <= next_start_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_time must be later than start_time",
        )

    updated_fixed_event = store.update_fixed_event(fixed_event_id, update_payload)
    if updated_fixed_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed event not found")

    return FixedEventRead.model_validate(updated_fixed_event)


def delete_fixed_event(user_id: int, fixed_event_id: int) -> None:
    store = get_store()
    current_fixed_event = store.get_fixed_event(fixed_event_id)
    if current_fixed_event is None or current_fixed_event["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed event not found")
    if not store.soft_delete_fixed_event(fixed_event_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fixed event not found")
