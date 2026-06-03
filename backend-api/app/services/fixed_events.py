from datetime import date

from app.repositories.store import get_store
from app.schemas.fixed_events import FixedEventCreate, FixedEventRead


def list_fixed_events(user_id: int, target_date: date | None = None) -> list[FixedEventRead]:
    store = get_store()
    fixed_events = store.list_fixed_events(user_id=user_id, target_date=target_date)
    return [FixedEventRead.model_validate(fixed_event) for fixed_event in fixed_events]


def create_fixed_event(payload: FixedEventCreate) -> FixedEventRead:
    store = get_store()
    fixed_event = store.create_fixed_event(payload.model_dump())
    return FixedEventRead.model_validate(fixed_event)
