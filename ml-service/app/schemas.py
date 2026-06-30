from pydantic import BaseModel, Field


class DurationTaskInput(BaseModel):
    task_id: int
    title: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=50)
    estimated_minutes: int = Field(gt=0)
    priority: int = Field(ge=1, le=5)
    difficulty: int = Field(ge=1, le=5)
    requires_focus: bool = False
    actual_minutes: int = Field(default=0, ge=0)


class DurationPredictRequest(BaseModel):
    user_id: int = 1
    tasks: list[DurationTaskInput] = Field(default_factory=list)


class DurationPrediction(BaseModel):
    task_id: int
    predicted_minutes: int
    confidence: float = Field(ge=0, le=1)
    model_name: str
    reason: str


class DurationPredictResponse(BaseModel):
    user_id: int
    model_name: str
    model_version: str
    predictions: list[DurationPrediction]
