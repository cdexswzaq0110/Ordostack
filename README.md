# OrdoStack

OrdoStack is an AI daily planning MVP for task capture, protected calendar blocks, persisted generated schedules, execution analytics, local duration prediction, and MySQL-backed persistence.

This version is intentionally small: it implements task/fixed-event APIs, a scheduler-service MVP, persisted generated schedules, execution logs, daily analytics, local ML duration prediction, MySQL persistence in Docker, and a React dashboard. Authentication, production migrations, ClearML agent execution, and AWS deployment are not implemented yet.

## Quick Start

### Windows PowerShell

```powershell
docker compose up --build
```

### Linux / WSL

```bash
docker compose up --build
```

## Health Checks

After Docker Compose is running:

- backend-api: http://localhost:8000/api/health
- scheduler-service: http://localhost:8100/health
- ml-service: http://localhost:8200/health
- web-dashboard: http://localhost:5173

Expected backend health response:

```json
{
  "status": "ok"
}
```

## Services

| Service | Port | Purpose |
| --- | ---: | --- |
| backend-api | 8000 | Main FastAPI API entrypoint |
| scheduler-service | 8100 | Scheduling algorithm service |
| ml-service | 8200 | ML prediction service skeleton |
| web-dashboard | 5173 | React / Vite dashboard |
| mysql | 3307 -> 3306 | Local MySQL persistence for backend-api |

## Repository Structure

```text
.
|-- backend-api/
|-- scheduler-service/
|-- ml-service/
|-- web-dashboard/
|-- mobile-app/
|-- database/
|-- clearml/
|-- scripts/
|-- docs/
|-- .github/
|-- README.md
|-- ORDOSTACK_PROJECT_SPEC.md
|-- AI_RULEBOOK.md
|-- DEVELOPMENT_RULEBOOK.md
|-- ARCHITECTURE.md
|-- docker-compose.yml
|-- docker-compose.prod.yml
`-- .env.example
```

## Current Scope

Covered in Issue 1:

- Repository structure.
- Core documentation files.
- Docker Compose skeleton.
- FastAPI service skeletons.
- Health endpoints.
- Vite dashboard landing page.

Covered in Issue 2 MVP:

- Task list, create, update status, reopen, and soft delete APIs.
- Fixed event list and create APIs.
- Seeded demo user data through an in-memory repository.
- Dashboard reads task and fixed event data from backend-api.
- Dashboard supports creating tasks, completing/reopening/deleting tasks, and creating fixed events.

Covered in Issue 3 MVP:

- scheduler-service `POST /schedule/generate`.
- backend-api `POST /api/schedules/generate`.
- Priority scoring, topological sort, knapsack capacity selection, priority queue ordering, and fixed-event slot building.
- Dashboard `Generate Plan` action shows generated schedule and algorithm summary.

Covered in Issue 4 MVP:

- Task execution start, pause, complete, and skip endpoints.
- Execution log listing API.
- Daily analytics API for actual minutes, estimate drift, and completion rate.
- Dashboard execution controls and actual-time metrics.

Covered in Issue 5 MVP:

- ml-service `POST /duration/predict`.
- backend-api `GET /api/ml/duration-predictions`.
- Schedule generation uses ML predicted minutes when available.
- Dashboard task rows show estimated, predicted, and actual minutes.

Covered in Issue 6 MVP:

- Local duration training sample dataset.
- Training script that writes model and metrics JSON artifacts.
- ml-service loads `local-duration-regressor` from the bundled artifact.
- ml-service falls back to `heuristic-duration` if the artifact is missing.

Covered in Issue 7 MVP:

- Docker Compose MySQL service for local persistence.
- backend-api store selector with `DATA_STORE=mysql` in Docker.
- Persisted `tasks`, `fixed_events`, and `execution_logs`.
- Automatic schema bootstrap for local MVP development.
- MySQL host port is `3307` because local `3306` may already be occupied.

Covered in Issue 8 MVP:

- Persisted generated schedule runs and schedule items.
- backend-api `GET /api/schedules/latest`.
- Dashboard loads the latest saved schedule on startup.
- Version history and suggested commit notes are recorded in `CHANGELOG.md` and `docs/development-log.md`.

Covered in Issue 9 MVP:

- Alembic migration baseline for the current MySQL schema.
- backend-api runs `alembic upgrade head` before starting in Docker.
- Existing automatic schema bootstrap remains as a local compatibility fallback.
- Destructive downgrade is intentionally not implemented.

Covered in Issue 10 MVP:

- GitHub Actions CI workflow for backend-api, scheduler-service, ml-service, web-dashboard, and Docker Compose config.
- Pull request template with verification checklist.
- Branching strategy document for feature, fix, chore, and docs branches.
- Development rulebook updated with branch and CI expectations.

Covered in Issue 11 MVP:

- `VERSION` file for release tracking.
- Release process documentation.
- Baseline commit checklist for future branch-based development.

Covered in Issue 12 MVP:

- Dashboard selected date state.
- Previous day and next day navigation.
- Tasks, fixed events, analytics, duration predictions, and latest schedule reload by selected date.
- New task and fixed event forms create records on the currently selected date.

Covered in Issue 13 MVP:

- Dashboard inline task editing.
- Task create and edit flows share the same field component.
- Task form validation runs before create and update requests.
- Edited tasks are saved through `PATCH /api/tasks/{task_id}`.

Covered in Issue 14 MVP:

- Fixed event update and soft delete APIs.
- Dashboard inline fixed event editing.
- Fixed event delete controls use soft delete.
- Fixed event form validation for title, type, and `HH:MM` time ranges.

Covered in Issue 15 MVP:

- Dashboard date picker for arbitrary date selection.
- Today shortcut in the date control.
- Open create/edit forms close when changing date.

Covered in Issue 16 MVP:

- `GET /api/schedules/history` for recent generated plans.
- Dashboard schedule history panel.
- Users can switch the timeline to a previous generated plan.

Covered in Issue 17 MVP:

- Dashboard empty states for timeline, schedule history, and fixed events.
- Retry action in the error banner.
- Compact empty-state styling for demo usability.

Not covered yet:

- Production ML / DL model registry.
- ClearML agent execution.
- Mobile app implementation.
- AWS deployment.

## No Secrets Policy

Do not commit `.env`, API keys, ClearML credentials, AWS credentials, database passwords, or private tokens.

## QA MVP

Manual QA instructions are in [docs/qa-mvp.md](docs/qa-mvp.md).

## Development Process

- Branching guide: [docs/branching-strategy.md](docs/branching-strategy.md)
- Release process: [docs/release-process.md](docs/release-process.md)
- Version history: [CHANGELOG.md](CHANGELOG.md)
