from app.algorithms.knapsack import select_tasks_within_capacity
from app.algorithms.priority_queue import order_tasks_by_priority
from app.algorithms.priority_score import planned_minutes, score_tasks
from app.algorithms.schedule_builder import build_free_slots, build_schedule_items, total_slot_minutes
from app.algorithms.topological_sort import topological_sort_task_ids
from app.schemas.schedule import AlgorithmSummary, ScheduleGenerateRequest, ScheduleGenerateResponse, TaskInput

APPLIED_ALGORITHMS = [
    "priority-score",
    "topological-sort",
    "knapsack-capacity",
    "priority-queue",
    "fixed-event-free-slot-builder",
    "locked-item-preservation",
]


class ScheduleGenerationError(Exception):
    pass


def generate_schedule(payload: ScheduleGenerateRequest) -> ScheduleGenerateResponse:
    locked_task_ids = {
        item.task_id
        for item in payload.locked_items
        if item.type == "task" and item.task_id is not None
    }
    candidate_tasks = [
        task
        for task in payload.tasks
        if task.status not in {"completed", "skipped"} and not task.is_fixed and task.id not in locked_task_ids
    ]
    scores = score_tasks(candidate_tasks, payload.target_date)
    priority_ordered_tasks = order_tasks_by_priority(candidate_tasks, scores)

    free_slots = build_free_slots(
        target_date=payload.target_date,
        fixed_events=payload.fixed_events,
        start_hour=payload.start_hour,
        end_hour=payload.end_hour,
        include_fixed_events=payload.include_fixed_events,
    )
    available_minutes = total_slot_minutes(free_slots)

    capacity_selected_tasks = select_tasks_within_capacity(
        tasks=priority_ordered_tasks,
        capacity_minutes=available_minutes,
        scores=scores,
    )
    dependency_safe_tasks = remove_tasks_with_unmet_dependencies(capacity_selected_tasks, candidate_tasks)
    task_by_id = {task.id: task for task in dependency_safe_tasks}

    try:
        ordered_ids = topological_sort_task_ids(
            dependency_safe_tasks,
            preferred_order=[task.id for task in priority_ordered_tasks],
        )
    except ValueError as error:
        raise ScheduleGenerationError(str(error)) from error

    schedule_items, unscheduled_task_ids = build_schedule_items(
        tasks=[task_by_id[task_id] for task_id in ordered_ids],
        fixed_events=payload.fixed_events,
        locked_items=payload.locked_items,
        target_date=payload.target_date,
        scores=scores,
        start_hour=payload.start_hour,
        end_hour=payload.end_hour,
        buffer_minutes=payload.buffer_minutes,
        include_fixed_events=payload.include_fixed_events,
    )

    scheduled_task_count = sum(1 for item in schedule_items if item.type == "task")
    selected_task_count = len(dependency_safe_tasks)
    skipped_task_count = max(0, len(candidate_tasks) - (scheduled_task_count - len(locked_task_ids)))
    warnings = build_warnings(
        candidate_count=len(candidate_tasks),
        selected_count=selected_task_count,
        unscheduled_task_ids=unscheduled_task_ids,
        available_minutes=available_minutes,
    )

    return ScheduleGenerateResponse(
        schedule_date=payload.target_date,
        planning_mode=payload.planning_mode,
        items=schedule_items,
        algorithm_summary=AlgorithmSummary(
            available_minutes=available_minutes,
            selected_task_count=selected_task_count,
            scheduled_task_count=scheduled_task_count,
            skipped_task_count=skipped_task_count,
            total_task_minutes=sum(planned_minutes(task) for task in candidate_tasks),
            applied_algorithms=APPLIED_ALGORITHMS,
            warnings=warnings,
        ),
    )


def remove_tasks_with_unmet_dependencies(
    selected_tasks: list[TaskInput],
    candidate_tasks: list[TaskInput],
) -> list[TaskInput]:
    candidate_task_ids = {task.id for task in candidate_tasks}
    remaining_tasks = selected_tasks

    while True:
        selected_task_ids = {task.id for task in remaining_tasks}
        next_tasks = [
            task
            for task in remaining_tasks
            if all(dependency_id not in candidate_task_ids or dependency_id in selected_task_ids for dependency_id in task.dependency_ids)
        ]
        if len(next_tasks) == len(remaining_tasks):
            return next_tasks
        remaining_tasks = next_tasks


def build_warnings(
    candidate_count: int,
    selected_count: int,
    unscheduled_task_ids: list[int],
    available_minutes: int,
) -> list[str]:
    warnings: list[str] = []

    if available_minutes <= 0:
        warnings.append("No free planning capacity is available.")
    if selected_count < candidate_count:
        warnings.append("Some tasks were skipped because they exceeded the available capacity or had unmet dependencies.")
    if unscheduled_task_ids:
        warnings.append("Some selected tasks did not fit because fixed events fragmented the day.")

    return warnings
