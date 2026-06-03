from datetime import date

from fastapi import APIRouter, status

from app.schemas.fixed_events import FixedEventCreate, FixedEventRead
from app.services import fixed_events as fixed_event_service

router = APIRouter(prefix="/api/fixed-events", tags=["fixed-events"])


@router.get("", response_model=list[FixedEventRead])
def list_fixed_events(user_id: int = 1, target_date: date | None = None) -> list[FixedEventRead]:
    return fixed_event_service.list_fixed_events(user_id=user_id, target_date=target_date)


@router.post("", response_model=FixedEventRead, status_code=status.HTTP_201_CREATED)
def create_fixed_event(payload: FixedEventCreate) -> FixedEventRead:
    return fixed_event_service.create_fixed_event(payload)

