# Environment Configuration

Issue 27 defines the local environment contract for OrdoStack.

## Supported Environments

| Value | Purpose |
| --- | --- |
| `local` | Default developer and Docker Compose environment |
| `test` | Automated test environment |
| `production` | Future deployed environment with stricter validation |

`ORDOSTACK_ENV` defaults to `local` when it is not set.

## Backend Configuration

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `ORDOSTACK_ENV` | No | `local` | Must be `local`, `test`, or `production` |
| `DATA_STORE` | No | `memory` | Must be `memory` or `mysql` |
| `DB_HOST` | MySQL only | `mysql` | Required when `DATA_STORE=mysql` |
| `DB_PORT` | MySQL only | `3306` | Must be an integer from `1` to `65535` |
| `DB_NAME` | MySQL only | `ordostack` | Required when `DATA_STORE=mysql` |
| `DB_USER` | MySQL only | `root` | Required when `DATA_STORE=mysql` |
| `DB_PASSWORD` | Production MySQL only | empty | Empty is allowed for local Docker only |
| `SCHEDULER_SERVICE_URL` | Production explicit | `http://scheduler-service:8100` | Must be `http` or `https` |
| `ML_SERVICE_URL` | Production explicit | `http://ml-service:8200` | Must be `http` or `https` |

Production mode requires explicit `DATA_STORE`, `SCHEDULER_SERVICE_URL`, and `ML_SERVICE_URL`. If production uses MySQL, `DB_PASSWORD` must not be empty.

## Web Dashboard Configuration

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | No | `http://localhost:8000/api` | Frontend API base URL |

## ML Service Configuration

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `DURATION_MODEL_PATH` | No | bundled artifact path | Optional local duration model override |

## Local Docker Compose

`docker-compose.yml` sets:

```text
ORDOSTACK_ENV=local
DATA_STORE=mysql
DB_HOST=mysql
DB_PORT=3306
DB_NAME=ordostack
DB_USER=root
DB_PASSWORD=
SCHEDULER_SERVICE_URL=http://scheduler-service:8100
ML_SERVICE_URL=http://ml-service:8200
```

The empty MySQL password is intentionally local-only. Do not reuse it for production.

## Validation

backend-api validates runtime configuration during FastAPI startup. Alembic migrations and backend runtime use the same configuration parser, so migration and API startup fail consistently when required environment values are invalid.

Current validation coverage:

- Invalid `ORDOSTACK_ENV` is rejected.
- Invalid `DATA_STORE` is rejected.
- Invalid `DB_PORT` is rejected.
- Invalid scheduler or ML service URLs are rejected.
- Production mode requires explicit service URLs.
- Production MySQL mode requires a non-empty database password.
