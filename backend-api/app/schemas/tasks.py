from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    category: str = Field(min_length=1, max_length=50)
    estimated_minutes: int = Field(gt=0)
    priority: int = Field(ge=1, le=5)
    difficulty: int = Field(ge=1, le=5)
    deadline: datetime | None = None
    requires_focus: bool = False
    is_fixed: bool = False
    is_splittable: bool = False
    dependency_ids: list[int] = Field(default_factory=list)


class TaskCreate(TaskBase):
    user_id: int = 1


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    estimated_minutes: int | None = Field(default=None, gt=0)
    priority: int | None = Field(default=None, ge=1, le=5)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    deadline: datetime | None = None
    requires_focus: bool | None = None
    is_fixed: bool | None = None
    is_splittable: bool | None = None
    dependency_ids: list[int] | None = None
    status: str | None = Field(default=None, pattern="^(pending|in_progress|completed|skipped)$")


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    predicted_minutes: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

