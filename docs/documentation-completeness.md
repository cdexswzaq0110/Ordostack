# Documentation Index

This repository keeps several Markdown files because the project has product, engineering, QA, and operations concerns. For GitHub readers, the entry points are intentionally small:

- [README.md](../README.md) for project overview and local setup.
- [ARCHITECTURE.md](../ARCHITECTURE.md) for service boundaries and data flow.
- [ORDOSTACK_PROJECT_SPEC.md](../ORDOSTACK_PROJECT_SPEC.md) for current product scope.
- [docs/qa-mvp.md](qa-mvp.md) for verification.
- [docs/api.md](api.md) for endpoint behavior.

## Testing Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `docs/qa-mvp.md` | Present | Manual QA and API smoke coverage |
| `scripts/ponytail.py` | Present | Compact local clean gate |
| `scripts/release_qa_gate.py` | Present | Tests, audits, build, translations, and visual regression |
| `scripts/e2e_smoke.py` | Present | Docker runtime API smoke |
| `scripts/browser_smoke.py` | Present | Dashboard browser smoke |
| `.github/workflows/ci.yml` | Present | CI baseline |

## System Design Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `ORDOSTACK_PROJECT_SPEC.md` | Present | Product scope and launch gaps |
| `ARCHITECTURE.md` | Present | Runtime boundaries, data flow, persistence, and gates |
| `docs/system-analysis.md` | Present | Problem, actors, data ownership, and acceptance baseline |
| `docs/api.md` | Present | Endpoint behavior |
| `docs/algorithms.md` | Present | Scheduling algorithm notes |
| `docs/database-migrations.md` | Present | Alembic and migration policy |
| `docs/environment.md` | Present | Runtime variables |
| `docs/deployment.md` | Present | Future hosted deployment checklist |

## GitHub Documents

| Document | Status | Purpose |
| --- | --- | --- |
| `README.md` | Present | First-read project page |
| `CONTRIBUTING.md` | Present | Local setup and quality gate |
| `SECURITY.md` | Present | Vulnerability and secrets policy |
| `SUPPORT.md` | Present | Support scope and known limits |
| `.github/pull_request_template.md` | Present | PR checklist |
| `.github/ISSUE_TEMPLATE/*` | Present | Bug, feature, and ML experiment templates |

## Cleanup Note

The files below are useful during development but are candidates for consolidation before a public launch:

- `AI_RULEBOOK.md`
- `DEVELOPMENT_RULEBOOK.md`
- `docs/development-log.md`
- `docs/project-status-report.md`
- `docs/beta-readiness.md`
- `docs/branching-strategy.md`

They were not deleted in this cleanup because repository file deletion requires explicit owner approval.

## Verification

Run:

```powershell
python scripts\docs_completeness_check.py --root .
python scripts\ponytail.py --include-compose-config
```

Expected:

- documentation completeness passes,
- release QA gate passes,
- Git whitespace check passes,
- Docker Compose config validation passes.
