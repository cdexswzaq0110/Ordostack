# OrdoStack Project Status Report

Date: 2026-06-10
Version: 0.44.0
Report role: PM / project management

## Executive Summary

OrdoStack is currently a local Customer Demo MVP / Technical Preview with authentication, user-scoped planner data, English / Traditional Chinese dashboard locale support, manual schedule controls, recurring fixed events, reusable schedule templates, local PDF export, completion forecast, local model registry, duration feedback export, browser smoke CI, visual regression script, accessibility static audit, security audit script, deployment baseline documentation, observability baseline, and backup/restore drill baseline. It is suitable for internal QA and customer reference demos on a developer machine. It is not ready for public launch because final Docker/deployment hardening, hosted monitoring, production backup automation, production security review, mobile app, ClearML agent execution, and production model governance are not implemented yet.

Current evidence:

- Previous release tag before this hardening batch: `v0.32.0`.
- Current product stage after Issue 45: local Customer Demo MVP / Technical Preview `v0.44.0`.
- Main runnable entrypoint: `http://localhost:5173`.
- Runtime: local services; Docker finalization intentionally deferred.
- Database: local MySQL container.
- Verification gates available: Python tests, readiness checks, environment validation, E2E smoke, browser screenshot smoke, visual regression script, a11y static audit, security audit, backup verification, secrets scan, and non-Docker browser smoke CI.

## PM Assessment

Customer reference MVP:

```text
Status: Ready for local customer reference demo
Confidence: High for demo flow, not for production usage
```

Public launch:

```text
Status: Not ready
Estimated remaining issue count: 10 to 16 focused issues
Reason: final Docker/deployment hardening, production security review, hosted monitoring, production backup automation, production data policy, and operational workflows are missing
```

Private beta:

```text
Status: Candidate after focused QA
Estimated remaining issue count: 4 to 8 focused issues
Reason: beta can skip mobile and full MLOps, but still needs final Docker/deployment hardening, security hardening, hosted monitoring, and stricter QA sign-off
```

The exact issue count depends on the launch definition. If launch means a controlled private beta for a small customer group, the smaller range applies. If launch means public SaaS or app-store-ready product, the larger range is more realistic.

## Implemented Scope

Product capabilities already implemented:

- Task create, edit, status transition, reopen, skip, soft delete.
- Fixed event create, edit, soft delete.
- Weekly recurring fixed event expansion.
- Date navigation, date picker, Today shortcut.
- Task queue search, status/category/focus filters, sorting.
- English / Traditional Chinese dashboard language switcher.
- Daily schedule generation.
- Schedule item lock/unlock and manual `-15/+15` adjustment controls.
- Scheduler algorithms: priority score, topological sort, knapsack-style capacity selection, priority queue ordering, fixed-event free-slot builder.
- Execution logs and daily analytics.
- Local duration prediction through ml-service.
- Completion forecast.
- Local JSON model registry and duration feedback CSV export.
- MySQL persistence for Docker runtime.
- Alembic migrations through revision `20260604_0003`.
- Generated schedule latest view and history.
- Schedule history rename, soft delete, lock, manual adjustment, diff, Markdown/CSV/PDF export.
- Named schedule templates.
- Demo reset for bundled local demo user.
- Local auth foundation with demo account, register, login, and current-user API.
- User-scoped planner APIs for authenticated local users.
- Observability baseline with request IDs, structured request logs, and readiness endpoints.
- Backup/restore baseline with local MySQL backup scripts, backup verification, and non-destructive restore drill docs.
- Dashboard empty states and retry behavior.
- Local E2E smoke test.
- Browser screenshot smoke test and non-Docker CI browser smoke artifact.
- Visual regression threshold script.
- Accessibility static audit script.
- Security audit script.
- Version history, release process, QA plan, API docs, architecture docs.
- Environment configuration docs and startup validation.

## Not Implemented

Launch-critical gaps:

- Production-grade authentication and authorization.
- Real onboarding and user profile settings.
- Timezone and locale settings.
- Production deployment with HTTPS, domain, reverse proxy, environment separation.
- Hosted observability: metrics, traces, uptime checks, alerting, retention.
- Production backup automation, off-host encrypted storage, restore approval workflow, and data retention policy.
- Production secrets management.
- Production security hardening, dependency governance, and formal security review.
- Full manual accessibility audit and keyboard workflow QA sign-off.
- Hosted browser regression governance beyond local threshold script.
- Rate limiting and API abuse protection.
- Production database migration rollback policy.

Product gaps from the original specification:

- Mobile app implementation.
- ClearML agent execution and hosted tracking workflow.
- Production ML model promotion workflow.
- DL completion-rate or focus-score service.
- Calendar integration and cloud share links.
- Drag-and-drop schedule editing.

## Known Weak Points

- The dashboard now uses local bearer auth, but it is still a demo-oriented web client.
- The demo reset endpoint restores local demo data and is not a production account recovery feature.
- Browser smoke verifies a nonblank PNG but does not detect visual regressions pixel-by-pixel.
- The ML model is a local JSON artifact, not an operationally managed model.
- Current CI validates build/test/config but does not run full Docker runtime E2E in GitHub Actions.
- Observability is local baseline only; it has no metrics backend, tracing backend, hosted uptime monitor, alerting, or retention policy yet.
- Backup/restore is local baseline only; it has no scheduled jobs, encrypted off-host storage, or automated production restore.

## Recommended Next Issues

Issue 46: Focused QA pass for Issues 34-45

- Run manual QA for lock, manual move, recurrence, templates, export, forecast, model registry, and scripts.
- Capture customer-demo screenshots in English and Traditional Chinese.

Issue 47: Production auth hardening

- Add password policy, token expiry governance, refresh/session handling, and rate limiting.
- Define account recovery and admin support boundaries.

Issue 48: Hosted monitoring baseline

- Add metrics and uptime monitor plan.
- Define alert routing and retention policy.

Issue 49: Production backup automation

- Add scheduled backup design, encryption, off-host storage, restore approval workflow, and retention policy.

Issue 50: Docker finalization and deployment hardening

- Revisit Dockerfiles, Docker Compose, production compose, reverse proxy, health checks, image scanning, and deployment runbooks as one final deployment pass.
- This is intentionally deferred until product behavior stabilizes.

Issue 51: Hosted beta deployment execution

- Provision target environment only after account decisions are confirmed.
- Validate HTTPS, domain, runtime env, backup, monitoring, and rollback.

Issue 52: Manual accessibility QA

- Run keyboard-only, screen reader, contrast, and responsive checks on real browser flows.

Issue 53: Product beta readiness review

- Review data policy, support workflow, customer onboarding, feedback collection, and launch messaging.

## Launch Recommendation

Do not market this as a finished public product yet.

Recommended positioning now:

```text
Customer Demo MVP / Technical Preview
```

Recommended next milestone:

```text
Private Beta Candidate
```

Minimum next target for private beta:

- Complete a focused QA pass on Issues 34 to 45.
- Keep Docker finalization as a dedicated deployment hardening pass.
- Decide whether hosted beta needs AWS or a simpler single-node environment.
- Keep mobile and ClearML agent execution out of the first beta unless they become explicit customer blockers.

## Next Execution Plan

The next engineering pass should run Issue 46 focused QA for Issues 34-45, then prepare Issue 50 Docker finalization and deployment hardening once the product behavior is accepted.
