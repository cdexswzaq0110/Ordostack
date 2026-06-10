from datetime import date, datetime

from app.repositories.store import get_store
from app.schemas.analytics import CompletionForecastRead, DailyAnalyticsRead, TaskExecutionSummary

CLOSING_EVENTS = {"pause", "complete", "skip"}


def get_daily_analytics(user_id: int, target_date: date) -> DailyAnalyticsRead:
    store = get_store()
    tasks = store.list_tasks(user_id=user_id, target_date=target_date)
    logs = store.list_execution_logs(user_id=user_id, target_date=target_date)
    actual_minutes_by_task = calculate_actual_minutes_by_task(logs)

    task_summaries = [
        TaskExecutionSummary(
            task_id=task["id"],
            title=task["title"],
            status=task["status"],
            estimated_minutes=task["estimated_minutes"],
            actual_minutes=actual_minutes_by_task.get(task["id"], 0),
            estimate_delta_minutes=actual_minutes_by_task.get(task["id"], 0) - task["estimated_minutes"],
        )
        for task in tasks
    ]

    completed_tasks = sum(1 for task in tasks if task["status"] == "completed")
    skipped_tasks = sum(1 for task in tasks if task["status"] == "skipped")
    in_progress_tasks = sum(1 for task in tasks if task["status"] == "in_progress")
    estimated_minutes = sum(task["estimated_minutes"] for task in tasks)
    actual_minutes = sum(summary.actual_minutes for summary in task_summaries)

    return DailyAnalyticsRead(
        user_id=user_id,
        target_date=target_date,
        total_tasks=len(tasks),
        completed_tasks=completed_tasks,
        skipped_tasks=skipped_tasks,
        in_progress_tasks=in_progress_tasks,
        estimated_minutes=estimated_minutes,
        actual_minutes=actual_minutes,
        estimate_delta_minutes=actual_minutes - estimated_minutes,
        completion_rate=0 if not tasks else round((completed_tasks / len(tasks)) * 100),
        focus_minutes=sum(
            task["estimated_minutes"]
            for task in tasks
            if task["requires_focus"] and task["status"] not in {"completed", "skipped"}
        ),
        task_summaries=task_summaries,
    )


def get_completion_forecast(user_id: int, target_date: date) -> CompletionForecastRead:
    analytics = get_daily_analytics(user_id=user_id, target_date=target_date)
    remaining_tasks = max(0, analytics.total_tasks - analytics.completed_tasks - analytics.skipped_tasks)
    remaining_minutes = sum(
        max(0, summary.estimated_minutes - summary.actual_minutes)
        for summary in analytics.task_summaries
        if summary.status not in {"completed", "skipped"}
    )

    if analytics.total_tasks == 0:
        return CompletionForecastRead(
            user_id=user_id,
            target_date=target_date,
            forecast_completion_rate=0,
            remaining_minutes=0,
            projected_done_tasks=0,
            confidence=0.4,
            reason="No tasks are available for the selected date.",
        )

    actual_signal = min(1.0, analytics.actual_minutes / max(1, analytics.estimated_minutes))
    workload_pressure = min(1.0, remaining_minutes / 240) if remaining_minutes else 0
    projected_additional_tasks = round(remaining_tasks * max(0.0, actual_signal - (workload_pressure * 0.35)))
    projected_done_tasks = min(analytics.total_tasks, analytics.completed_tasks + projected_additional_tasks)
    forecast_completion_rate = round((projected_done_tasks / analytics.total_tasks) * 100)
    confidence = 0.55
    if analytics.actual_minutes > 0:
        confidence += 0.2
    if remaining_minutes <= 120:
        confidence += 0.1

    return CompletionForecastRead(
        user_id=user_id,
        target_date=target_date,
        forecast_completion_rate=min(100, max(0, forecast_completion_rate)),
        remaining_minutes=remaining_minutes,
        projected_done_tasks=projected_done_tasks,
        confidence=round(min(confidence, 0.9), 2),
        reason="Heuristic forecast based on current completion, actual minutes, and remaining workload.",
    )


def calculate_actual_minutes_by_task(logs: list[dict]) -> dict[int, int]:
    actual_minutes_by_task: dict[int, int] = {}
    active_start_by_task: dict[int, datetime] = {}

    for log in sorted(logs, key=lambda item: (item["occurred_at"].replace(tzinfo=None), item["id"])):
        task_id = log["task_id"]
        if log["event_type"] == "start" and task_id not in active_start_by_task:
            active_start_by_task[task_id] = log["occurred_at"]
            continue

        if log["event_type"] in CLOSING_EVENTS and task_id in active_start_by_task:
            start_time = active_start_by_task.pop(task_id)
            actual_minutes_by_task[task_id] = actual_minutes_by_task.get(task_id, 0) + minutes_between(
                start_time,
                log["occurred_at"],
            )

    return actual_minutes_by_task


def minutes_between(start_time: datetime, end_time: datetime) -> int:
    start_time = start_time.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    if end_time <= start_time:
        return 0
    return int((end_time - start_time).total_seconds() // 60)
