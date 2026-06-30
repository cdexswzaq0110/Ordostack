# API

Base URL:

```text
http://localhost:8000/api
```

Core planner endpoints require:

```text
Authorization: Bearer <access_token>
```

Get a local token with `/auth/login` or `/auth/register`.

## Health

Health endpoints are liveness checks. Readiness endpoints verify whether the service is ready to serve product traffic.

| Service | Health endpoint | Readiness endpoint |
| --- | --- | --- |
| backend-api | `GET /api/health`, `GET /health` | `GET /api/ready`, `GET /ready` |
| scheduler-service | `GET /health` | `GET /ready` |
| ml-service | `GET /health` | `GET /ready` |

All FastAPI services return `X-Request-ID`. If a valid `X-Request-ID` request header is provided, the same value is returned and written to the structured request log.

## Auth MVP

Issue 28 adds local bearer-token authentication. Issue 47 adds local production-auth hardening controls for password policy, token lifetime configuration, production secret validation, and failed-login rate limiting. It does not use AWS, OAuth, email delivery, or paid APIs.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/auth/register` | Create a local user and return an access token |
| `POST` | `/auth/login` | Login with email/password and return an access token |
| `GET` | `/auth/me` | Return the current bearer-token user |

Demo account:

```text
demo@ordostack.local
ordostack-demo
```

Register request:

```json
{
  "email": "qa@example.com",
  "display_name": "QA Tester",
  "password": "strong-password"
}
```

Registration password policy:

- At least `AUTH_PASSWORD_MIN_LENGTH` characters.
- At least one letter.
- At least one number or symbol.
- Must not contain the email username.

Failed login policy:

- Failed attempts are counted per email and client address.
- `AUTH_LOGIN_MAX_FAILURES`, `AUTH_LOGIN_WINDOW_SECONDS`, and `AUTH_LOGIN_LOCKOUT_SECONDS` control the local lockout behavior.
- Lockout responses return HTTP `429`.

Auth response:

```json
{
  "access_token": "local-hmac-token",
  "token_type": "bearer",
  "expires_at": "2026-06-11T12:00:00Z",
  "user": {
    "id": 2,
    "email": "qa@example.com",
    "display_name": "QA Tester",
    "created_at": "2026-06-04T00:00:00"
  }
}
```

## Demo MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/demo/reset?user_id=1` | Reset the bundled local demo user dataset |

This is a demo-only endpoint for local QA and customer demos. It returns `404` when `ORDOSTACK_ENV=production` and is not a production account-management API.

## Tasks MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/tasks?target_date=2026-06-03` | List non-deleted tasks for the authenticated user |
| `POST` | `/tasks` | Create a task |
| `PATCH` | `/tasks/{task_id}` | Update task fields or status |
| `POST` | `/tasks/{task_id}/reopen` | Reopen a completed task |
| `DELETE` | `/tasks/{task_id}` | Soft delete a task |

Create task example:

```json
{
  "title": "Draft QA cases",
  "description": "Prepare manual test checklist.",
  "category": "qa",
  "estimated_minutes": 45,
  "priority": 4,
  "difficulty": 2,
  "deadline": "2026-06-03T16:00:00",
  "requires_focus": false,
  "is_fixed": false,
  "is_splittable": true,
  "dependency_ids": []
}
```

## Fixed Events MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/fixed-events?target_date=2026-06-03` | List fixed events for the authenticated user |
| `POST` | `/fixed-events` | Create a fixed event |
| `POST` | `/fixed-events/recurring` | Create weekly recurring fixed events expanded into dated events |
| `PATCH` | `/fixed-events/{fixed_event_id}` | Update a fixed event |
| `DELETE` | `/fixed-events/{fixed_event_id}` | Soft delete a fixed event |

Create fixed event example:

```json
{
  "title": "Gym",
  "start_time": "2026-06-03T17:30:00",
  "end_time": "2026-06-03T18:15:00",
  "event_type": "exercise"
}
```

## Schedules MVP

