from datetime import date, datetime
from typing import Literal
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ScheduleGenerateRequest(BaseModel):
    user_id: int = 1
    target_date: date
    planning_mode: str = Field(default="balanced", min_length=1, max_length=50)
    start_hour: int = Field(default=9, ge=0, le=23)
    end_hour: int = Field(default=23, ge=1, le=24)
    buffer_minutes: int = Field(default=10, ge=0, le=60)
    include_fixed_events: bool = True


ScheduleGenerateResponse = dict[str, Any]


class ScheduleHistoryItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    planning_mode: str
    scheduled_task_count: int
    item_count: int
    schedule: ScheduleGenerateResponse


class ScheduleHistoryUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ScheduleItemLockUpdate(BaseModel):
    locked: bool


class ScheduleItemTimeUpdate(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_time_range(self) -> "ScheduleItemTimeUpdate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class ScheduleHistoryDeleteResponse(BaseModel):
    deleted: bool


class ScheduleDiffItem(BaseModel):
    item_key: str
    change_type: Literal["added", "removed", "changed"]
    title: str
    previous_start_time: str | None
    next_start_time: str | None
    previous_planned_minutes: int | None
    next_planned_minutes: int | None


class ScheduleDiffResponse(BaseModel):
    base_run_id: int
    compare_run_id: int
    added_count: int
    removed_count: int
    changed_count: int
    unchanged_count: int
    total_delta_minutes: int
    changes: list[ScheduleDiffItem]


class ScheduleExportResponse(BaseModel):
    filename: str
    format: Literal["markdown", "csv", "pdf"]
    content_type: str
    content: str
    encoding: Literal["utf-8", "base64"] = "utf-8"
