# Architecture

OrdoStack is a small service-oriented local application. The dashboard talks to one backend API. The backend owns product data and calls two internal services: one for scheduling and one for duration prediction.

```mermaid
flowchart LR
  browser["Browser"] --> dashboard["web-dashboard\nReact / Vite\n:5173"]
  dashboard --> api["backend-api\nFastAPI\n:8000"]
  api --> mysql["MySQL\n:3306 container\n:3307 host"]
  api --> scheduler["scheduler-service\nFastAPI\n:8100"]
  api --> ml["ml-service\nFastAPI\n:8200"]
```

## Runtime Boundaries

| Component | Responsibility |
| --- | --- |
| `web-dashboard` | Browser UI, task forms, schedule review, history controls, export actions, language switcher |
| `backend-api` | Auth, task data, fixed events, execution logs, analytics, schedule persistence, exports, demo reset |
| `scheduler-service` | Scheduling algorithms and timeline generation |
| `ml-service` | Local duration prediction and model metadata |
| `mysql` | Docker persistence for product data |

The backend is the only public product API. The dashboard does not call MySQL, scheduler-service, or ml-service directly.

## Repository Structure

```text
web-dashboard/       Browser client
backend-api/         Public product API and persistence owner
scheduler-service/   Stateless scheduling engine
ml-service/          Stateless local duration prediction
database/            Schema reference
scripts/             QA, smoke, backup, and verification commands
infra/               Reverse-proxy configuration
docs/                Product, operations, security, and release documents
```

There is no shared application framework between services. Each service owns a small HTTP boundary and can be tested independently.

## Data Flow

1. The dashboard loads tasks, fixed events, analytics, duration predictions, latest schedule, and schedule history for the selected date.
2. `backend-api` reads and writes through its repository layer.
3. In Docker, the repository layer uses MySQL. In tests, it uses the in-memory store.
4. When the user generates a plan, `backend-api` requests duration predictions from `ml-service`.
5. `backend-api` sends tasks, fixed events, and planning settings to `scheduler-service`.
6. `scheduler-service` returns schedule items and an algorithm summary.
7. `backend-api` saves the generated run and schedule items.
8. The dashboard can reload, rename, compare, lock, move, or export saved schedule runs.

## Scheduling

The scheduler service keeps planning logic out of backend routes. Current algorithms are intentionally small and readable:

- priority scoring for task value,
- topological sorting for dependencies,
- capacity selection for tasks that fit available time,
- priority-queue ordering,
- free-slot construction around fixed events,
- locked-item preservation for manually adjusted schedules.

The scheduler returns a generated timeline. It does not persist data.

## Duration Prediction

`ml-service` predicts task duration from:

- estimated minutes,
- category,
- priority,
- difficulty,
- focus requirement,
- actual minutes when available.

The service first looks for the model referenced by the local JSON registry (`model_registry.json`), then the default artifact, and falls back to a deterministic heuristic when neither exists. No paid API or hosted model endpoint is required.

The retraining loop is local and metrics-gated:

1. `scripts/export_duration_feedback.py` pulls completed-task feedback from `backend-api`.
2. `ml-service/training/train_duration_model.py` retrains with a seeded holdout split and reports out-of-sample MAE against the naive-estimate baseline.
3. `ml-service/training/promote_duration_model.py` promotes the candidate into the registry only when it beats the baseline and does not regress against the active model.
4. `POST /model/reload` serves the promoted artifact without a restart.

Training and promotion optionally record tasks, metrics, and artifacts to ClearML (`ORDOSTACK_CLEARML_ENABLED=1`, offline-capable, never blocking the loop); see [clearml/README.md](clearml/README.md). Longer-term model lifecycle planning lives in [docs/internal/mlops-production-roadmap.md](docs/internal/mlops-production-roadmap.md).

## Persistence

Docker Compose uses MySQL for:

- users,
- tasks,
- fixed events,
- execution logs,
- schedule runs,
- schedule items,
- schedule templates.

Alembic migrations run before `backend-api` starts in Docker. The older schema bootstrap remains only as a local compatibility fallback.

## Failure Modes

| Failure | Product behavior | Recovery boundary |
| --- | --- | --- |
| `ml-service` unavailable | Backend uses task estimates as the duration fallback | Restore ML service; no product data repair required |
| `scheduler-service` unavailable | Schedule generation returns `503`; existing tasks and saved schedules remain available | Restore scheduler service and retry generation |
| MySQL unavailable | Persistent product requests fail; health remains process-only and readiness must be checked | Restore MySQL before accepting writes |
| Dashboard unavailable | API and stored data remain intact | Restore or replace the stateless dashboard container |
| Migration failure | Backend container does not start | Fix forward or restore an approved backup; do not silently downgrade |
| Invalid production configuration | Backend startup or readiness fails | Correct external environment values and restart |

## Deployment Topology

Local and CI runtime:

```mermaid
flowchart LR
  user["Browser"] --> dashboard["web-dashboard"]
  dashboard --> api["backend-api"]
  api --> mysql[("MySQL volume")]
  api --> scheduler["scheduler-service"]
  api --> ml["ml-service"]
```

Hosted beta target:

```mermaid
flowchart LR
  internet["Internet"] --> tls["TLS / reverse proxy"]
  tls --> dashboard["web-dashboard"]
  tls --> api["backend-api"]
  api --> mysql[("Private MySQL / RDS")]
  api --> scheduler["private scheduler-service"]
  api --> ml["private ml-service"]
  api --> logs["logs / monitoring"]
  mysql --> backups["encrypted off-host backups"]
```

Only the dashboard and backend API may be public. Internal services and MySQL must not expose public ports in a hosted environment.

## Security Boundaries

- `backend-api` authenticates users and scopes planner data by user.
- Production rejects the local auth secret and disables demo reset.
- Secrets remain external to images and Git.
- Request logs exclude bodies, authorization headers, cookies, and query strings.
- Hosted TLS, secret storage, rate limiting, and account recovery remain deployment gates.

## Quality Gates

Local verification is split into two levels.

Fast gate:

```powershell
python scripts\ponytail.py --include-compose-config
```

Runtime gate:

```powershell
docker compose up --build -d
python scripts\e2e_smoke.py
python scripts\browser_smoke.py
```

The runtime gate checks the full path through dashboard, backend, scheduler, ml-service, and MySQL.

GitHub Actions also runs the stack from a clean checkout and verifies migrations, E2E, browser rendering, MySQL restart persistence, backup integrity, and restore into a temporary database.

## Current Limits

- No hosted infrastructure is included.
- No production secret store is configured.
- No off-host backup destination is wired.
- No external monitoring vendor is configured.
- No production ML model registry or ClearML agent is running.
- The mobile app folder is not an implemented mobile client.
