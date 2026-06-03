from datetime import datetime

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


class FixedEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    start_time: datetime | None = None
    end_time: datetime | None = None
    event_type: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_time_range(self) -> "FixedEventUpdate":
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class FixedEventRead(FixedEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
