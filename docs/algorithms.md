# Algorithms

Scheduler algorithms live in `scheduler-service`. The backend only forwards tasks and fixed events; the dashboard only renders the schedule response.

## MVP Pipeline

1. Load locked generated schedule items from the latest saved run.
   - Locked task items are preserved in later generation.
2. Filter candidate tasks.
   - Exclude `completed`, `skipped`, `is_fixed`, and locked task ids.
3. Score tasks.
   - `score = priority * 10 + deadline_urgency + focus_bonus - difficulty * 2 - planned_minutes / 30`
   - `planned_minutes` uses `predicted_minutes` when present, otherwise `estimated_minutes`.
4. Order candidates with a priority queue.
   - Sort by score descending, deadline ascending, then task id.
5. Select tasks with 0/1 knapsack.
   - Capacity is total free minutes in the planning window.
   - Unit size is 5 minutes.
6. Remove selected tasks with unmet selected-day dependencies.
7. Topologically sort selected tasks.
   - Detect dependency cycles and return `422`.
8. Build free slots from fixed events and locked item blockers.
   - Fixed events and locked items are protected and never overlapped.
9. Place tasks sequentially into the first fitting free slot.
   - Apply `buffer_minutes` after each task.
10. Merge locked items and newly generated items by start time.

## Current Limits

- Generated schedules are persisted by backend-api after scheduler-service returns a successful response.
- No task splitting yet, even when `is_splittable` is true.
- No timezone preference model yet; datetimes are treated as local MVP values.
- ML duration prediction is connected through backend-api and falls back to estimates when ml-service is unavailable.
- Manual schedule adjustment is button-based, not drag-and-drop.
