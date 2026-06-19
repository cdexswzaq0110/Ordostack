# Release Process

OrdoStack uses MVP issue releases until production deployment exists.

## Current Version

```text
0.50.0
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

## Current Non-Docker Release Checklist

Windows PowerShell:

```powershell
python scripts\ponytail.py
```

Expanded commands:

```powershell
cd backend-api
..\.venv\Scripts\python.exe -m pytest tests
cd ..\scheduler-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..\ml-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..
cd web-dashboard
npm run build
cd ..
python scripts\a11y_static_audit.py
python scripts\security_audit.py --root .
python scripts\backup_policy_audit.py --root .
python scripts\beta_readiness_check.py --root .
python scripts\visual_regression.py --baseline artifacts\visual-baseline\dashboard.png --candidate artifacts\browser-smoke\dashboard.png --threshold 0.01
```

Combined non-Docker gate:

```powershell
python scripts\release_qa_gate.py
```

## Clean Check

Use this before final delivery or commit:

```powershell
python scripts\ponytail.py
```

Use this when Docker is available:

```powershell
python scripts\ponytail.py --include-compose-config
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
cd web-dashboard
npm run build
cd ..
python scripts/a11y_static_audit.py
python scripts/security_audit.py --root .
python scripts/backup_policy_audit.py --root .
python scripts/beta_readiness_check.py --root .
python scripts/visual_regression.py --baseline artifacts/visual-baseline/dashboard.png --candidate artifacts/browser-smoke/dashboard.png --threshold 0.01
```

## Deferred Docker Deployment Checklist

Run this checklist during the dedicated Docker finalization issue, not during product behavior iteration:

```powershell
docker compose config
docker compose up --build -d
docker compose ps
python scripts\e2e_smoke.py
python scripts\browser_smoke.py
powershell -ExecutionPolicy Bypass -File scripts\backup_mysql.ps1
powershell -ExecutionPolicy Bypass -File scripts\verify_mysql_backup.ps1 -Path artifacts\backups\<backup-file>.sql
```

## Tagging

After a clean release commit:

```bash
git tag v0.50.0
```

Tags should point only to commits that passed the release checklist.
