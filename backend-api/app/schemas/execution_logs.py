from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

ExecutionEventType = Literal["start", "pause", "complete", "skip"]


class TaskExecutionEventRequest(BaseModel):
    user_id: int = 1
    occurred_at: datetime | None = None


class TaskExecutionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_id: int
    event_type: ExecutionEventType
    occurred_at: datetime
    created_at: datetime