Backend entrypoint:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/schedules/generate` | Generate a daily schedule from backend tasks and fixed events |
| `GET` | `/schedules/latest?target_date=2026-06-03` | Load the latest persisted generated schedule |
| `GET` | `/schedules/history?target_date=2026-06-03&limit=5` | Load recent persisted generated schedules |
| `PATCH` | `/schedules/history/{schedule_run_id}` | Rename a schedule history item |
| `PATCH` | `/schedules/history/{schedule_run_id}/items/{item_key}/lock` | Lock or unlock a schedule item |
| `PATCH` | `/schedules/history/{schedule_run_id}/items/{item_key}/time` | Manually adjust a schedule item time |
| `DELETE` | `/schedules/history/{schedule_run_id}` | Soft delete a schedule history item |
| `GET` | `/schedules/history/{schedule_run_id}/diff?against_run_id=1` | Compare two schedule history items |
| `GET` | `/schedules/history/{schedule_run_id}/export?format=markdown` | Export a schedule history item as Markdown, CSV, or PDF |

Request example:

```json
{
  "target_date": "2026-06-03",
  "planning_mode": "balanced",
  "start_hour": 9,
  "end_hour": 23,
  "buffer_minutes": 10,
  "include_fixed_events": true
}
```

Response shape:

```json
{
  "schedule_date": "2026-06-03",
  "planning_mode": "balanced",
  "items": [
    {
      "type": "task",
      "task_id": 1,
      "fixed_event_id": null,
      "title": "ML course chapter notes",
      "start_time": "2026-06-03T09:00:00",
      "end_time": "2026-06-03T10:45:00",
      "planned_minutes": 105,
      "order_index": 0,
      "category": "study",
      "requires_focus": true,
      "score": 72.5,
      "locked": false,
      "manual_override": false
    }
  ],
  "algorithm_summary": {
    "available_minutes": 620,
    "selected_task_count": 3,
    "scheduled_task_count": 3,
    "skipped_task_count": 0,
    "total_task_minutes": 225,
    "applied_algorithms": [
      "priority-score",
      "topological-sort",
      "knapsack-capacity",
      "priority-queue",
      "fixed-event-free-slot-builder"
    ],
    "warnings": []
  }
}
```

Scheduler internal endpoint:

```text
POST http://localhost:8100/schedule/generate
```

The scheduler endpoint accepts the same schedule request plus explicit `tasks` and `fixed_events` arrays. In Docker, backend-api calls it through `SCHEDULER_SERVICE_URL`.

Generated schedule persistence:

- `POST /schedules/generate` stores the generated schedule after scheduler-service returns successfully.
- `GET /schedules/latest` returns the latest generated schedule for the authenticated user and `target_date`.
- `GET /schedules/history` returns recent non-deleted generated schedules for the authenticated user and `target_date`, newest first.
- `PATCH /schedules/history/{schedule_run_id}` updates the history item title.
- `PATCH /schedules/history/{schedule_run_id}/items/{item_key}/lock` updates `locked`.
- `PATCH /schedules/history/{schedule_run_id}/items/{item_key}/time` updates start/end time, sets `locked=true`, sets `manual_override=true`, and rejects fixed-event conflicts.
- `DELETE /schedules/history/{schedule_run_id}` soft deletes the history item.
- `GET /schedules/history/{schedule_run_id}/diff` compares a selected generated run against another run.
- `GET /schedules/history/{schedule_run_id}/export` returns a downloadable payload for `markdown`, `csv`, or base64 `pdf`.
- If no saved schedule exists, `GET /schedules/latest` returns `404`.

Locked item key examples:

```text
task:1
fixed_event:2
```

Manual time adjustment request:

```json
{
  "start_time": "2026-06-03T11:00:00",
  "end_time": "2026-06-03T12:15:00"
}
```

Recurring fixed event example:

```json
{
  "title": "Weekly planning",
  "start_time": "2026-06-03T08:30:00",
  "end_time": "2026-06-03T09:00:00",
  "event_type": "planning",
  "recurrence_days": [2],
  "recurrence_until": "2026-06-17"
}
```

`recurrence_days` uses weekday values from `0` Monday through `6` Sunday.

## Schedule Templates MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/schedule-templates` | List named planning templates |
| `POST` | `/schedule-templates` | Create a named planning template |
| `PATCH` | `/schedule-templates/{template_id}` | Update a planning template |
| `DELETE` | `/schedule-templates/{template_id}` | Soft delete a planning template |

