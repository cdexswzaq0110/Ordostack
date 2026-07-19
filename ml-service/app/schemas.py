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


class PredictionFactor(BaseModel):
    """One contribution to the prediction, in minutes (signed)."""

    name: str
    impact_minutes: float


class DurationPrediction(BaseModel):
    task_id: int
    predicted_minutes: int
    # Backward-compatible score in [0, 1]; see `reliability` for the honest
    # label. This is a rule-derived score, NOT a calibrated probability.
    confidence: float = Field(ge=0, le=1)
    model_name: str
    reason: str
    model_version: str | None = None
    # Historical error band (prediction +/- recent category MAE), clamped to
    # serving bounds. Absent when the artifact has no learned error profile.
    lower_bound: int | None = None
    upper_bound: int | None = None
    # "high" | "medium" | "low" | "insufficient-data"
    reliability: str = "insufficient-data"
    # Training rows behind this task's category; None when the artifact
    # predates sample-count tracking.
    sample_count: int | None = None
    fallback: bool = False
    out_of_distribution: bool = False
    factors: list[PredictionFactor] = Field(default_factory=list)


class DurationPredictResponse(BaseModel):
    user_id: int
    model_name: str
    model_version: str
    predictions: list[DurationPrediction]
