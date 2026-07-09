# OrdoStack Project Status Report

Date: 2026-06-30
Version: 0.52.0
Report role: PM / project management

## Executive Summary

OrdoStack is a local Private Beta Candidate with authenticated user-scoped planning, schedule generation and persistence, execution analytics, local duration prediction, Docker Compose, MySQL migrations, and automated release gates. The v0.52.0 CI runtime gate starts the full stack from a clean checkout and verifies E2E behavior, browser rendering, MySQL restart persistence, backup integrity, and isolated restore. It is not ready for public launch because hosted deployment, production monitoring, external secret management, off-host backup automation, account recovery, and formal security/accessibility approval remain open.

Current evidence:

- Previous release baseline: `v0.51.3`.
- Current product stage: local Private Beta Candidate `v0.52.0`.
- Main runnable entrypoint: `http://localhost:5173`.
- Runtime: local Docker Compose with an automated clean-checkout CI gate.
- Database: local MySQL container.
- Verification gates available: service tests, dashboard build, Compose validation, full Docker startup, readiness, E2E, browser smoke, MySQL restart persistence, backup and isolated restore, accessibility static audit, security audit, documentation checks, and translation coverage.

## PM Assessment

Customer reference MVP:

```text
Status: Ready for local customer reference demo
Confidence: High for demo flow, not for production usage
```

Public launch:

```text
Status: Not ready
Estimated remaining issue count: 7 to 12 focused issues
Reason: hosted deployment execution, production security review, monitoring implementation, off-host backup automation, production data policy, and operational ownership are missing
```

Private beta:

```text
Status: Local Private Beta Candidate
Estimated remaining issue count: 3 to 5 focused issues
Reason: repository and Docker runtime gates are in place; hosted deployment, external operations, and manual sign-off remain
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
- Alembic migrations through revision `20260610_0004`.
- Generated schedule latest view and history.
- Schedule history rename, soft delete, lock, manual adjustment, diff, Markdown/CSV/PDF export.
- Named schedule templates.
- Demo reset for bundled local demo user.
- Local auth foundation with demo account, register, login, and current-user API.
- Auth hardening baseline with password policy, token expiry configuration, production secret validation, and failed-login rate limiting.
- User-scoped planner APIs for authenticated local users.
- Observability baseline with request IDs, structured request logs, readiness endpoints, hosted monitoring plan, and local monitoring probe.
- Backup/restore baseline with local MySQL backup scripts, backup verification, non-destructive restore drill docs, and production backup policy audit.
- Dashboard empty states and retry behavior.
- Local E2E smoke test.
- Browser screenshot smoke test and non-Docker CI browser smoke artifact.
- Visual regression threshold script.
- Accessibility static audit script.
- Security audit script.
- Non-Docker release QA gate.
- Backup policy audit and beta readiness check.
- Manual accessibility QA checklist.
- Beta readiness review.
- Version history, release process, QA plan, API docs, architecture docs.
- Environment configuration docs and startup validation.

## Not Implemented

Launch-critical gaps:

- Hosted refresh-token/session store, account recovery, admin support tooling, and complex authorization.
- Real onboarding and user profile settings.
- Timezone and locale settings.
- Production deployment with HTTPS, domain, reverse proxy, environment separation.
- Hosted observability implementation: metrics backend, traces, uptime checks, alerting, retention.
- Production backup execution: scheduled jobs, off-host encrypted storage, restore execution, and data retention policy.
- Production secrets management.
- Production security hardening, dependency governance, and formal security review.
- Manual accessibility QA execution and keyboard workflow QA sign-off.
- Hosted browser regression governance beyond local threshold script.
- Broader API abuse protection beyond login rate limiting.
- Production database migration rollback policy.

Product gaps from the original specification:

- Mobile app implementation.
- ClearML agent execution and hosted tracking workflow.
- Production ML model promotion workflow.
- DL completion-rate or focus-score service.
- Calendar integration and cloud share links.
- Drag-and-drop schedule editing.

## Known Weak Points

- The dashboard uses local bearer auth and auth hardening controls, but it is still a demo-oriented web client without hosted refresh sessions.
- The demo reset endpoint restores local demo data and is not a production account recovery feature.
- Browser smoke verifies a nonblank PNG; the local visual regression script still depends on reviewed screenshot artifacts.
- The ML model is a local JSON artifact, not an operationally managed model.
- CI runs build/test/config plus the full Docker runtime, E2E, persistence, backup, and isolated restore gate.
- Observability has a hosted monitoring plan but no configured hosted metrics backend, tracing backend, uptime monitor, or alerting implementation yet.
- Backup/restore has a production policy baseline but no scheduled jobs, encrypted off-host storage implementation, or automated production restore.

## Recommended Next Issues

Issue 46: Focused QA pass for Issues 34-45

- Status: implemented as `scripts/release_qa_gate.py` plus QA documentation.

Issue 47: Production auth hardening

- Status: local baseline implemented for password policy, token expiry configuration, production secret validation, and failed-login rate limiting.
- Remaining: hosted refresh/session store, account recovery, and admin support boundaries.

Issue 48: Hosted monitoring baseline

- Status: implemented as monitoring plan and local health/readiness probe.
- Remaining: configure chosen hosted monitoring backend after deployment target is selected.

Issue 49: Production backup automation

- Status: policy and audit implemented.
- Remaining: scheduled backup execution, encrypted off-host destination, and restore execution after hosting target is selected.

Issue 50: Docker finalization and deployment hardening

- Status: local beta runtime gate implemented in v0.52.0.
- Remaining production work: image scanning, hosted TLS, external secrets, private networking, and operational rollout under Issue 51.

Issue 51: Hosted beta deployment execution

- Provision target environment only after account decisions are confirmed.
- Validate HTTPS, domain, runtime env, backup, monitoring, and rollback.

Issue 52: Manual accessibility QA

- Status: checklist implemented.
- Remaining: execute manual QA on real browser flows and record findings.

Issue 53: Product beta readiness review

- Status: beta readiness document and check implemented.
- Remaining: PM approval of support owner, onboarding language, feedback channel, and launch messaging.

## Launch Recommendation

Do not market this as a finished public product yet.

Recommended positioning now:

```text
Private Beta Candidate
```

Recommended next milestone:

```text
Private Beta
```

Minimum next target for private beta:

- Complete formal manual accessibility and security sign-off.
- Keep the Docker runtime gate required on every release PR.
- Decide whether hosted beta needs AWS or a simpler single-node environment.
- Keep mobile and ClearML agent execution out of the first beta unless they become explicit customer blockers.

## Next Execution Plan

The next engineering pass should execute manual QA using `docs/qa-mvp.md` and `docs/accessibility-qa.md`, then start Issue 51 hosted beta deployment after hosting, monitoring, backup, and support ownership are confirmed.
