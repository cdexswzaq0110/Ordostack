# API

Base URL:

```text
http://localhost:8000/api
```

## Health

| Service | Endpoint |
| --- | --- |
| backend-api | `GET /api/health` |
| scheduler-service | `GET /health` |
| ml-service | `GET /health` |

## Tasks MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/tasks?user_id=1&target_date=2026-06-03` | List non-deleted tasks |
| `POST` | `/tasks` | Create a task |
| `PATCH` | `/tasks/{task_id}` | Update task fields or status |
| `POST` | `/tasks/{task_id}/reopen` | Reopen a completed task |
| `DELETE` | `/tasks/{task_id}` | Soft delete a task |

Create task example:

```json
{
  "user_id": 1,
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
| `GET` | `/fixed-events?user_id=1&target_date=2026-06-03` | List fixed events |
| `POST` | `/fixed-events` | Create a fixed event |

Create fixed event example:

```json
{
  "user_id": 1,
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
| `GET` | `/schedules/latest?user_id=1&target_date=2026-06-03` | Load the latest persisted generated schedule |

Request example:

```json
{
  "user_id": 1,
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
      "score": 72.5
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
- `GET /schedules/latest` returns the latest generated schedule for the given `user_id` and `target_date`.
- If no saved schedule exists, `GET /schedules/latest` returns `404`.

## Execution Logs MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/task-execution-logs?user_id=1&target_date=2026-06-03` | List execution events |
| `POST` | `/tasks/{task_id}/execution/start` | Mark task as in progress |
| `POST` | `/tasks/{task_id}/execution/pause` | Pause an in-progress task |
| `POST` | `/tasks/{task_id}/execution/complete` | Complete a task and close any active interval |
| `POST` | `/tasks/{task_id}/execution/skip` | Skip a task |

Execution event request:

```json
{
  "user_id": 1,
  "occurred_at": "2026-06-03T09:00:00"
}
```

`occurred_at` is optional. When omitted, backend-api uses server time.

## Daily Analytics MVP

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/analytics/daily?user_id=1&target_date=2026-06-03` | Daily execution summary |

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
| `GET` | `/ml/duration-predictions?user_id=1&target_date=2026-06-03` | Predict task duration for dashboard and scheduler |

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

Expected local artifact response:

```json
{
  "model_name": "local-duration-regressor",
  "model_version": "0.1.0",
  "source": "local-artifact"
}
```

## Current Data Store

Docker Compose runs backend-api with `DATA_STORE=mysql`, backed by the `mysql:8.4` service and the `ordostack` database. The persisted MVP tables are `tasks`, `fixed_events`, `execution_logs`, `schedule_runs`, and `schedule_items`.

Local pytest runs use the in-memory seeded repository by default, so tests do not require a running database.

MySQL host access:

```text
localhost:3307 -> mysql container port 3306
```

Generated schedules are persisted after `POST /api/schedules/generate`.
