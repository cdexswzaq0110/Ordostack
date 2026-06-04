# OrdoStack Project Specification

Source document: `C:\Users\HUANG\Desktop\OrdoStack Project Specification.docx`

This markdown file records the implementation baseline used by Codex for the repository. The project is developed incrementally by issue. As of Issue 20, the repository is a local Customer Demo MVP, not a production launch build.

## Current Baseline

```text
Version: 0.23.0
Stage: Customer Demo MVP
Runtime: Local Docker Compose
Primary UI: web-dashboard
Production readiness: Not ready for public launch
```

## Project Identity

- English name: OrdoStack
- Subtitle: Algorithmic Daily Planning Mobile App with ClearML MLOps
- Chinese name: OrdoStack：演算法每日規劃與 ClearML MLOps 的 AI 行程 App

## One-line Description

OrdoStack is an AI daily planning product that lets users capture tasks and fixed events, generate daily plans with scheduling algorithms, compare estimates with execution data, and use local ML duration prediction to improve planning quality.

## Primary Goals

- Let users create, edit, complete, reopen, skip, and soft-delete daily tasks.
- Let users create, edit, and soft-delete fixed events.
- Generate daily plans automatically without overlapping protected fixed events.
- Track task execution start, pause, completion, and skip events.
- Compare estimated, predicted, and actual task duration.
- Persist tasks, fixed events, execution logs, generated schedule runs, and schedule items in MySQL.
- Predict task duration through the local ML service.
- Keep the scheduling algorithms inside scheduler-service instead of backend routes.
- Provide a professional web dashboard suitable for customer demo review.
- Run locally with Docker Compose and pass repeatable smoke verification.

## Non-goals For Current MVP

- No paid APIs.
- No production authentication or account management.
- No native mobile app implementation yet.
- No app store release.
- No ClearML agent execution yet.
- No production ML / DL model registry yet.
- No DL completion-rate or focus-score service yet.
- No AWS deployment, HTTPS, Nginx production reverse proxy, or production backup plan yet.
- No full Google Calendar two-way sync.
- No payment system.
- No complex permission system.
- No chatbot replacing the scheduling algorithm core.

## Implemented Through Issue 20

| Area | Current implementation |
| --- | --- |
| Repository | Monorepo structure, README, project spec, rulebooks, architecture docs, Docker Compose, CI docs |
| Web dashboard | React / Vite TypeScript dashboard with landing/demo product experience, task filters, and task sorting |
| Tasks | Create, list, edit, status transitions, reopen, soft delete |
| Fixed events | Create, list, edit, soft delete, validation for `HH:MM` time ranges |
| Date navigation | Previous day, next day, native date picker, Today shortcut |
| Scheduler | Daily schedule generation with priority score, topological sort, knapsack selection, priority queue ordering, and fixed-event free-slot building |
| Schedule persistence | Latest generated schedule, recent schedule history, schedule history rename, soft delete, diff, and text export |
| Execution tracking | Start, pause, complete, skip, execution log listing |
| Analytics | Daily actual minutes, estimate delta, completion rate, focus minutes |
| ML duration prediction | Local duration prediction API with bundled training artifact and heuristic fallback |
| Storage | Docker MySQL persistence with Alembic migration baseline and local compatibility bootstrap |
| Demo support | Seeded demo data and demo-only reset control |
| Quality gates | Python service tests, web-dashboard build, Docker Compose config, local E2E smoke script, GitHub Actions baseline |
| Documentation | API docs, QA plan, release process, branching strategy, development log, changelog |

## System Components

| Component | Purpose | Current status |
| --- | --- | --- |
| web-dashboard | React / Vite dashboard for demo and QA | Implemented MVP |
| backend-api | FastAPI gateway for tasks, fixed events, schedules, logs, analytics, ML predictions, and demo reset | Implemented MVP |
| scheduler-service | Scheduling algorithm service | Implemented MVP |
| ml-service | Duration prediction service | Implemented MVP |
| mysql | Local relational persistence for Docker Compose | Implemented MVP |
| mobile-app | Future React Native / Expo mobile client | Not implemented |
| dl-service | Future completion-rate or focus-score prediction service | Not implemented |
| clearml-agent | Future model training worker | Not implemented |
| nginx | Future production reverse proxy | Not implemented |

## Target Tech Stack

| Area | Stack |
| --- | --- |
| Web | React, Vite, TypeScript |
| Backend | Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Scheduler | Python 3.11+, FastAPI, heapq, custom DP and graph algorithms |
| ML | Python, local model artifact, heuristic fallback |
| Future Mobile | React Native, Expo, TypeScript |
| Future DL | PyTorch, pandas, numpy, ClearML SDK |
| Database | MySQL 8.x |
| DevOps | Docker, Docker Compose, GitHub Actions; AWS EC2 in a future phase |

