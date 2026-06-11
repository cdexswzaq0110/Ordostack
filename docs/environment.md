# Environment Configuration

Issue 27 defines the local environment contract for OrdoStack.

Issue 30 adds `.env.production.example` as a hosted deployment template. Copy it to `.env.production` on the target server and keep the filled file out of Git.

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
| `AUTH_TOKEN_SECRET` | Production explicit | local-only fallback | HMAC signing secret for local bearer tokens; production requires at least 32 characters |
| `AUTH_TOKEN_TTL_MINUTES` | No | `10080` | Access token lifetime in minutes |
| `AUTH_LOGIN_MAX_FAILURES` | No | `5` | Failed login attempts allowed inside the login window |
| `AUTH_LOGIN_WINDOW_SECONDS` | No | `300` | Failed login counting window |
| `AUTH_LOGIN_LOCKOUT_SECONDS` | No | `300` | Lockout duration after too many failed login attempts |
| `AUTH_PASSWORD_MIN_LENGTH` | No | `12` | Registration password minimum length |

Production mode requires explicit `DATA_STORE`, `SCHEDULER_SERVICE_URL`, `ML_SERVICE_URL`, and `AUTH_TOKEN_SECRET`. The production auth token secret cannot use the local fallback and must be at least 32 characters. If production uses MySQL, `DB_PASSWORD` must not be empty.

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
AUTH_TOKEN_TTL_MINUTES=10080
AUTH_LOGIN_MAX_FAILURES=5
AUTH_LOGIN_WINDOW_SECONDS=300
AUTH_LOGIN_LOCKOUT_SECONDS=300
AUTH_PASSWORD_MIN_LENGTH=12
```

The empty MySQL password and fallback auth token secret are intentionally local-only. Do not reuse either behavior for production.

## Validation

backend-api validates runtime configuration during FastAPI startup. Alembic migrations and backend runtime use the same configuration parser, so migration and API startup fail consistently when required environment values are invalid.

Current validation coverage:

- Invalid `ORDOSTACK_ENV` is rejected.
- Invalid `DATA_STORE` is rejected.
- Invalid `DB_PORT` is rejected.
- Invalid scheduler or ML service URLs are rejected.
- Production mode requires explicit service URLs.
- Production mode rejects the local auth fallback secret and short auth token secrets.
- Auth numeric policy values must be positive integers.
- Production MySQL mode requires a non-empty database password.
