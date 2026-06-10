from datetime import date, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FixedEventBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    event_type: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_time_range(self) -> "FixedEventBase":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class FixedEventCreate(FixedEventBase):
    user_id: int = 1
    recurrence_id: str | None = Field(default=None, max_length=64)
    recurrence_rule: str | None = Field(default=None, max_length=255)


class RecurringFixedEventCreate(FixedEventBase):
    recurrence_type: Literal["weekly"] = "weekly"
    recurrence_days: list[int] = Field(min_length=1, max_length=7)
    recurrence_until: date

    @model_validator(mode="after")
    def validate_recurrence(self) -> "RecurringFixedEventCreate":
        if self.recurrence_until < self.start_time.date():
            raise ValueError("recurrence_until must be on or after start_time")
        if len(set(self.recurrence_days)) != len(self.recurrence_days):
            raise ValueError("recurrence_days must not contain duplicates")
        if any(day < 0 or day > 6 for day in self.recurrence_days):
            raise ValueError("recurrence_days must use weekday values from 0 to 6")
        return self

    def build_recurrence_id(self) -> str:
        return f"rec-{uuid4().hex[:16]}"

    def build_recurrence_rule(self) -> str:
        days = ",".join(str(day) for day in sorted(self.recurrence_days))
        return f"weekly:{days}:until:{self.recurrence_until.isoformat()}"


class FixedEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    start_time: datetime | None = None
    end_time: datetime | None = None
    event_type: str | None = Field(default=None, max_length=50)
    recurrence_id: str | None = Field(default=None, max_length=64)
    recurrence_rule: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_time_range(self) -> "FixedEventUpdate":
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class FixedEventRead(FixedEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recurrence_id: str | None = None
    recurrence_rule: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
