from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class TaskInput(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=50)
    estimated_minutes: int = Field(gt=0)
    predicted_minutes: int | None = Field(default=None, gt=0)
    priority: int = Field(ge=1, le=5)
    difficulty: int = Field(ge=1, le=5)
    deadline: datetime | None = None
    requires_focus: bool = False
    is_fixed: bool = False
    is_splittable: bool = False
    dependency_ids: list[int] = Field(default_factory=list)
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|skipped)$")


class FixedEventInput(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=255)
    start_time: datetime
    end_time: datetime
    event_type: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_time_range(self) -> "FixedEventInput":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class ScheduleGenerateRequest(BaseModel):
    user_id: int = 1
    target_date: date
    planning_mode: str = Field(default="balanced", min_length=1, max_length=50)
    start_hour: int = Field(default=9, ge=0, le=23)
    end_hour: int = Field(default=23, ge=1, le=24)
    buffer_minutes: int = Field(default=10, ge=0, le=60)
    include_fixed_events: bool = True
    tasks: list[TaskInput] = Field(default_factory=list)
    fixed_events: list[FixedEventInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_planning_window(self) -> "ScheduleGenerateRequest":
        if self.end_hour <= self.start_hour:
            raise ValueError("end_hour must be later than start_hour")
        return self


class ScheduleItem(BaseModel):
    type: Literal["task", "fixed_event"]
    title: str
    start_time: datetime
    end_time: datetime
    planned_minutes: int
    order_index: int
    task_id: int | None = None
    fixed_event_id: int | None = None
    category: str | None = None
    requires_focus: bool = False
    score: float | None = None


class AlgorithmSummary(BaseModel):
    available_minutes: int
    selected_task_count: int
    scheduled_task_count: int
    skipped_task_count: int
    total_task_minutes: int
    applied_algorithms: list[str]
    warnings: list[str] = Field(default_factory=list)


class ScheduleGenerateResponse(BaseModel):
    schedule_date: date
    planning_mode: str
    items: list[ScheduleItem]
    algorithm_summary: AlgorithmSummary
