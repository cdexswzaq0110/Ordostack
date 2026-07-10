# OrdoStack Project Specification

This file records the current product baseline for the repository. The original project brief lives outside the repo at `C:\Users\HUANG\Desktop\OrdoStack Project Specification.docx`.

## Current Baseline

```text
Version: 0.54.0
Stage: Local Private Beta Candidate
Runtime: Docker Compose local stack
Primary UI: web-dashboard
Public launch readiness: Not ready
```

OrdoStack can be used for controlled local beta evaluation. It is not yet a hosted production product.

## Product Identity

- Name: OrdoStack
- Category: Daily planning and schedule optimization
- Core idea: turn tasks, fixed events, estimates, and execution data into a usable daily schedule.

## Primary Goals

- Create and maintain daily tasks.
- Protect fixed events from schedule conflicts.
- Generate a practical daily plan.
- Let users lock and manually adjust generated schedule items.
- Persist schedule history so generated plans are not throwaway output.
- Track actual execution time and compare it with estimates.
- Use local duration prediction to improve planning quality.
- Keep the scheduling algorithm in `scheduler-service`.
- Keep duration prediction in `ml-service`.
- Run locally without paid APIs.

## Non-Goals For The Current MVP

- No hosted SaaS launch.
- No AWS account, DNS, TLS certificate, or paid API setup.
- No app store release.
- No production mobile client.
- No ClearML agent execution.
- No hosted production model registry.
- No payment system.
- No enterprise permission model.
- No chatbot replacing the scheduling engine.

## System Components

| Component | Purpose | Current status |
| --- | --- | --- |
| `web-dashboard` | React / Vite dashboard | Implemented MVP |
| `backend-api` | Main FastAPI product API | Implemented MVP |
| `scheduler-service` | Schedule generation algorithms | Implemented MVP |
| `ml-service` | Local duration prediction | Implemented MVP |
| `mysql` | Docker persistence | Implemented MVP |
| `mobile-app` | Future mobile client | Placeholder only |
| `clearml` | Optional experiment tracking for the training loop | Implemented, disabled by default; server/agent remain future work |

## Implemented Scope

| Area | Current implementation |
| --- | --- |
| Auth | Register, login, current user, bearer token, password policy, failed-login lockout, demo account |
| Tasks | Create, list, edit, status changes, reopen, soft delete |
| Fixed events | Create, list, edit, soft delete, weekly recurrence expansion |
| Schedule generation | Priority scoring, dependency ordering, capacity selection, free-slot building, fixed-event conflict avoidance |
| Schedule history | Save generated runs, reload, rename, soft delete, compare, lock items, move items |
| Export | Markdown, CSV, local PDF |
| Analytics | Actual minutes, estimate drift, completion rate, focus minutes, completion forecast |
| ML | Local duration prediction, JSON artifact, heuristic fallback, model metadata, feedback export, holdout-evaluated retraining, metrics-gated promotion into a local registry, hot model reload, optional ClearML tracking |
| Storage | MySQL in Docker, memory store in tests |
| Observability | Request IDs, structured request logs, health and readiness endpoints |
| Backup | Local MySQL backup script and verification script |
| QA | Unit tests, E2E smoke, browser smoke, visual regression, a11y audit, security audit, beta readiness check |
| Language | English default and Traditional Chinese dashboard copy |

## Main User Flow

1. User opens `http://localhost:5173`.
2. User signs in with the demo account or registers locally.
3. User reviews tasks, fixed events, analytics, predictions, and current schedule.
4. User adds or edits tasks and fixed events for the selected date.
5. User clicks Generate plan.
6. `backend-api` calls `ml-service` for duration prediction.
7. `backend-api` calls `scheduler-service` for schedule generation.
8. `backend-api` saves the generated schedule.
9. User reviews, locks, moves, compares, or exports the plan.
10. User tracks execution and reviews actual-time analytics.

## API Baseline

Base URL:

```text
http://localhost:8000/api
```

Core groups:

- Health: `GET /api/health`, `GET /api/ready`
- Auth: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Tasks: `GET /tasks`, `POST /tasks`, `PATCH /tasks/{task_id}`, `DELETE /tasks/{task_id}`
- Fixed events: `GET /fixed-events`, `POST /fixed-events`, `PATCH /fixed-events/{fixed_event_id}`, `DELETE /fixed-events/{fixed_event_id}`
- Execution: task start, pause, complete, skip, and execution log listing
- Analytics: `GET /analytics/daily`
- Schedules: generate, latest, history, diff, export, lock, manual move
- ML: `GET /ml/duration-predictions`, `GET /ml/duration-feedback`
- Demo: `POST /demo/reset`

Detailed endpoint behavior is in [docs/api.md](docs/api.md).

## Quality Gates

Minimum local gate:

```powershell
python scripts\ponytail.py --include-compose-config
```

Runtime gate:

```powershell
docker compose up --build -d
python scripts\e2e_smoke.py
python scripts\browser_smoke.py
```

Expected runtime checks:

- `http://localhost:5173` returns the dashboard.
- `http://localhost:8000/api/health` returns `ok`.
- `http://localhost:8000/api/ready` returns `ready`.
- `http://localhost:8100/health` returns `ok`.
- `http://localhost:8200/health` returns `ok`.
- E2E smoke can create and edit tasks, create and edit fixed events, generate schedules, rename history, compare schedules, and export schedules.

## Definition Of Done

A change is done when:

- the behavior is implemented,
- validation and data-loss checks are preserved,
- one meaningful runnable check exists for non-trivial logic,
- relevant docs are updated,
- version history is recorded,
- no secrets are committed,
- local clean gates pass.

Any Docker, database, migration, or deployment change also requires `docker compose up --build` and service health/log verification.

## Remaining Gaps Before Public Launch

- Hosted deployment with DNS, TLS, production secrets, and monitored infrastructure.
- Off-host backup storage and restore procedure for production.
- Production-grade auth sessions, account recovery, and admin support.
- Production ML model registry and promotion workflow.
- ClearML agent execution.
- Mobile app implementation.
- External calendar integration.
- Load testing and security review.
