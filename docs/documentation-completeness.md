# Documentation Completeness

This is the index used to check whether the repository has the documents needed for a local release candidate.

## Testing Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `docs/qa-mvp.md` | Present | Manual smoke, API, schedule, auth, export, backup, a11y, and beta checks |
| `scripts/ponytail.py` | Present | Compact docs, tests, audits, and optional Docker Compose config runner |
| `scripts/release_qa_gate.py` | Present | Python service tests, a11y, security, backup policy, beta readiness, translations, and visual regression |
| `scripts/e2e_smoke.py` | Present | End-to-end API and dashboard smoke after Docker Compose is running |
| `scripts/browser_smoke.py` | Present | Dashboard screenshot smoke with local Edge or Chrome |
| `.github/workflows/ci.yml` | Present | Python tests, dashboard build, browser smoke, and compose config |

## System Design Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `ORDOSTACK_PROJECT_SPEC.md` | Present | Product specification, scope, implemented areas, gaps, and definition of done |
| `ARCHITECTURE.md` | Present | Runtime boundaries, data flow, persistence, quality gates, and limitations |
| `docs/system-analysis.md` | Present | Problem, actors, functional scope, data ownership, and acceptance baseline |
| `docs/api.md` | Present | Endpoint groups, request/response behavior, auth, persistence, and service contracts |
| `docs/algorithms.md` | Present | Scheduling pipeline and algorithm responsibilities |
| `docs/database-migrations.md` | Present | Alembic expectations and non-destructive rollback notes |
| `docs/environment.md` | Present | Local and production environment variables and validation rules |
| `docs/deployment.md` | Present | Single-node target, production env setup, reverse proxy, and smoke checklist |

## GitHub Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `README.md` | Present | Overview, quick start, health checks, clean checks, docs map, and support links |
| `CONTRIBUTING.md` | Present | Local setup, branching, quality gate, and no-secrets policy |
| `SECURITY.md` | Present | Supported version, reporting guidance, and secrets policy |
| `SUPPORT.md` | Present | Support scope, required debug info, and known limits |
| `.github/pull_request_template.md` | Present | Verification and release checklist |
| `.github/ISSUE_TEMPLATE/*` | Present | Bug, feature, and ML experiment templates |

## Verification

Run:

```powershell
python scripts\docs_completeness_check.py --root .
python scripts\ponytail.py
```

Expected:

- Documentation completeness check passes.
- Release QA gate passes.
- Git whitespace check passes.
- Optional Docker Compose config passes when `--include-compose-config` is used.
