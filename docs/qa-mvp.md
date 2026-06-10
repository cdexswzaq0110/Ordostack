# QA MVP Test Plan

Scope: Issues 34-45 Non-Docker Product Hardening, Issue 33 Traditional Chinese Dashboard Locale, Issue 32 Backup And Restore MVP, Issue 31 Observability Baseline, Issue 30 Deployment Baseline, Issue 29 User Isolation, Issue 28 Authentication Foundation, Issue 27 Environment Configuration Hardening, Issue 25 Browser Screenshot Smoke, Issue 24 Schedule Export, Issue 23 Schedule Diff, Issue 22 Schedule History Actions, Issue 21 Task Filter And Sort, Issue 20 Demo MVP Documentation Baseline, Issue 19 E2E Smoke Workflow, Demo Seed And Reset Control, Dashboard UX Polish, Schedule History Management, Date Picker Navigation, Fixed Event Editing, Task Editing, Task, Fixed Event, Scheduler, Persisted Schedule, Date Navigation, Execution Log, Analytics, Duration Prediction, Local ML Training, MySQL Persistence, and Migration Baseline MVP.

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

Expected: output contains `20260610_0004`.
15. Click `Next day`.
16. Expected: the date changes to June 4, 2026 and dashboard data reloads.
17. Click `Previous day`.
18. Expected: the date changes back to June 3, 2026 and saved schedule data reloads.
19. Select a date without demo data.
20. Expected: timeline, history, and fixed event areas show coherent empty states.

## E2E Smoke Script

Windows PowerShell:

```powershell
python scripts\e2e_smoke.py
```

## Issue 34-45 Non-Docker Checks

Run service tests from each service directory:

```powershell
cd backend-api
python -m pytest tests
cd ..\scheduler-service
python -m pytest tests
cd ..\ml-service
python -m pytest tests
cd ..
```

Run local audit scripts:

```powershell
python scripts\a11y_static_audit.py
python scripts\security_audit.py --root .
python scripts\visual_regression.py --baseline artifacts\visual-baseline\dashboard.png --candidate artifacts\browser-smoke\dashboard.png --threshold 0.01
```

Manual schedule control checks:

1. Generate a schedule for June 3, 2026.
2. Click the lock icon on a task schedule item.
3. Expected: the item metadata shows locked state after refresh.
4. Click `+15` or `-15` move control.
5. Expected: the item moves, remains locked, and shows manual state.
6. Try moving an item into a fixed event block.
7. Expected: backend rejects the change with a conflict response.
8. Generate a new plan.
9. Expected: locked item remains in the preserved time range.

Recurring fixed event checks:

1. Call `POST /api/fixed-events/recurring`.
2. Use `recurrence_days` with weekday values `0` to `6`.
3. Expected: API returns dated fixed events with `recurrence_id` and `recurrence_rule`.
4. Open each generated date.
5. Expected: fixed event appears on those dates.

Schedule template checks:

1. Create a schedule template.
2. Update its name or buffer.
3. List templates.
4. Delete the template.
5. Expected: deleted template no longer appears.

Export checks:

1. Export a generated schedule as Markdown.
2. Export the same schedule as CSV.
3. Export the same schedule as PDF.
4. Expected: PDF payload uses base64 and decodes to `%PDF-1.4`.

ML and analytics checks:

1. Call `GET /api/analytics/completion-forecast?target_date=2026-06-03`.
2. Expected: response includes forecast completion rate, remaining minutes, projected done tasks, confidence, and reason.
3. Call `GET /api/ml/duration-feedback?target_date=2026-06-03`.
4. Expected: response contains CSV rows only for completed tasks with actual minutes.
5. Call `GET http://localhost:8200/model/registry`.
6. Expected: response reports local JSON registry metadata or fallback.

Linux / WSL:

```bash
python scripts/e2e_smoke.py
```

Expected:

- Console output contains `"status": "ok"`.
- Script exits with status code `0`.
- Local smoke task and fixed event records are created for traceability.

## Browser Screenshot Smoke

Windows PowerShell:

```powershell
python scripts\browser_smoke.py
```

Linux / WSL:

```bash
python scripts/browser_smoke.py
```

Expected:

- Console output contains `"status": "ok"`.
- Script exits with status code `0`.
- `artifacts/browser-smoke/dashboard.png` exists.
- Screenshot file is a non-trivial PNG.

## Dashboard Locale Checks

1. Open `http://localhost:5173`.
2. Expected: dashboard loads in English by default.
3. Change Language to `繁體中文`.
4. Expected: navigation, controls, form labels, empty states, analytics labels, and schedule labels switch to Traditional Chinese.
5. Refresh the page.
6. Expected: selected language remains Traditional Chinese.
7. Change Language back to `English`.
8. Expected: dashboard returns to English.
9. Expected: user-entered task and fixed event titles are unchanged.

## Environment Configuration Checks

1. Confirm `.env.example` documents backend, dashboard, ML, and optional ClearML variables.
2. Confirm Docker Compose sets `ORDOSTACK_ENV=local` for backend-api.
3. Run backend-api tests.
4. Expected: config validation tests pass.
5. Confirm production MySQL mode rejects an empty `DB_PASSWORD`.
6. Confirm production mode requires explicit `AUTH_TOKEN_SECRET`.

## Deployment Baseline Checks

1. Confirm `.env.production.example` exists.
2. Confirm all secret-like values in `.env.production.example` are blank.
3. Confirm `infra/nginx/ordostack.conf` proxies `/api/` to backend-api and `/` to web-dashboard.
4. Run:

```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile production config
```

5. Expected: config renders without creating AWS, domain, TLS, or paid-service resources.

## Observability Baseline Checks