## MVP User Flows

1. User opens `http://localhost:5173`.
2. User reviews daily tasks, protected fixed events, analytics, predictions, and current timeline.
3. User adds or edits task data for the selected date.
4. User adds or edits fixed events for the selected date.
5. User clicks `Generate Plan`.
6. backend-api requests duration predictions, sends planning input to scheduler-service, persists the generated plan, and returns the schedule.
7. User reviews the generated timeline and algorithm summary.
8. User can switch to recent generated plans through schedule history.
9. User can execute tasks and review actual-time analytics.
10. For demos, user can reset bundled demo data after confirming the dashboard prompt.

## API Baseline

Base URL:

```text
http://localhost:8000/api
```

Core endpoint groups:

- Health: `GET /api/health`
- Tasks: `GET /tasks`, `POST /tasks`, `PATCH /tasks/{task_id}`, `DELETE /tasks/{task_id}`, `POST /tasks/{task_id}/reopen`
- Fixed events: `GET /fixed-events`, `POST /fixed-events`, `PATCH /fixed-events/{fixed_event_id}`, `DELETE /fixed-events/{fixed_event_id}`
- Execution logs: `GET /task-execution-logs`, task start / pause / complete / skip endpoints
- Analytics: `GET /analytics/daily`
- Schedules: `POST /schedules/generate`, `GET /schedules/latest`, `GET /schedules/history`
- ML predictions: `GET /ml/duration-predictions`
- Demo: `POST /demo/reset?user_id=1`

Detailed API documentation is maintained in `docs/api.md`.

## Scheduling Algorithm Requirements

The scheduler service owns algorithm logic. Backend routes must not contain scheduling internals.

Implemented algorithms:

- Priority score.
- Topological sort for task dependencies.
- 0/1 knapsack-style capacity selection.
- Priority queue ordering.
- Fixed event free-slot builder.
- Fixed event conflict avoidance.
- Schedule builder orchestration.

Future algorithm work:

- Weighted interval scheduling for richer event conflict scenarios.
- Manual schedule lock / drag-and-drop adjustment.
- Named schedule templates.
- Recurring fixed event expansion.

## Current Data Ownership

| Data | Owner |
| --- | --- |
| Tasks | backend-api store layer, persisted in MySQL for Docker |
| Fixed events | backend-api store layer, persisted in MySQL for Docker |
| Execution logs | backend-api store layer, persisted in MySQL for Docker |
| Generated schedule runs | backend-api store layer, persisted in MySQL for Docker |
| Generated schedule items | backend-api store layer, persisted in MySQL for Docker |
| Scheduling algorithm output | scheduler-service, called by backend-api |
| Duration predictions | ml-service, called by backend-api |
| Demo reset seed | backend-api demo service |

## Quality Gates

Before a release tag:

- backend-api tests pass.
- scheduler-service tests pass.
- ml-service tests pass.
- web-dashboard production build passes.
- `docker compose config` passes.
- `docker compose up --build -d` starts all services.
- Health checks pass:
  - `http://localhost:8000/api/health`
  - `http://localhost:8100/health`
  - `http://localhost:8200/health`
  - `http://localhost:5173`
- `python scripts/e2e_smoke.py` exits with status code `0`.
- Secrets scan finds no committed credentials.

## Remaining Gaps Before Public Launch

- Production authentication, authorization, and user isolation.
- Real onboarding, user settings, timezone handling, and profile data.
- Production-grade migration policy, backup, restore, and data retention.
- Hosted deployment with HTTPS, domain, reverse proxy, observability, and incident playbook.
- Mobile app implementation.
- ClearML experiment tracking, model registry, agent execution, and deployment workflow.
- DL completion-rate / focus-score service.
- Calendar integration and recurring event support.
- Schedule manual editing and named schedule templates.
- Browser-based automated UI regression tests with screenshots.
- PDF export and cloud share links.
- Load, security, and accessibility audits.

## Planned Phases

1. Local Customer Demo MVP: complete through Issue 20.
2. Beta Hardening: auth, user isolation, deployment, observability, backup, a11y, and browser regression tests.
3. MLOps Expansion: ClearML tracking, model registry, scheduled retraining, and model promotion.
4. Intelligence Expansion: DL completion-rate or focus-score service.
5. Mobile Product: React Native / Expo mobile client.
6. Production Launch: cloud deployment, security review, monitoring, support process, and release governance.

## Definition Of Done

A feature is done only when:

- Code is implemented where required.
- Tests exist where meaningful.
- Tests pass.
- Docker can start the affected service.
- API, QA, or README documentation is updated when behavior changes.
- Version history is recorded.
- No secrets are committed.
- No hard-coded credentials are introduced.
