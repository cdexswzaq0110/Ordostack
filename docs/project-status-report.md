# OrdoStack Project Status Report

Date: 2026-06-04
Version: 0.30.0
Report role: PM / project management

## Executive Summary

OrdoStack is currently a local Customer Demo MVP with authentication, user-scoped planner data, deployment baseline documentation, and observability baseline. It is suitable for internal QA and customer reference demos on a developer machine through Docker Compose. It is not ready for public launch because hosted deployment execution, backup/restore operations, security review, mobile app, ClearML production workflow, hosted monitoring, and production model governance are not implemented yet.

Current evidence:

- Previous release tag before observability baseline: `v0.29.0`.
- Current product stage after Issue 31: observable Customer Demo MVP `v0.30.0`.
- Main runnable entrypoint: `http://localhost:5173`.
- Runtime: local Docker Compose.
- Database: local MySQL container.
- Verification gates available: Python tests, web build, Docker health checks, readiness checks, environment validation, E2E smoke, browser screenshot smoke, secrets scan.

## PM Assessment

Customer reference MVP:

```text
Status: Ready for local customer reference demo
Confidence: High for demo flow, not for production usage
```

Public launch:

```text
Status: Not ready
Estimated remaining issue count: 16 to 22 focused issues
Reason: hosted deployment, security, backup, production data policy, accessibility, hosted monitoring, and operational workflows are missing
```

Private beta:

```text
Status: Not ready yet
Estimated remaining issue count: 4 to 7 focused issues
Reason: beta can skip mobile and full MLOps, but still needs backup, hosted deployment execution, security hardening, hosted monitoring, and stricter QA
```

The exact issue count depends on the launch definition. If launch means a controlled private beta for a small customer group, the smaller range applies. If launch means public SaaS or app-store-ready product, the larger range is more realistic.

## Implemented Scope

Product capabilities already implemented:

- Task create, edit, status transition, reopen, skip, soft delete.
- Fixed event create, edit, soft delete.
- Date navigation, date picker, Today shortcut.
- Task queue search, status/category/focus filters, sorting.
- Daily schedule generation.
- Scheduler algorithms: priority score, topological sort, knapsack-style capacity selection, priority queue ordering, fixed-event free-slot builder.
- Execution logs and daily analytics.
- Local duration prediction through ml-service.
- MySQL persistence for Docker runtime.
- Alembic migrations through revision `20260604_0003`.
- Generated schedule latest view and history.
- Schedule history rename, soft delete, diff, Markdown/CSV export.
- Demo reset for bundled local demo user.
- Local auth foundation with demo account, register, login, and current-user API.
- User-scoped planner APIs for authenticated local users.
- Observability baseline with request IDs, structured request logs, and readiness endpoints.
- Dashboard empty states and retry behavior.
- Local E2E smoke test.
- Browser screenshot smoke test.
- Version history, release process, QA plan, API docs, architecture docs.
- Environment configuration docs and startup validation.

## Not Implemented

Launch-critical gaps:

- Production-grade authentication and authorization.
- Real onboarding and user profile settings.
- Timezone and locale settings.
- Production deployment with HTTPS, domain, reverse proxy, environment separation.
- Hosted observability: metrics, traces, uptime checks, alerting, retention.
- Backup, restore, and data retention policy.
- Production secrets management.
- Security hardening and dependency audit gate.
- Accessibility audit and keyboard workflow QA.
- Browser regression test baseline beyond smoke screenshot.
- Rate limiting and API abuse protection.
- Production database migration rollback policy.

Product gaps from the original specification:

- Mobile app implementation.
- ClearML experiment tracking and agent execution.
- Production ML model registry and model promotion workflow.
- DL completion-rate or focus-score service.
- Calendar integration and recurring fixed events.
- Manual schedule editing / locking / drag-and-drop.
- Named schedule templates.
- PDF export and cloud share links.

## Known Weak Points

- The dashboard now uses local bearer auth, but it is still a demo-oriented web client.
- The demo reset endpoint restores local demo data and is not a production account recovery feature.
- Browser smoke verifies a nonblank PNG but does not detect visual regressions pixel-by-pixel.
- The ML model is a local JSON artifact, not an operationally managed model.
- Current CI validates build/test/config but does not run full Docker runtime E2E in GitHub Actions.
- Observability is local baseline only; it has no metrics backend, tracing backend, hosted uptime monitor, alerting, or retention policy yet.

## Recommended Next Issues

Issue 32: Backup and restore MVP

- Add database backup command docs.
- Add restore drill docs.
- Add non-destructive backup verification checklist.

Issue 33: Manual schedule locking

- Allow a generated schedule item to be locked.
- Scheduler should preserve locked items in future generation.

Issue 34: Schedule manual adjustment

- Add simple time edit for schedule items.
- Validate fixed event conflicts.

Issue 35: Recurring fixed events MVP

- Add weekly recurrence fields.
- Expand recurrence into date-scoped fixed events.

Issue 36: Named schedule templates

- Save planning settings as reusable templates.
- Reuse start/end hour, buffer, mode, fixed-event inclusion.

Issue 37: PDF export

- Add local PDF export without paid APIs.
- Keep Markdown/CSV as fallback.

Issue 38: Accessibility pass

- Keyboard navigation QA.
- Focus states.
- ARIA label audit.
- Color contrast review.

Issue 39: ClearML local tracking baseline

- Add optional local ClearML tracking docs and disabled-by-default config.
- No paid API dependency.

Issue 40: Model registry abstraction

- Add local model metadata registry interface.
- Keep JSON artifact fallback.

Issue 41: Duration feedback loop

- Use completed task actual minutes to improve local model training data.

Issue 42: Completion forecast MVP

- Add heuristic completion-rate forecast before DL service.
- Use execution history and workload.

Issue 43: GitHub Actions browser smoke

- Add CI path for browser smoke where feasible.
- Upload screenshot artifact in CI.

Issue 44: Visual regression baseline

- Add deterministic screenshot baseline and threshold comparison.
- Keep artifacts ignored locally.

Issue 45: Security and dependency audit

- Add dependency audit commands.
- Add secret scan gate.
- Add dependency update policy.

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

- Complete Issues 28 to 32.
- Keep Issues 33 to 38 as product polish if beta users need schedule editing and recurring events.
- Keep Issues 39 to 42 as intelligence roadmap, not beta blockers unless ML capability is the primary sales claim.

## Next Execution Plan

The next engineering pass should complete Issue 32 because backup and restore drill documentation is the next blocker before calling this a private-beta candidate.