1. Call backend readiness with a request ID:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ready" -Headers @{ "X-Request-ID" = "qa-backend-ready" }
```

2. Expected: response returns `status: ready`.
3. Expected: response header includes `X-Request-ID: qa-backend-ready`.
4. Call scheduler and ML readiness:

```powershell
Invoke-RestMethod -Uri "http://localhost:8100/ready" -Headers @{ "X-Request-ID" = "qa-scheduler-ready" }
Invoke-RestMethod -Uri "http://localhost:8200/ready" -Headers @{ "X-Request-ID" = "qa-ml-ready" }
```

5. Expected: both responses return `status: ready`.
6. Review service logs:

```powershell
docker compose logs backend-api
docker compose logs scheduler-service
docker compose logs ml-service
```

7. Expected: logs contain JSON entries with `event`, `service`, `request_id`, `method`, `path`, `status_code`, and `duration_ms`.
8. Expected: logs do not contain request bodies, query strings, authorization headers, cookies, database passwords, or token values.

## Backup And Restore MVP Checks

1. Confirm Docker Compose is running:

```powershell
docker compose ps
```

2. Create a local MySQL backup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup_mysql.ps1
```

3. Expected: console output contains `"status": "ok"`.
4. Expected: a SQL file exists under `artifacts/backups`.
5. Verify the generated backup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_mysql_backup.ps1 -Path artifacts\backups\<backup-file>.sql
```

6. Expected: verification returns `"status": "ok"`.
7. Expected: verification confirms `destructive_statements` is `none`.
8. Confirm backup artifacts are not staged for Git:

```powershell
git status --short artifacts
```

9. Expected: no generated SQL backup file is tracked.
10. Restore drill must use a temporary database or disposable MySQL container only.
11. Do not restore into the active `ordostack` database during QA.

## Auth Foundation Checks

1. Open `http://localhost:5173`.
2. In the Account panel, click `Demo`.
3. Expected: account summary shows `Demo User`.
4. Click sign out.
5. Switch to `Register`.
6. Enter a local email, display name, and password with at least 8 characters.
7. Expected: account is created and account summary appears.
8. Call `/api/auth/me` with the returned bearer token if testing through API.
9. Expected: response returns the current local user.

For PowerShell API snippets below, create auth headers first:

```powershell
$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" -ContentType "application/json" -Body '{"email":"demo@ordostack.local","password":"ordostack-demo"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
```

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

### Filter And Sort Task Queue

1. Open `http://localhost:5173`.
2. Select a task status filter.
3. Expected: Task queue only shows matching tasks.
4. Select a category filter.
5. Expected: Task queue only shows matching category rows.
6. Select Focus `Focus` or `Flexible`.
7. Expected: Task queue follows the focus requirement.
8. Change Sort to deadline, estimate, or status.
9. Expected: Task queue order changes without reloading the page.
10. Click `Reset`.
11. Expected: filters return to defaults and all matching date tasks are visible.

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
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/latest?target_date=2026-06-03" -Headers $headers
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
5. Click the rename control on a history row.
6. Enter a title and save.
7. Expected: the schedule history row shows the updated title.
8. Click the delete control on a history row and confirm.
9. Expected: the row disappears from schedule history.
10. Select a history row that has an older run below it.
11. Click `Compare previous`.
12. Expected: diff summary shows added, removed, changed, and minute-delta counts.
13. Click `Export MD`.
14. Expected: browser downloads a Markdown text export for the selected generated plan.
15. Call:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/history?target_date=2026-06-03&limit=5" -Headers $headers
```

Expected:

- Response contains recent generated schedule runs.
- First item is the newest run.
- Soft-deleted runs are not returned.
- Export API supports `format=markdown` and `format=csv`.

## ML Duration Prediction Tests

### Dashboard Prediction

1. Open the dashboard.
2. Expected: task rows show `estimate`, `predicted`, and `actual` minutes.
3. Expected: AI review panel shows `Predicted workload` before generating a plan.

### Prediction API

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/ml/duration-predictions?target_date=2026-06-03" -Headers $headers
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
Invoke-RestMethod -Uri "http://localhost:8000/api/task-execution-logs?target_date=2026-06-03" -Headers $headers
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

3. Expected: current revision is `20260604_0003`.
4. Expected: backend health remains `ok`.

## API Checks

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/demo/reset?user_id=1"
$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" -ContentType "application/json" -Body '{"email":"demo@ordostack.local","password":"ordostack-demo"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Uri "http://localhost:8000/api/tasks?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/fixed-events?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/task-execution-logs?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/analytics/daily?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/ml/duration-predictions?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8000/api/schedules/latest?target_date=2026-06-03" -Headers $headers
Invoke-RestMethod -Uri "http://localhost:8200/model/info"
```

## Known Limitations

- Demo reset is for local demo user data only and is not a production data restore feature.
- Schedule history rename, deletion, and compact diff are implemented; side-by-side timeline diff is not implemented yet.
- Active timers only affect actual minutes after pause, complete, or skip closes an interval.
- Task splitting is not implemented yet.
- Duration prediction uses a local JSON artifact and local registry abstraction, not a hosted production model promotion workflow.
- Core planner APIs require local bearer authentication and scope data to the current user.
- Observability baseline provides request IDs, request logs, and readiness only; metrics, tracing, alerting, and hosted uptime checks are not implemented yet.
- Backup/restore baseline provides local SQL dump and verification only; scheduled jobs, encrypted off-host storage, and automated production restore are not implemented yet.
- A11y, security, and visual regression gates are local MVP scripts; formal external audit and hosted regression governance are not implemented yet.
- Docker finalization is intentionally deferred to a dedicated deployment hardening pass.
- Schema bootstrap remains as a compatibility fallback; Alembic is the Docker startup path.
- MySQL uses local development settings and no production credential management.
