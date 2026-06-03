# OrdoStack Project Specification

Source document: `C:\Users\HUANG\Desktop\OrdoStack Project Specification.docx`

This markdown file records the implementation baseline used by Codex for the repository. The project is developed incrementally by issue; Issue 1 only initializes the runnable skeleton.

## Project Identity

- English name: OrdoStack
- Subtitle: Algorithmic Daily Planning Mobile App with ClearML MLOps
- Chinese name: OrdoStack: 結合排程演算法與 ClearML MLOps 的 AI 日常規劃手機 App

## One-line Description

OrdoStack is an AI daily planning mobile app that uses scheduling algorithms to generate daily plans, ML / DL models to predict task duration and completion rate, and ClearML to manage MLOps workflows.

## Primary Goals

- Let users create daily tasks and fixed events.
- Generate daily plans automatically.
- Track task execution start, pause, completion, and skip events.
- Compare estimated time and actual time.
- Predict task duration with ML models.
- Predict daily completion rate or focus score with DL models.
- Track training runs, metrics, and artifacts through ClearML.
- Run locally with Docker Compose.
- Deploy a demo version to AWS EC2 in later phases.

## Non-goals For MVP

- No social features.
- No chatbot.
- No payment system.
- No full Google Calendar two-way sync.
- No native app store release.
- No complex permission system.
- No black-box API replacing the core scheduling algorithms.
- No all-at-once implementation.

## System Components

| Component | Purpose |
| --- | --- |
| mobile-app | React Native / Expo mobile client |
| web-dashboard | React / Vite analytics and demo dashboard |
| backend-api | FastAPI service for tasks, schedules, logs, analytics |
| scheduler-service | Scheduling algorithms and schedule builder |
| ml-service | Task duration prediction |
| dl-service | Completion rate or focus score prediction in a later phase |
| mysql | Main relational database in a later phase |
| clearml-agent | Training worker in a later phase |
| nginx | Production reverse proxy in a later phase |

## Target Tech Stack

| Area | Stack |
| --- | --- |
| Mobile | React Native, Expo, TypeScript |
| Web | React, Vite, TypeScript |
| Backend | Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Scheduler | Python 3.11+, FastAPI, heapq, custom DP and graph algorithms |
| ML | scikit-learn, pandas, numpy, joblib, ClearML SDK |
| DL | PyTorch, pandas, numpy, ClearML SDK |
| Database | MySQL 8.x |
| DevOps | Docker, Docker Compose, GitHub Actions, AWS EC2 |

## Issue 1 Scope

Acceptance criteria:

- `docker compose up --build` succeeds.
- `backend-api` returns ok at `http://localhost:8000/api/health`.
- `scheduler-service` returns ok at `http://localhost:8100/health`.
- `ml-service` returns ok at `http://localhost:8200/health`.
- `web-dashboard` is visible at `http://localhost:5173`.
- README contains quick start instructions.
- No secrets are committed.

## Planned Phases

1. Project skeleton.
2. Tasks and fixed events.
3. Scheduling algorithms.
4. Task execution logs and analytics.
5. ML duration prediction and ClearML tracking.
6. Optional DL completion prediction.
7. Web dashboard completion, AWS deployment, CI/CD.

## Scheduling Algorithm Requirements

The scheduler service owns algorithm logic. Backend routes must not contain scheduling internals.

Algorithms planned for later phases:

- Priority score.
- Priority queue scheduling.
- 0/1 knapsack dynamic programming.
- Fixed event conflict detection.
- Weighted interval scheduling.
- Topological sort for task dependencies.
- Schedule builder orchestration.

## API Baseline

Issue 1 only exposes health endpoints:

- `GET /api/health` on backend-api.
- `GET /health` on scheduler-service.
- `GET /health` on ml-service.

Future backend base URL:

```text
http://localhost:8000/api
```

## Definition Of Done

A feature is done only when:

- Code is implemented.
- Tests exist where meaningful.
- Tests pass.
- Docker can start the affected service.
- API or README documentation is updated.
- No secrets are committed.
- No hard-coded credentials are introduced.

