from datetime import date, datetime, timedelta

from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.fixed_events import FixedEventCreate, FixedEventRead, FixedEventUpdate, RecurringFixedEventCreate


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


def create_recurring_fixed_events(user_id: int, payload: RecurringFixedEventCreate) -> list[FixedEventRead]:
    store = get_store()
    recurrence_id = payload.build_recurrence_id()
    recurrence_rule = payload.build_recurrence_rule()
    start_clock = payload.start_time.time()
    end_clock = payload.end_time.time()
    duration_days = (payload.end_time.date() - payload.start_time.date()).days

    created_events: list[FixedEventRead] = []
    current_date = payload.start_time.date()
    recurrence_days = set(payload.recurrence_days)
    while current_date <= payload.recurrence_until:
        if current_date.weekday() in recurrence_days:
            event_start = datetime.combine(current_date, start_clock)
            event_end = datetime.combine(current_date + timedelta(days=duration_days), end_clock)
            fixed_event = store.create_fixed_event(
                {
                    "user_id": user_id,
                    "title": payload.title,
                    "start_time": event_start,
                    "end_time": event_end,
                    "event_type": payload.event_type,
                    "recurrence_id": recurrence_id,
                    "recurrence_rule": recurrence_rule,
                }
            )
            created_events.append(FixedEventRead.model_validate(fixed_event))
        current_date += timedelta(days=1)

    if not created_events:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="recurrence rule does not produce any events",
        )

    return created_events


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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
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
