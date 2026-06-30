from heapq import heappop, heappush

from app.schemas.schedule import TaskInput


def topological_sort_task_ids(tasks: list[TaskInput], preferred_order: list[int] | None = None) -> list[int]:
    task_by_id = {task.id: task for task in tasks}
    rank = {task_id: index for index, task_id in enumerate(preferred_order or task_by_id.keys())}
    incoming_count = {task.id: 0 for task in tasks}
    outgoing_edges: dict[int, list[int]] = {task.id: [] for task in tasks}

    for task in tasks:
        for dependency_id in task.dependency_ids:
            if dependency_id not in task_by_id:
                continue

            incoming_count[task.id] += 1
            outgoing_edges[dependency_id].append(task.id)

    ready_heap: list[tuple[int, int]] = []
    for task_id, count in incoming_count.items():
        if count == 0:
            heappush(ready_heap, (rank.get(task_id, len(rank)), task_id))

    sorted_ids: list[int] = []
    while ready_heap:
        _, task_id = heappop(ready_heap)
        sorted_ids.append(task_id)

        for next_task_id in outgoing_edges[task_id]:
            incoming_count[next_task_id] -= 1
            if incoming_count[next_task_id] == 0:
                heappush(ready_heap, (rank.get(next_task_id, len(rank)), next_task_id))

    if len(sorted_ids) != len(tasks):
        raise ValueError("Task dependency cycle detected")

    return sorted_ids
