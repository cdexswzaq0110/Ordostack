from datetime import date

from app.schemas.schedule import TaskInput


def planned_minutes(task: TaskInput) -> int:
    return task.predicted_minutes or task.estimated_minutes


def deadline_urgency(deadline_date: date | None, target_date: date) -> int:
    if deadline_date is None:
        return 0

    days_until_deadline = (deadline_date - target_date).days
    if days_until_deadline < 0:
        return 40
    if days_until_deadline <= 1:
        return 30
    if days_until_deadline <= 3:
        return 20
    if days_until_deadline <= 7:
        return 10
    return 5


def score_task(task: TaskInput, target_date: date) -> float:
    urgency = deadline_urgency(task.deadline.date() if task.deadline else None, target_date)
    focus_bonus = 4 if task.requires_focus else 0
    duration_penalty = planned_minutes(task) / 30
    score = (task.priority * 10) + urgency + focus_bonus - (task.difficulty * 2) - duration_penalty
    return round(score, 2)


def score_tasks(tasks: list[TaskInput], target_date: date) -> dict[int, float]:
    return {task.id: score_task(task, target_date) for task in tasks}
