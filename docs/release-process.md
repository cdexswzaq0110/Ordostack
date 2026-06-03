# Release Process

OrdoStack uses MVP issue releases until production deployment exists.

## Current Version

```text
0.11.0
```

## Release Types

- Major: reserved for production-breaking architecture changes.
- Minor: new MVP feature issue.
- Patch: workflow, documentation, CI, or baseline process improvement.

## Baseline Commit

Issue 11 establishes the first Git baseline commit because the repository had no commits after Issues 1 through 10 were implemented.

Baseline commit message:

```text
chore(repo): establish ordostack mvp baseline
```

This baseline includes:

- Repository skeleton.
- Task and fixed event MVP.
- Scheduler MVP.
- Execution logs and analytics.
- Duration prediction and local ML artifact.
- MySQL persistence.
- Persisted generated schedules.
- Alembic migration baseline.
- CI quality gate and branch strategy.

## Release Checklist

Windows PowerShell:

```powershell
cd backend-api
..\.venv\Scripts\python.exe -m pytest tests
cd ..\scheduler-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..\ml-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..
docker compose config
docker compose up --build -d
docker compose ps
```

Linux / WSL:

```bash
cd backend-api
../.venv/bin/python -m pytest tests
cd ../scheduler-service
../.venv/bin/python -m pytest tests
cd ../ml-service
../.venv/bin/python -m pytest tests
cd ..
docker compose config
docker compose up --build -d
docker compose ps
```

## Tagging

After a clean baseline commit:

```bash
git tag v0.10.1
```

Tags should point only to commits that passed the release checklist.
