# OrdoStack

OrdoStack is an AI daily planning MVP for task capture, protected calendar blocks, persisted generated schedules, manual schedule control, execution analytics, local duration prediction, and MySQL-backed persistence.

This version is a local Customer Demo MVP: it implements task/fixed-event APIs, recurring fixed event expansion, schedule locking and manual adjustment, reusable schedule templates, scheduler-service MVP, persisted generated schedules, Markdown/CSV/PDF export, execution logs, daily analytics, completion forecast, local ML duration prediction, local model registry, duration feedback export, MySQL persistence in Docker, Alembic baseline migrations, a React dashboard, English / Traditional Chinese dashboard locale support, demo reset, local auth foundation, user-scoped planner APIs, deployment baseline docs, observability baseline, backup/restore drill baseline, local E2E smoke verification, browser smoke CI, visual regression script, a11y static audit, and security audit script. Production-grade auth hardening, ClearML agent execution, mobile app implementation, hosted monitoring, and AWS deployment are not implemented yet.

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

Readiness endpoints:

- backend-api: http://localhost:8000/api/ready
- scheduler-service: http://localhost:8100/ready
- ml-service: http://localhost:8200/ready

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

Covered in Issue 18 MVP:

- Demo-only reset API for the bundled demo user.
- Dashboard Reset demo control with confirmation.
- Backend test coverage for restoring seeded demo data.

Covered in Issue 19 MVP:

- Local E2E smoke script for Docker Compose demo verification.
- Smoke coverage for health, dashboard HTML, task edit, fixed event edit, schedule generation, and schedule history.

Covered in Issue 20 MVP:

- Project specification refreshed to the Customer Demo MVP baseline.
- Architecture documentation updated for current service boundaries and data flow.
- Demo script, release process, QA plan, README, changelog, and development log aligned to version `0.19.0`.

Covered in Issue 21 MVP:

- Dashboard task filters for status, category, and focus requirement.
- Dashboard task sorting by priority, deadline, estimate, or status.
- Active filter count and reset action for customer demo triage.

Covered in Issue 22 MVP:

- Schedule history titles for generated plans.
- Dashboard rename and soft delete controls for schedule history.
- backend-api schedule history rename/delete endpoints.
- Alembic migration for schedule history action fields.

Covered in Issue 23 MVP:

- Schedule history diff endpoint for comparing generated runs.
- Dashboard Compare previous action.
- Compact diff summary for added, removed, changed, and minute delta.

Covered in Issue 24 MVP:

- Schedule history export endpoint for Markdown and CSV.
- Dashboard Export MD action for selected generated plans.
- Backend tests for export filename and content.

Covered in Issue 25 MVP:

- Browser smoke script that captures a dashboard PNG screenshot with headless Edge or Chrome.
- E2E smoke coverage for schedule rename, diff, and export APIs.
- Generated browser smoke artifacts ignored from Git.

Covered in Issue 26 MVP:

- PM project status report.
- Documentation baseline corrected from Issue 20 to Issue 26.
- Migration expectation corrected to Alembic revision `20260604_0002`.

Covered in Issue 27 MVP:

- Backend runtime configuration validation.
- Shared configuration parser for backend runtime, Alembic, MySQL, scheduler URL, and ML URL.
- Expanded `.env.example` and environment configuration documentation.
- Explicit local environment setting in Docker Compose.

Covered in Issue 28 MVP:

- Local user registration, login, and current-user APIs.
- PBKDF2 password hashing and HMAC bearer tokens without external paid services.
- Seeded demo auth account: `demo@ordostack.local` / `ordostack-demo`.
- MySQL `users` table through Alembic revision `20260604_0003`.
- Dashboard account controls for demo login, register, login, and sign out.

Covered in Issue 29 MVP:

- Core planner APIs use the authenticated bearer-token user instead of implicit `user_id=1`.
- Tasks, fixed events, execution logs, analytics, predictions, and schedule history are scoped to `current_user.id`.
- Cross-user tests cover tasks, fixed events, execution events, and schedule history export.
- Dashboard and E2E smoke script authenticate with the demo account before planner API calls.

