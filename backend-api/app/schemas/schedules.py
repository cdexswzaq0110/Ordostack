from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


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
    created_at: datetime
    planning_mode: str
    scheduled_task_count: int
    item_count: int
    schedule: ScheduleGenerateResponse
