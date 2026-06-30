# OrdoStack

OrdoStack is a local-first daily planner. It combines tasks, fixed events, execution logs, schedule generation, and duration prediction into one workflow: plan the day, adjust the schedule, run the work, then compare estimates with reality.

The repository is currently a Customer Demo MVP / Technical Preview. It runs locally with Docker Compose and does not use paid APIs.

## Problem

Most planning tools keep a list. A list is useful, but it does not answer the harder questions:

- Where does this task fit around meetings or fixed commitments?
- Which tasks should fit into the remaining day?
- How far off were the original estimates?
- Can the generated plan be saved, edited, compared, and exported?

OrdoStack focuses on that loop for one day at a time.

## What Works Today

- Local account registration, demo login, bearer-token auth, password policy, and login lockout.
- Date-scoped tasks with create, edit, status changes, reopen, and soft delete.
- Fixed events with create, edit, soft delete, and weekly recurrence expansion.
- Schedule generation through a dedicated scheduler service.
- Schedule history with rename, compare, export, lock, and manual time adjustment.
- Local schedule exports in Markdown, CSV, and PDF.
- Execution logs and daily analytics: actual minutes, estimate drift, completion rate, focus minutes, and forecast.
- Local duration prediction through `ml-service` using a JSON artifact or heuristic fallback.
- English UI by default, with Traditional Chinese available in the dashboard.
- Docker Compose runtime with MySQL persistence.
- Local QA gates for tests, build, security, accessibility, backup policy, visual regression, and smoke checks.

## Quick Start

Requirements:

- Docker Desktop with Docker Compose.
- Python 3.11+ for local QA scripts.
- Node.js 20+ only when running `web-dashboard` outside Docker.

Windows PowerShell:

```powershell
git clone https://github.com/cdexswzaq0110/Ordostack.git
cd Ordostack
docker compose up --build -d
```

Linux / WSL:

```bash
git clone https://github.com/cdexswzaq0110/Ordostack.git
cd Ordostack
docker compose up --build -d
```

Open:

```text
http://localhost:5173
```

Demo account:

```text
demo@ordostack.local
ordostack-demo
```

Stop the stack:

```powershell
docker compose down
```

## Health Checks

| Service | URL |
| --- | --- |
| Dashboard | `http://localhost:5173` |
| backend-api | `http://localhost:8000/api/health` |
| scheduler-service | `http://localhost:8100/health` |
| ml-service | `http://localhost:8200/health` |

Readiness:

| Service | URL |
| --- | --- |
| backend-api | `http://localhost:8000/api/ready` |
| scheduler-service | `http://localhost:8100/ready` |
| ml-service | `http://localhost:8200/ready` |

## Architecture

```text
Browser
  |
  v
web-dashboard :5173
  |
  v
backend-api :8000
  |-- MySQL :3306 container / :3307 host
  |-- scheduler-service :8100
  `-- ml-service :8200
```

`backend-api` is the product API. It owns authentication, tasks, fixed events, execution logs, analytics, schedule persistence, schedule export, and demo reset.

`scheduler-service` owns scheduling logic. It scores tasks, respects dependencies, selects work that fits into available time, builds free slots around fixed events, and returns timeline items.

`ml-service` owns duration prediction. It uses a local JSON model artifact when available and falls back to a deterministic heuristic when the artifact is missing.

`mysql` stores local Docker data: users, tasks, fixed events, execution logs, schedule runs, schedule items, and schedule templates.

## Clean Check

Run before committing:

```powershell
python scripts\ponytail.py --include-compose-config
```

The gate runs documentation completeness, service tests, dashboard build, security audit, accessibility audit, backup policy audit, beta readiness check, translation coverage, visual regression when artifacts exist, Git whitespace checks, and Docker Compose config validation.

For runtime verification, run:

```powershell
docker compose up --build -d
python scripts\e2e_smoke.py
python scripts\browser_smoke.py
```

## Documentation Map

Start here:

| Topic | File |
| --- | --- |
| Product scope | [ORDOSTACK_PROJECT_SPEC.md](ORDOSTACK_PROJECT_SPEC.md) |
| System architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| API behavior | [docs/api.md](docs/api.md) |
| QA workflow | [docs/qa-mvp.md](docs/qa-mvp.md) |
| Release process | [docs/release-process.md](docs/release-process.md) |
| Environment variables | [docs/environment.md](docs/environment.md) |
| Backup and restore | [docs/backup-restore.md](docs/backup-restore.md) |
| Product roadmap | [docs/product-roadmap.md](docs/product-roadmap.md) |
| AWS deployment plan | [docs/aws-deployment-plan.md](docs/aws-deployment-plan.md) |
| ClearML MLOps plan | [docs/mlops-clearml-plan.md](docs/mlops-clearml-plan.md) |
| Security checklist | [docs/security-checklist.md](docs/security-checklist.md) |

Repository maintenance:

| Topic | File |
| --- | --- |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Support | [SUPPORT.md](SUPPORT.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

The remaining files under `docs/` are supporting runbooks and historical notes. They are useful for QA and release review, but not required for a first read.

## Current Limits

- Not a hosted SaaS launch.
- No AWS resources, DNS, TLS certificate, paid API, or external monitoring vendor is provisioned by this repository.
- The mobile app folder is a placeholder, not a shipped mobile client.
- ClearML and production model governance are documented but not operational.
- Production secrets must stay outside Git.
