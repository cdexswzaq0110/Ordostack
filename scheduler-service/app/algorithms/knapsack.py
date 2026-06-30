from math import ceil

from app.algorithms.priority_score import planned_minutes
from app.schemas.schedule import TaskInput

UNIT_MINUTES = 5


def select_tasks_within_capacity(
    tasks: list[TaskInput],
    capacity_minutes: int,
    scores: dict[int, float],
) -> list[TaskInput]:
    if capacity_minutes <= 0 or not tasks:
        return []

    capacity_units = capacity_minutes // UNIT_MINUTES
    if capacity_units <= 0:
        return []

    task_by_id = {task.id: task for task in tasks}
    dp: list[tuple[float, tuple[int, ...]]] = [(0, tuple()) for _ in range(capacity_units + 1)]

    for task in tasks:
        weight = max(1, ceil(planned_minutes(task) / UNIT_MINUTES))
        value = scores.get(task.id, 0)
        if weight > capacity_units:
            continue

        for current_capacity in range(capacity_units, weight - 1, -1):
            previous_value, previous_ids = dp[current_capacity - weight]
            candidate = (previous_value + value, previous_ids + (task.id,))
            current = dp[current_capacity]

            if candidate[0] > current[0] or (
                candidate[0] == current[0] and len(candidate[1]) > len(current[1])
            ):
                dp[current_capacity] = candidate

    selected_ids = max(dp, key=lambda entry: (entry[0], len(entry[1])))[1]
    return [task_by_id[task_id] for task_id in selected_ids]
