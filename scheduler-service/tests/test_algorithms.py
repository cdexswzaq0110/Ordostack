from datetime import date, datetime

import pytest

from app.algorithms.knapsack import select_tasks_within_capacity
from app.algorithms.priority_queue import order_tasks_by_priority
from app.algorithms.priority_score import score_tasks
from app.algorithms.topological_sort import topological_sort_task_ids
from app.schemas.schedule import TaskInput


TARGET_DATE = date(2026, 6, 3)


def make_task(
    task_id: int,
    title: str,
    minutes: int,
    priority: int = 3,
    difficulty: int = 3,
    dependency_ids: list[int] | None = None,
) -> TaskInput:
    return TaskInput(
        id=task_id,
        title=title,
        category="study",
        estimated_minutes=minutes,
        priority=priority,
        difficulty=difficulty,
        deadline=datetime(2026, 6, 3, 18, 0),
        dependency_ids=dependency_ids or [],
    )


def test_priority_score_orders_higher_priority_task_first() -> None:
    tasks = [
        make_task(1, "Low value", 30, priority=2),
        make_task(2, "High value", 30, priority=5),
    ]

    scores = score_tasks(tasks, TARGET_DATE)
    ordered = order_tasks_by_priority(tasks, scores)

    assert ordered[0].id == 2
    assert scores[2] > scores[1]


def test_topological_sort_respects_dependencies() -> None:
    tasks = [
        make_task(2, "Implementation", 60, dependency_ids=[1]),
        make_task(1, "Design", 45),
    ]

    assert topological_sort_task_ids(tasks, preferred_order=[2, 1]) == [1, 2]


def test_topological_sort_rejects_dependency_cycle() -> None:
    tasks = [
        make_task(1, "A", 30, dependency_ids=[2]),
        make_task(2, "B", 30, dependency_ids=[1]),
    ]

    with pytest.raises(ValueError, match="cycle"):
        topological_sort_task_ids(tasks)


def test_knapsack_selects_tasks_within_capacity() -> None:
    tasks = [
        make_task(1, "Long task", 120, priority=5),
        make_task(2, "Medium task", 45, priority=4),
        make_task(3, "Short task", 30, priority=4),
    ]
    scores = score_tasks(tasks, TARGET_DATE)

    selected = select_tasks_within_capacity(tasks, capacity_minutes=80, scores=scores)

    assert sum(task.estimated_minutes for task in selected) <= 80
    assert {task.id for task in selected} == {2, 3}
