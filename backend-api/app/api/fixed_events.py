from datetime import date

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.fixed_events import FixedEventCreate, FixedEventRead, FixedEventUpdate
from app.services import fixed_events as fixed_event_service

router = APIRouter(prefix="/api/fixed-events", tags=["fixed-events"])


@router.get("", response_model=list[FixedEventRead])
def list_fixed_events(
    target_date: date | None = None,
    current_user: UserRead = Depends(get_current_user),
) -> list[FixedEventRead]:
    return fixed_event_service.list_fixed_events(user_id=current_user.id, target_date=target_date)


@router.post("", response_model=FixedEventRead, status_code=status.HTTP_201_CREATED)
def create_fixed_event(
    payload: FixedEventCreate,
    current_user: UserRead = Depends(get_current_user),
) -> FixedEventRead:
    return fixed_event_service.create_fixed_event(user_id=current_user.id, payload=payload)


@router.patch("/{fixed_event_id}", response_model=FixedEventRead)
def update_fixed_event(
    fixed_event_id: int,
    payload: FixedEventUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> FixedEventRead:
    return fixed_event_service.update_fixed_event(
        user_id=current_user.id,
        fixed_event_id=fixed_event_id,
        payload=payload,
    )


@router.delete("/{fixed_event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixed_event(fixed_event_id: int, current_user: UserRead = Depends(get_current_user)) -> Response:
    fixed_event_service.delete_fixed_event(user_id=current_user.id, fixed_event_id=fixed_event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
