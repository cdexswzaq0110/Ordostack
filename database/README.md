# Database

Issue 9 adds an Alembic migration baseline for `backend-api`, including generated schedules.

Docker Compose starts `mysql:8.4` with a local development database named `ordostack`. `backend-api` runs Alembic migrations before starting the API server.

Persisted tables:

- `tasks`
- `fixed_events`
- `execution_logs`
- `schedule_runs`
- `schedule_items`

Current limits:

- No production credential management yet.
- No schedule version comparison UI yet.
- No user/auth tables yet.
- Destructive downgrade is not supported in the MVP.

## Migration Commands

Windows PowerShell:

```powershell
docker compose exec backend-api alembic current
docker compose exec backend-api alembic upgrade head
```

Linux / WSL:

```bash
docker compose exec backend-api alembic current
docker compose exec backend-api alembic upgrade head
```

The first migration is idempotent and uses `CREATE TABLE IF NOT EXISTS` so existing local MVP volumes are not destroyed.
