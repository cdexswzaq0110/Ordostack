# Database Migrations

Issue 9 introduces Alembic as the database migration tool for `backend-api`.

## Current Revision

```text
20260604_0003_auth_users
```

## Docker Startup

`backend-api` runs this before serving HTTP traffic:

```bash
alembic upgrade head
```

The repository still keeps repository-level `CREATE TABLE IF NOT EXISTS` bootstrap as a local compatibility fallback, but Docker startup treats Alembic as the migration path.

## Commands

Windows PowerShell:

```powershell
docker compose exec backend-api alembic current
docker compose exec backend-api alembic history
docker compose exec backend-api alembic upgrade head
```

Linux / WSL:

```bash
docker compose exec backend-api alembic current
docker compose exec backend-api alembic history
docker compose exec backend-api alembic upgrade head
```

## Downgrade Policy

Destructive downgrade is not implemented in the MVP. Database rollback must be handled by restoring a known development volume or a production backup in later deployment phases.
