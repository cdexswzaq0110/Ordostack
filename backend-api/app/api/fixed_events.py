from datetime import date

from fastapi import APIRouter, Response, status

from app.schemas.fixed_events import FixedEventCreate, FixedEventRead, FixedEventUpdate
from app.services import fixed_events as fixed_event_service

router = APIRouter(prefix="/api/fixed-events", tags=["fixed-events"])


@router.get("", response_model=list[FixedEventRead])
def list_fixed_events(user_id: int = 1, target_date: date | None = None) -> list[FixedEventRead]:
    return fixed_event_service.list_fixed_events(user_id=user_id, target_date=target_date)


@router.post("", response_model=FixedEventRead, status_code=status.HTTP_201_CREATED)
def create_fixed_event(payload: FixedEventCreate) -> FixedEventRead:
    return fixed_event_service.create_fixed_event(payload)


@router.patch("/{fixed_event_id}", response_model=FixedEventRead)
def update_fixed_event(fixed_event_id: int, payload: FixedEventUpdate) -> FixedEventRead:
    return fixed_event_service.update_fixed_event(fixed_event_id, payload)


@router.delete("/{fixed_event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed_event(fixed_event_id: int) -> Response:
    fixed_event_service.delete_fixed_event(fixed_event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
