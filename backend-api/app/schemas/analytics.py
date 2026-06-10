from datetime import date

from pydantic import BaseModel


class TaskExecutionSummary(BaseModel):
    task_id: int
    title: str
    status: str
    estimated_minutes: int
    actual_minutes: int
    estimate_delta_minutes: int


class DailyAnalyticsRead(BaseModel):
    user_id: int
    target_date: date
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int
    in_progress_tasks: int
    estimated_minutes: int
    actual_minutes: int
    estimate_delta_minutes: int
    completion_rate: int
    focus_minutes: int
    task_summaries: list[TaskExecutionSummary]


class CompletionForecastRead(BaseModel):
    user_id: int
    target_date: date
    forecast_completion_rate: int
    remaining_minutes: int
    projected_done_tasks: int
    confidence: float
    reason: str
