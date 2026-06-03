from datetime import date, datetime, time, timedelta

from app.algorithms.priority_score import planned_minutes
from app.schemas.schedule import FixedEventInput, ScheduleItem, TaskInput

TimeSlot = tuple[datetime, datetime]


def make_naive(value: datetime) -> datetime:
    return value.replace(tzinfo=None)


def planning_window(target_date: date, start_hour: int, end_hour: int) -> TimeSlot:
    start_time = datetime.combine(target_date, time(start_hour))
    if end_hour == 24:
        end_time = datetime.combine(target_date + timedelta(days=1), time(0))
    else:
        end_time = datetime.combine(target_date, time(end_hour))
    return start_time, end_time


def minutes_between(start_time: datetime, end_time: datetime) -> int:
    return max(0, int((end_time - start_time).total_seconds() // 60))


def build_free_slots(
    target_date: date,
    fixed_events: list[FixedEventInput],
    start_hour: int,
    end_hour: int,
    include_fixed_events: bool,
) -> list[TimeSlot]:
    day_start, day_end = planning_window(target_date, start_hour, end_hour)
    if not include_fixed_events:
        return [(day_start, day_end)]

    blocking_events = sorted(
        (
            (max(make_naive(event.start_time), day_start), min(make_naive(event.end_time), day_end))
            for event in fixed_events
        ),
        key=lambda slot: slot[0],
    )

    free_slots: list[TimeSlot] = []
    cursor = day_start
    for event_start, event_end in blocking_events:
        if event_end <= day_start or event_start >= day_end:
            continue
        if cursor < event_start:
            free_slots.append((cursor, event_start))
        if cursor < event_end:
            cursor = event_end

    if cursor < day_end:
        free_slots.append((cursor, day_end))

    return free_slots


def total_slot_minutes(slots: list[TimeSlot]) -> int:
    return sum(minutes_between(start_time, end_time) for start_time, end_time in slots)


def build_schedule_items(
    tasks: list[TaskInput],
    fixed_events: list[FixedEventInput],
    target_date: date,
    scores: dict[int, float],
    start_hour: int,
    end_hour: int,
    buffer_minutes: int,
    include_fixed_events: bool,
) -> tuple[list[ScheduleItem], list[int]]:
    free_slots = build_free_slots(target_date, fixed_events, start_hour, end_hour, include_fixed_events)
    items = build_fixed_event_items(fixed_events) if include_fixed_events else []
    unscheduled_task_ids: list[int] = []
    order_index = len(items)

    for task in tasks:
        duration = planned_minutes(task)
        slot_index = find_first_fitting_slot(free_slots, duration)
        if slot_index is None:
            unscheduled_task_ids.append(task.id)
            continue

        slot_start, slot_end = free_slots[slot_index]
        task_start = slot_start
        task_end = task_start + timedelta(minutes=duration)
        items.append(
            ScheduleItem(
                type="task",
                task_id=task.id,
                title=task.title,
                start_time=task_start,
                end_time=task_end,
                planned_minutes=duration,
                order_index=order_index,
                category=task.category,
                requires_focus=task.requires_focus,
                score=scores.get(task.id),
            )
        )
        order_index += 1

        next_slot_start = task_end + timedelta(minutes=buffer_minutes)
        if next_slot_start < slot_end:
            free_slots[slot_index] = (next_slot_start, slot_end)
        else:
            free_slots.pop(slot_index)

    ordered_items = sorted(items, key=lambda item: (item.start_time, item.order_index))
    for index, item in enumerate(ordered_items):
        item.order_index = index

    return ordered_items, unscheduled_task_ids


def build_fixed_event_items(fixed_events: list[FixedEventInput]) -> list[ScheduleItem]:
    items: list[ScheduleItem] = []
    for index, event in enumerate(fixed_events):
        start_time = make_naive(event.start_time)
        end_time = make_naive(event.end_time)
        items.append(
            ScheduleItem(
                type="fixed_event",
                fixed_event_id=event.id,
                title=event.title,
                start_time=start_time,
                end_time=end_time,
                planned_minutes=minutes_between(start_time, end_time),
                order_index=index,
                category=event.event_type,
            )
        )
    return items


def find_first_fitting_slot(slots: list[TimeSlot], duration_minutes: int) -> int | None:
    for index, (slot_start, slot_end) in enumerate(slots):
        if minutes_between(slot_start, slot_end) >= duration_minutes:
            return index
    return None