Covered in Issue 30 MVP:

- Production environment template with blank secret values.
- Nginx reverse-proxy skeleton for future single-node deployment.
- Deployment guide with account requirements, HTTPS plan, validation commands, and hosted smoke checklist.
- No AWS resources or external accounts are required for this issue.

Covered in Issue 31 MVP:

- `X-Request-ID` propagation for backend-api, scheduler-service, and ml-service.
- Structured JSON request logs that exclude bodies, query strings, auth headers, cookies, and secrets.
- Readiness endpoints separate from health endpoints.
- Local observability runbook and QA checks.
- No external observability account or paid monitoring API is required for this issue.

Covered in Issue 32 MVP:

- Local MySQL backup scripts for Windows PowerShell and Linux / WSL.
- Backup verification scripts that reject empty files and destructive SQL statements.
- Restore drill documentation that targets temporary databases only.
- Generated backup files are written under ignored `artifacts/backups`.
- No cloud backup account, paid API, or automatic destructive restore command is required for this issue.

Covered in Issue 33 MVP:

- Dashboard language switcher.
- English remains the default language.
- Traditional Chinese UI copy for the main dashboard workflow.
- Selected language persists in local storage.
- User-entered task and event content is not translated.

Covered in Issues 34-45 MVP:

- Schedule item lock/unlock and manual `-15/+15` dashboard adjustment controls.
- Locked generated items are preserved during later schedule generation.
- Manual schedule adjustment validates conflicts against fixed event blocks.
- Weekly recurring fixed events expand into dated fixed event rows.
- Named schedule templates store reusable planning settings.
- Markdown, CSV, and local PDF schedule export are available without paid APIs.
- Dashboard a11y static audit and select focus-visible coverage are included.
- ClearML is documented as disabled-by-default local tracking only; no account is required.
- ML service has a local JSON model registry abstraction and `/model/registry`.
- Backend can export completed-task duration feedback CSV for local training review.
- Completion forecast endpoint estimates likely daily completion from execution state.
- GitHub Actions includes a non-Docker browser smoke job with screenshot artifact upload.
- Visual regression and security audit scripts are available for local QA.
- Docker implementation changes are intentionally deferred to the final deployment phase.

Not covered yet:

- Production ML / DL model registry.
- Hosted model registry and ClearML agent execution.
- Mobile app implementation.
- AWS deployment.
- Production-grade auth hardening and authorization.
- Hosted monitoring, alerting, metrics backend, and tracing backend.
- Encrypted off-host backups, scheduled backup jobs, and production restore automation.

## No Secrets Policy

Do not commit `.env`, API keys, ClearML credentials, AWS credentials, database passwords, or private tokens.

## QA MVP

Manual QA instructions are in [docs/qa-mvp.md](docs/qa-mvp.md).

Non-Docker local QA scripts:

```powershell
python scripts\a11y_static_audit.py
python scripts\security_audit.py --root .
python scripts\visual_regression.py --baseline artifacts\visual-baseline\dashboard.png --candidate artifacts\browser-smoke\dashboard.png --threshold 0.01
```

Local E2E smoke after Docker Compose is running:

```powershell
python scripts\e2e_smoke.py
```

Local browser smoke after Docker Compose is running and Edge or Chrome is installed:

```powershell
python scripts\browser_smoke.py
```

## Development Process

- Branching guide: [docs/branching-strategy.md](docs/branching-strategy.md)
- Release process: [docs/release-process.md](docs/release-process.md)
- Version history: [CHANGELOG.md](CHANGELOG.md)
- PM status report: [docs/project-status-report.md](docs/project-status-report.md)
- Environment configuration: [docs/environment.md](docs/environment.md)
- Observability baseline: [docs/observability.md](docs/observability.md)
- Backup and restore baseline: [docs/backup-restore.md](docs/backup-restore.md)
