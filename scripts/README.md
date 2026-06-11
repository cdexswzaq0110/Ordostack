# Scripts

Operational scripts for local development and QA.

## Non-Docker Release QA Gate

Windows PowerShell:

```powershell
python scripts\release_qa_gate.py
```

Linux / WSL:

```bash
python scripts/release_qa_gate.py
```

The gate runs service tests, static audits, translation coverage, backup policy audit, and beta readiness checks. Frontend build is skipped when `npm` is not available unless `--require-frontend` is passed. Visual regression is skipped when screenshot artifacts are missing unless `--require-visual` is passed.

Strict mode after local frontend tooling and screenshots are available:

```powershell
python scripts\release_qa_gate.py --require-frontend --require-visual
```

## E2E Smoke

Windows PowerShell:

```powershell
python scripts\e2e_smoke.py
```

Linux / WSL:

```bash
python scripts/e2e_smoke.py
```

The smoke script expects `docker compose up --build -d` to be running locally.

## Browser Smoke

Windows PowerShell:

```powershell
python scripts\browser_smoke.py
```

Linux / WSL:

```bash
python scripts/browser_smoke.py
```

The browser smoke script expects Docker Compose to be running and a local Edge or Chrome executable to be installed. It writes screenshot artifacts under `artifacts/browser-smoke`, which is ignored by Git.

## A11y Static Audit

Windows PowerShell:

```powershell
python scripts\a11y_static_audit.py
```

Linux / WSL:

```bash
python scripts/a11y_static_audit.py
```

This static check does not require Docker. It validates the current dashboard source for focus-visible coverage and key ARIA labels.

## Visual Regression

Windows PowerShell:

```powershell
python scripts\visual_regression.py --baseline artifacts\visual-baseline\dashboard.png --candidate artifacts\browser-smoke\dashboard.png --threshold 0.01
```

Linux / WSL:

```bash
python scripts/visual_regression.py --baseline artifacts/visual-baseline/dashboard.png --candidate artifacts/browser-smoke/dashboard.png --threshold 0.01
```

To create or refresh a local baseline after review:

```powershell
python scripts\visual_regression.py --baseline artifacts\visual-baseline\dashboard.png --candidate artifacts\browser-smoke\dashboard.png --update
```

Baseline and candidate artifacts stay under `artifacts/`, which is ignored by Git.

## Security Audit

Windows PowerShell:

```powershell
python scripts\security_audit.py --root .
```

Linux / WSL:

```bash
python scripts/security_audit.py --root .
```

The audit scans for common secret token and private key patterns while excluding `.git`, `node_modules`, `dist`, and local artifacts.

## Monitoring Baseline

Windows PowerShell:

```powershell
python scripts\monitoring_baseline.py
```

Linux / WSL:

```bash
python scripts/monitoring_baseline.py
```

This probe checks local health and readiness endpoints. It expects services to be running but does not start Docker.

## Backup Policy Audit

Windows PowerShell:

```powershell
python scripts\backup_policy_audit.py --root .
```

Linux / WSL:

```bash
python scripts/backup_policy_audit.py --root .
```

This audit checks that backup scripts and the non-destructive production backup policy are documented.

## Beta Readiness Check

Windows PowerShell:

```powershell
python scripts\beta_readiness_check.py --root .
```

Linux / WSL:

```bash
python scripts/beta_readiness_check.py --root .
```

This check verifies that private-beta readiness documents and environment policy variables are present.

## MySQL Backup

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\backup_mysql.ps1
```

Linux / WSL:

```bash
bash scripts/backup_mysql.sh
```

Backup files are written under `artifacts/backups`, which is ignored by Git.

## MySQL Backup Verification

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_mysql_backup.ps1 -Path artifacts\backups\ordostack-YYYYMMDD-HHMMSS.sql
```

Linux / WSL:

```bash
bash scripts/verify_mysql_backup.sh artifacts/backups/ordostack-YYYYMMDD-HHMMSS.sql
```

The verification scripts check that the backup is non-empty, contains schema definitions, and does not contain `DROP DATABASE`, `DROP TABLE`, or `TRUNCATE TABLE`.
