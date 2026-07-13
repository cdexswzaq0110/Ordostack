from fastapi import HTTPException, status

from app.repositories.store import get_store
from app.schemas.schedule_templates import (
    ScheduleTemplateCreate,
    ScheduleTemplateDeleteResponse,
    ScheduleTemplateRead,
    ScheduleTemplateUpdate,
)


def list_schedule_templates(user_id: int) -> list[ScheduleTemplateRead]:
    templates = get_store().list_schedule_templates(user_id=user_id)
    return [ScheduleTemplateRead.model_validate(template) for template in templates]


def create_schedule_template(user_id: int, payload: ScheduleTemplateCreate) -> ScheduleTemplateRead:
    template_payload = payload.model_dump()
    template_payload["user_id"] = user_id
    template = get_store().create_schedule_template(template_payload)
    return ScheduleTemplateRead.model_validate(template)


def update_schedule_template(
    user_id: int,
    template_id: int,
    payload: ScheduleTemplateUpdate,
) -> ScheduleTemplateRead:
    current_template = get_store().get_schedule_template(user_id=user_id, template_id=template_id)
    if current_template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")

    update_payload = payload.model_dump(exclude_unset=True)
    next_start_hour = update_payload.get("start_hour", current_template["start_hour"])
    next_end_hour = update_payload.get("end_hour", current_template["end_hour"])
    if next_end_hour <= next_start_hour:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_hour must be later than start_hour",
        )

    updated_template = get_store().update_schedule_template(
        user_id=user_id,
        template_id=template_id,
        payload=update_payload,
    )
    if updated_template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")
    return ScheduleTemplateRead.model_validate(updated_template)


def delete_schedule_template(user_id: int, template_id: int) -> ScheduleTemplateDeleteResponse:
    deleted = get_store().soft_delete_schedule_template(user_id=user_id, template_id=template_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule template not found")
    return ScheduleTemplateDeleteResponse(deleted=True)
