from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_user
from app.schemas.auth import UserRead
from app.schemas.schedule_templates import (
    ScheduleTemplateCreate,
    ScheduleTemplateDeleteResponse,
    ScheduleTemplateRead,
    ScheduleTemplateUpdate,
)
from app.services import schedule_templates as template_service

router = APIRouter(prefix="/api/schedule-templates", tags=["schedule-templates"])


@router.get("", response_model=list[ScheduleTemplateRead])
def list_schedule_templates(current_user: UserRead = Depends(get_current_user)) -> list[ScheduleTemplateRead]:
    return template_service.list_schedule_templates(user_id=current_user.id)


@router.post("", response_model=ScheduleTemplateRead, status_code=status.HTTP_201_CREATED)
def create_schedule_template(
    payload: ScheduleTemplateCreate,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleTemplateRead:
    return template_service.create_schedule_template(user_id=current_user.id, payload=payload)


@router.patch("/{template_id}", response_model=ScheduleTemplateRead)
def update_schedule_template(
    template_id: int,
    payload: ScheduleTemplateUpdate,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleTemplateRead:
    return template_service.update_schedule_template(
        user_id=current_user.id,
        template_id=template_id,
        payload=payload,
    )


@router.delete("/{template_id}", response_model=ScheduleTemplateDeleteResponse)
def delete_schedule_template(
    template_id: int,
    current_user: UserRead = Depends(get_current_user),
) -> ScheduleTemplateDeleteResponse:
    return template_service.delete_schedule_template(user_id=current_user.id, template_id=template_id)
