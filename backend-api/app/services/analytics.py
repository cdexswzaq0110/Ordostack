from datetime import date, datetime

from app.repositories.store import get_store
from app.schemas.analytics import DailyAnalyticsRead, TaskExecutionSummary

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
