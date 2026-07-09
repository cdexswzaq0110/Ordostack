# Scripts

Operational scripts for local development and QA.

## Ponytail Clean Gate

Windows PowerShell:

```powershell
python scripts\ponytail.py
```

Linux / WSL:

```bash
python scripts/ponytail.py
```

The clean gate runs documentation completeness, the non-Docker release QA gate, and Git whitespace checks. Add Docker Compose config validation when Docker is available:

```powershell
python scripts\ponytail.py --include-compose-config
```

## Documentation Completeness

Windows PowerShell:

```powershell
python scripts\docs_completeness_check.py --root .
```

Linux / WSL:

```bash
python scripts/docs_completeness_check.py --root .
```

This check verifies that testing, system design, and GitHub-facing documents exist and contain the required launch-facing sections.

## Non-Docker Release QA Gate

Windows PowerShell:

```powershell
python scripts\release_qa_gate.py
```

Linux / WSL:

```bash
python scripts/release_qa_gate.py
```

The gate runs service tests, static audits, translation coverage, backup policy audit, and beta readiness checks. Frontend build is skipped when `npm` or dashboard dependencies are not available unless `--require-frontend` is passed. Visual regression is skipped when screenshot artifacts are missing unless `--require-visual` is passed.

Strict mode after local frontend tooling and screenshots are available:

```powershell
cd web-dashboard
npm ci
cd ..
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

## Duration Feedback Export

Windows PowerShell:

```powershell
python scripts\export_duration_feedback.py --days 14
```

Linux / WSL:

```bash
python scripts/export_duration_feedback.py --days 14
```

Exports completed-task execution feedback from backend-api into `ml-service/training/data/duration_feedback.csv` for retraining. It expects Docker Compose to be running. The full retraining loop is:

```powershell
python scripts\export_duration_feedback.py
python ml-service\training\train_duration_model.py
python ml-service\training\promote_duration_model.py
curl -X POST http://localhost:8200/model/reload
```

Promotion is metrics-gated: the candidate must beat the naive-estimate baseline on holdout MAE and must not regress against the active model. See [docs/internal/mlops-production-roadmap.md](../docs/internal/mlops-production-roadmap.md).

## README Screenshot Capture

Windows PowerShell:

```powershell
python -m pip install playwright
python scripts\capture_readme_screenshots.py
```

Linux / WSL:

```bash
python -m pip install playwright
python scripts/capture_readme_screenshots.py
```

Resets the demo dataset, generates a plan, signs in as the demo user, and writes the README screenshots to `docs/images/`. It expects Docker Compose to be running and uses the local Edge or Chrome executable, so Playwright does not download a browser. Playwright is a dev-only tool dependency and is not part of any service's `requirements.txt`.

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
