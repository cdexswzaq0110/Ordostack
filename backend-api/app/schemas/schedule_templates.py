from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleTemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    planning_mode: str = Field(default="balanced", min_length=1, max_length=50)
    start_hour: int = Field(default=9, ge=0, le=23)
    end_hour: int = Field(default=23, ge=1, le=24)
    buffer_minutes: int = Field(default=10, ge=0, le=60)
    include_fixed_events: bool = True

    @model_validator(mode="after")
    def validate_planning_window(self) -> "ScheduleTemplateBase":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be later than start_hour")
        return self


class ScheduleTemplateCreate(ScheduleTemplateBase):
    user_id: int = 1


class ScheduleTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    planning_mode: str | None = Field(default=None, min_length=1, max_length=50)
    start_hour: int | None = Field(default=None, ge=0, le=23)
    end_hour: int | None = Field(default=None, ge=1, le=24)
    buffer_minutes: int | None = Field(default=None, ge=0, le=60)
    include_fixed_events: bool | None = None

    @model_validator(mode="after")
    def validate_planning_window(self) -> "ScheduleTemplateUpdate":
        if self.start_hour is not None and self.end_hour is not None and self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be later than start_hour")
        return self


class ScheduleTemplateRead(ScheduleTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class ScheduleTemplateDeleteResponse(BaseModel):
    deleted: bool
