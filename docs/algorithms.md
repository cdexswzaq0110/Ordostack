# Algorithms

Scheduler algorithms live in `scheduler-service`. The backend only forwards tasks and fixed events; the dashboard only renders the schedule response.

## MVP Pipeline

1. Filter candidate tasks.
   - Exclude `completed`, `skipped`, and `is_fixed` tasks.
2. Score tasks.
   - `score = priority * 10 + deadline_urgency + focus_bonus - difficulty * 2 - planned_minutes / 30`
   - `planned_minutes` uses `predicted_minutes` when present, otherwise `estimated_minutes`.
3. Order candidates with a priority queue.
   - Sort by score descending, deadline ascending, then task id.
4. Select tasks with 0/1 knapsack.
   - Capacity is total free minutes in the planning window.
   - Unit size is 5 minutes.
5. Remove selected tasks with unmet selected-day dependencies.
6. Topologically sort selected tasks.
   - Detect dependency cycles and return `422`.
7. Build free slots from fixed events.
   - Fixed events are protected and never overlapped.
8. Place tasks sequentially into the first fitting free slot.
   - Apply `buffer_minutes` after each task.

## Current Limits

- Generated schedules are persisted by backend-api after scheduler-service returns a successful response.
- No task splitting yet, even when `is_splittable` is true.
- No timezone preference model yet; datetimes are treated as local MVP values.
- ML duration prediction is not connected yet.