Template request:

```json
{
  "name": "Deep work morning",
  "planning_mode": "focus-heavy",
  "start_hour": 8,
  "end_hour": 13,
  "buffer_minutes": 15,
  "include_fixed_events": true
}
```

## Execution Logs MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/task-execution-logs?target_date=2026-06-03` | List execution events for the authenticated user |
| `POST` | `/tasks/{task_id}/execution/start` | Mark task as in progress |
| `POST` | `/tasks/{task_id}/execution/pause` | Pause an in-progress task |
| `POST` | `/tasks/{task_id}/execution/complete` | Complete a task and close any active interval |
| `POST` | `/tasks/{task_id}/execution/skip` | Skip a task |

Execution event request:

```json
{
  "occurred_at": "2026-06-03T09:00:00"
}
```

`occurred_at` is optional. When omitted, backend-api uses server time.

## Daily Analytics MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/analytics/daily?target_date=2026-06-03` | Daily execution summary for the authenticated user |
| `GET` | `/analytics/completion-forecast?target_date=2026-06-03` | Heuristic completion forecast |

Response shape:

```json
{
  "user_id": 1,
  "target_date": "2026-06-03",
  "total_tasks": 3,
  "completed_tasks": 1,
  "skipped_tasks": 0,
  "in_progress_tasks": 0,
  "estimated_minutes": 225,
  "actual_minutes": 47,
  "estimate_delta_minutes": -178,
  "completion_rate": 33,
  "focus_minutes": 175,
  "task_summaries": [
    {
      "task_id": 3,
      "title": "Backend API review",
      "status": "completed",
      "estimated_minutes": 50,
      "actual_minutes": 47,
      "estimate_delta_minutes": -3
    }
  ]
}
```

## Duration Prediction MVP

Backend entrypoint:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/ml/duration-predictions?target_date=2026-06-03` | Predict task duration for dashboard and scheduler |
| `GET` | `/ml/duration-feedback?target_date=2026-06-03` | Export completed-task duration feedback as CSV |

Response shape:

```json
{
  "user_id": 1,
  "target_date": "2026-06-03",
  "model_name": "local-duration-regressor",
  "model_version": "0.1.0",
  "predictions": [
    {
      "task_id": 1,
      "predicted_minutes": 150,
      "confidence": 0.58,
      "model_name": "local-duration-regressor",
      "reason": "trained local artifact"
    }
  ]
}
```

ML service internal endpoint:

```text
POST http://localhost:8200/duration/predict
```

The backend passes task features and execution actual minutes to ml-service. If ml-service is unavailable, backend-api falls back to `estimated_minutes` with `model_name=estimate-fallback`.

ML model info endpoint:

```text
GET http://localhost:8200/model/info
```

ML model registry endpoint:

```text
GET http://localhost:8200/model/registry
```

Expected local artifact response:

```json
{
  "model_name": "local-duration-regressor",
  "model_version": "0.1.0",
  "source": "local-artifact"
}
```

## Current Data Store

Docker Compose runs backend-api with `DATA_STORE=mysql`, backed by the `mysql:8.4` service and the `ordostack` database. The persisted MVP tables are `tasks`, `fixed_events`, `execution_logs`, `schedule_runs`, `schedule_items`, and `schedule_templates`.

Local pytest runs use the in-memory seeded repository by default, so tests do not require a running database.

MySQL host access:

```text
localhost:3307 -> mysql container port 3306
```

Generated schedules are persisted after `POST /api/schedules/generate`.
