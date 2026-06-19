# OrdoStack

OrdoStack is a local-first daily planning system. It turns tasks, fixed events, estimates, execution logs, and duration predictions into a schedule that can be reviewed, adjusted, saved, and exported.

The current repository is a Customer Demo MVP / Technical Preview. It runs locally with Docker Compose and does not require paid APIs.

## Problem

Most planning tools stop at a list. That leaves three recurring problems:

- A task list does not protect real calendar time.
- Estimates are rarely checked against actual work.
- Generated plans are often temporary suggestions, not saved schedules people can edit, audit, or export.

OrdoStack closes that loop for a single-day planning workflow: capture work, protect fixed time, generate a schedule, adjust it, execute it, and compare the result with the estimate.

## Features

- Task workflow: create, edit, complete, pause, skip, reopen, and soft-delete tasks.
- Protected time: create fixed events and expand weekly recurring blocks.
- Schedule generation: build a date-scoped plan through `scheduler-service`.
- Manual control: lock generated schedule items and move them in 15-minute steps.
- Schedule history: persist generated runs, rename them, compare them, and reload older plans.
- Export: download schedules as Markdown, CSV, or local PDF.
- Analytics: track actual time, completion rate, estimate drift, focus minutes, and completion forecast.
- Local ML: predict task duration through `ml-service` with a local model artifact or heuristic fallback.
- Auth: local registration/login, bearer tokens, password policy, token expiry, and failed-login rate limiting.
- Language: English by default, with Traditional Chinese dashboard support.
- QA and ops: health/readiness endpoints, Docker Compose, tests, security audit, a11y audit, backup policy audit, and a compact clean gate.

## Quick Start

Requirements:

- Docker Desktop with Docker Compose.
- Python 3.11+ for local QA scripts.
- Node.js 20+ only if you run the dashboard outside Docker.

Windows PowerShell:

```powershell
git clone <your-repo-url>
cd OrdoStack
docker compose up --build -d
```

Linux / WSL:

```bash
git clone <your-repo-url>
cd OrdoStack
docker compose up --build -d
```

Open:

```text
http://localhost:5173
```

Demo login:

```text
demo@ordostack.local
ordostack-demo
```

Stop the stack:

```powershell
docker compose down
```

## Health Checks

After Docker Compose is running:

| Service | URL |
| --- | --- |
| Dashboard | `http://localhost:5173` |
| backend-api | `http://localhost:8000/api/health` |
| scheduler-service | `http://localhost:8100/health` |
| ml-service | `http://localhost:8200/health` |

Readiness endpoints:

| Service | URL |
| --- | --- |
| backend-api | `http://localhost:8000/api/ready` |
| scheduler-service | `http://localhost:8100/ready` |
| ml-service | `http://localhost:8200/ready` |

## Clean Check

Run this before final delivery or commit:

```powershell
python scripts\ponytail.py
```

When Docker is available:

```powershell
python scripts\ponytail.py --include-compose-config
```

The clean gate runs documentation completeness, service tests, release QA checks, security/a11y audits, translation coverage, visual regression when artifacts exist, and Git whitespace checks.

## Architecture

```text
web-dashboard -> backend-api -> MySQL
                         |-> scheduler-service
                         |-> ml-service
```

| Service | Port | Purpose |
| --- | ---: | --- |
| `web-dashboard` | 5173 | React / Vite dashboard |
| `backend-api` | 8000 | Main FastAPI API |
| `scheduler-service` | 8100 | Scheduling algorithms |
| `ml-service` | 8200 | Duration prediction |
| `mysql` | 3307 -> 3306 | Local persistence |

## Documentation Map

| Topic | File |
| --- | --- |
| Product specification | [ORDOSTACK_PROJECT_SPEC.md](ORDOSTACK_PROJECT_SPEC.md) |
| System design | [ARCHITECTURE.md](ARCHITECTURE.md) |
| System analysis | [docs/system-analysis.md](docs/system-analysis.md) |
| API | [docs/api.md](docs/api.md) |
| QA plan | [docs/qa-mvp.md](docs/qa-mvp.md) |
| Documentation status | [docs/documentation-completeness.md](docs/documentation-completeness.md) |
| Release process | [docs/release-process.md](docs/release-process.md) |
| Deployment planning | [docs/deployment.md](docs/deployment.md) |
| Environment variables | [docs/environment.md](docs/environment.md) |
| Backup and restore | [docs/backup-restore.md](docs/backup-restore.md) |
| Observability | [docs/observability.md](docs/observability.md) |
| Accessibility QA | [docs/accessibility-qa.md](docs/accessibility-qa.md) |
| Beta readiness | [docs/beta-readiness.md](docs/beta-readiness.md) |

## GitHub Project Files

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE)

## Current Limits

- Not a hosted public SaaS launch.
- No AWS resources, domain, TLS certificate, or paid API is provisioned by this repo.
- Mobile app, ClearML agent execution, external calendar sync, and production model governance are not implemented.
- Production secrets must stay outside Git.
