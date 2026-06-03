# QA MVP Test Plan

Scope: Issue 16 Schedule History Management, Date Picker Navigation, Fixed Event Editing, Task Editing, Task, Fixed Event, Scheduler, Persisted Schedule, Date Navigation, Execution Log, Analytics, Duration Prediction, Local ML Training, MySQL Persistence, and Migration Baseline MVP.

## Environment

```powershell
docker compose up --build -d
```

Dashboard:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8000/api
```

MySQL:

```text
localhost:3307 -> mysql container port 3306
database: ordostack
```

## Smoke Tests

1. Open `http://localhost:5173`.
2. Confirm the dashboard loads without a red error banner.
3. Confirm seeded tasks appear in Task queue.
4. Confirm seeded fixed events appear in Protected time.
5. Confirm all Docker services are healthy with:

```powershell
docker compose ps
```
6. Click `Generate Plan`.
7. Expected: button shows a loading state, then the timeline title changes to generated schedule data.
8. Expected: AI review panel shows scheduler algorithm summary.
9. Confirm the overview shows `Actual time`.
10. Confirm task rows show `predicted` minutes.
11. Confirm MySQL is healthy in `docker compose ps`.
12. Refresh the dashboard.
13. Expected: the timeline title shows the latest saved schedule without clicking `Generate Plan` again.
14. Confirm backend migration version:

```powershell
docker compose exec backend-api alembic current
```

Expected: output contains `20260603_0001`.
15. Click `Next day`.
16. Expected: the date changes to June 4, 2026 and dashboard data reloads.
17. Click `Previous day`.
18. Expected: the date changes back to June 3, 2026 and saved schedule data reloads.

## Task Tests

### Date Navigation

1. Open `http://localhost:5173`.
2. Confirm the top date shows June 3, 2026.
3. Click `Next day`.
4. Expected: the top date shows June 4, 2026.
5. Expected: task queue and analytics reload for June 4, 2026.
6. Click `Previous day`.
7. Expected: the top date shows June 3, 2026.
8. Select a date through the date picker.
9. Expected: dashboard data reloads for the selected date.
10. Click `Today`.
11. Expected: the top date changes to the current local date.
12. Expected: latest saved schedule can appear again for dates with saved schedules.

### Create Task

1. Click `Add task`.
2. Enter a title.
3. Keep minutes greater than `0`.
4. Click `Create task`.
5. Expected: new task appears in Task queue and timeline.
6. Expected: the created task belongs to the currently selected date.

### Edit Task

1. Click the edit icon on a task row.
2. Change title, category, minutes, priority, difficulty, deadline time, or focus requirement.
3. Click `Save changes`.
4. Expected: the task row refreshes with the edited values.
5. Expected: the edit form closes after a successful save.
6. Expected: refreshing the dashboard keeps the edited task values.

### Complete Task

1. Click the check icon on a pending task.
2. Expected: task state changes to `Done`.
3. Expected: completion metric updates.

### Start And Pause Task

1. Click the play icon on a pending task.
2. Expected: task state changes to `Doing`.
3. Click the pause icon on the same task.
4. Expected: task state changes back to `Ready`.
5. Expected: execution logs API contains `start` and `pause` events.

### Skip Task

1. Click the skip icon on a pending task.
2. Expected: task state changes to `Skipped`.
3. Expected: skipped task no longer appears in generated schedule candidates.

### Reopen Task

1. Click the reopen icon on a completed task.
2. Expected: task state changes back to `Ready`.

### Soft Delete Task

1. Click the delete icon on a task.
2. Expected: task disappears from the list.
3. Expected: task is not returned by `GET /api/tasks`.

## Fixed Event Tests

### Create Fixed Event

1. Click `Add` in Protected time.
2. Enter a title.
3. Set start time earlier than end time.
4. Click `Create event`.
5. Expected: event appears in Protected time and timeline.
6. Expected: the created event belongs to the currently selected date.

### Edit Fixed Event

1. Click the edit icon on a fixed event row.
2. Change title, type, start time, or end time.
3. Click `Save event`.
4. Expected: the event row refreshes with the edited values.
5. Expected: refreshing the dashboard keeps the edited event values.

### Soft Delete Fixed Event

1. Click the delete icon on a fixed event row.
2. Expected: the event disappears from Protected time.
3. Expected: the event is not returned by `GET /api/fixed-events`.

### Invalid Fixed Event

1. Create an event with end time earlier than start time through API.
2. Expected: API returns `422`.

