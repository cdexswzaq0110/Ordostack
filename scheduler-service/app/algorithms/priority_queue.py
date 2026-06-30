from datetime import datetime
from heapq import heappop, heappush

from app.schemas.schedule import TaskInput


def order_tasks_by_priority(tasks: list[TaskInput], scores: dict[int, float]) -> list[TaskInput]:
    heap: list[tuple[float, datetime, int, TaskInput]] = []

    for task in tasks:
        deadline = task.deadline or datetime.max
        heappush(heap, (-scores.get(task.id, 0), deadline, task.id, task))

    ordered_tasks: list[TaskInput] = []
    while heap:
        ordered_tasks.append(heappop(heap)[3])

    return ordered_tasks
