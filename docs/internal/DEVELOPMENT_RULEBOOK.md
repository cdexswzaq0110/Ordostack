# Development Rulebook

## Core Principles

- Keep the MVP runnable before adding features.
- Prefer clear data structures over complex branching.
- Use early returns where they reduce nesting.
- Keep route handlers thin.
- Put business logic in service modules.
- Put persistence logic in repository modules.
- Keep schemas, models, services, and repositories separate.

## Compatibility

- Do not break existing endpoints.
- Do not rename public routes without updating docs and callers.
- Do not change Docker ports without updating README and Compose health checks.

## Branching

- Use one short-lived branch per issue after the initial repository baseline exists.
- Use `feature/`, `fix/`, `chore/`, or `docs/` prefixes.
- Keep `main` runnable.
- Record suggested commit messages in `CHANGELOG.md` and `docs/internal/development-log.md`.

## Service Ports

| Service | Port |
| --- | ---: |
| backend-api | 8000 |
| scheduler-service | 8100 |
| ml-service | 8200 |
| web-dashboard | 5173 |

## Health Endpoint Contract

Each backend service must return JSON with at least:

```json
{
  "status": "ok",
  "service": "service-name",
  "version": "0.1.0"
}
```

## Local Commands

### Windows PowerShell

```powershell
docker compose up --build
```

### Linux / WSL

```bash
docker compose up --build
```

## Testing Policy

- Add focused tests for behavior that can regress.
- Scheduler algorithms require unit tests when implemented.
- Backend API features require integration-style endpoint tests.
- Docker Compose must stay runnable after every infrastructure change.
- Pull requests must pass the CI quality gate before merge.

## Secrets Policy

- `.env` is ignored.
- `.env.example` may contain empty variables only.
- ClearML and AWS credentials must live outside the repository.
- Database credentials must not be hard-coded in application code.