## Schedule Tests

### Generate Plan

1. Confirm the dashboard has pending tasks and fixed events.
2. Click `Generate Plan`.
3. Expected: generated timeline includes task blocks and protected fixed events.
4. Expected: no task block overlaps a protected fixed event.
5. Expected: Plan quality panel changes from baseline metrics to scheduler metrics.

### Schedule API

```powershell
$body = @{
  user_id = 1
  target_date = "2026-06-03"
  planning_mode = "balanced"
  start_hour = 9
  end_hour = 23
  buffer_minutes = 10
  include_fixed_events = $true
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/schedules/generate" -ContentType "application/json" -Body $body
```

Expected:

- `items` contains generated schedule blocks.
- `algorithm_summary.scheduled_task_count` is greater than or equal to `1`.
- Fixed event blocks are preserved.

### Latest Schedule API

After generating a schedule, call:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/latest?user_id=1&target_date=2026-06-03"
```

Expected:

- Response shape matches the schedule generation response.
- `items` contains the latest persisted schedule blocks.
- `algorithm_summary.scheduled_task_count` matches the latest generated plan.

### Schedule History

1. Click `Generate Plan` at least twice.
2. Expected: `Recent generated plans` appears below the timeline.
3. Click an older history row.
4. Expected: the timeline switches to the selected generated plan.
5. Call:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/history?user_id=1&target_date=2026-06-03&limit=5"
```

Expected:

- Response contains recent generated schedule runs.
- First item is the newest run.

## ML Duration Prediction Tests

### Dashboard Prediction

1. Open the dashboard.
2. Expected: task rows show `estimate`, `predicted`, and `actual` minutes.
3. Expected: AI review panel shows `Predicted workload` before generating a plan.

### Prediction API

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ml/duration-predictions?user_id=1&target_date=2026-06-03"
```

Expected:

- `model_name` is `local-duration-regressor` when the bundled training artifact is available.
- `predictions` contains task ids and `predicted_minutes`.
- `predicted_minutes` is greater than `0`.

### Local Training Artifact

Windows PowerShell:

```powershell
cd ml-service
..\.venv\Scripts\python.exe training\train_duration_model.py
```

Expected:

- `training/artifacts/duration_model.json` exists.
- `training/artifacts/duration_metrics.json` exists.
- Console output includes `model_mae`.

Linux / WSL:

```bash
cd ml-service
../.venv/bin/python training/train_duration_model.py
```

## Persistence Tests

### Task Persists After Backend Restart

1. Create a task through the dashboard or API.
2. Restart only the backend container:

```powershell
docker compose restart backend-api
```

3. Open `http://localhost:5173`.
4. Expected: the created task still appears.
5. Expected: `GET /api/tasks` still returns the created task.

### Execution Logs Persist

1. Start and complete a task.
2. Restart only the backend container:

```powershell
docker compose restart backend-api
```

3. Call:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/task-execution-logs?user_id=1&target_date=2026-06-03"
```

4. Expected: start and complete events remain available.

### Generated Schedule Persists

1. Click `Generate Plan`.
2. Restart only the backend container:

```powershell
docker compose restart backend-api
```

3. Refresh `http://localhost:5173`.
4. Expected: the dashboard shows `Saved schedule`.
5. Expected: `GET /api/schedules/latest` returns the saved schedule.

### Migration Baseline Is Applied

1. Start Docker Compose:

```powershell
docker compose up --build -d
```

2. Check migration status:

```powershell
docker compose exec backend-api alembic current
```

3. Expected: current revision is `20260603_0001`.
4. Expected: backend health remains `ok`.

## API Checks

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/tasks?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8000/api/fixed-events?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8000/api/task-execution-logs?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/daily?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8000/api/ml/duration-predictions?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/latest?user_id=1&target_date=2026-06-03"
Invoke-RestMethod -Uri "http://localhost:8200/model/info"
```

## Known Limitations

- Schedule history is persisted, but only the latest schedule is exposed through the API.
- Active timers only affect actual minutes after pause, complete, or skip closes an interval.
- Task splitting is not implemented yet.
- Duration prediction uses a local JSON training artifact, not a production model registry.
- There is no authentication; MVP uses `user_id=1`.
- ML metrics are local sample metrics until a production model registry exists.
- Schema bootstrap remains as a compatibility fallback; Alembic is the Docker startup path.
- MySQL uses local development settings and no production credential management.
