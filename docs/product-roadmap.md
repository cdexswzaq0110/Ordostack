# Product Roadmap

OrdoStack is a local Private Beta Candidate. The next milestone is a controlled hosted beta, not a public SaaS launch.

## Audit Baseline

Audited on 2026-06-30 against branch `codex/docs-github-cleanup`.

- Implemented: authenticated planner API, user-scoped tasks and fixed events, saved schedules, execution analytics, local duration prediction, MySQL migrations, Docker Compose definitions, and local QA scripts.
- Verified: 60 backend tests, 11 scheduler tests, 9 ML tests, dashboard production build, static accessibility audit, security scan, documentation check, backup policy check, beta readiness check, 210 translation keys, local E2E, and browser smoke.
- Docker Compose syntax passed in CI. The v0.52.0 runtime gate adds clean-checkout startup, migrations, E2E, MySQL restart persistence, backup verification, and isolated restore.
- The audited dead navigation, unused actions, static health claims, and production demo-reset exposure are resolved.

## Phase 1 — Minimum Credible Beta UI

Status: complete.

- Make every visible navigation and schedule action functional or remove it. Completed for the audited placeholders.
- Replace static health claims with state the dashboard can actually observe. Completed for dashboard data state.
- Preserve English default, Traditional Chinese support, keyboard focus, responsive layout, and existing API behavior.
- Add success feedback for core planning actions. Completed with an accessible live region.
- Gate: dashboard build, static accessibility audit, and translation coverage passed; local browser interaction smoke passed.

## Phase 2 — Runtime Confidence

Status: implemented as the v0.52.0 Docker runtime CI gate.

- Run Docker Compose from a clean checkout. Automated in CI.
- Verify migrations, MySQL persistence across restart, E2E smoke, backup creation, and restore against a temporary database. Automated in CI.
- Run dependency and container image scans; resolve high-severity findings. Remains a hosted release gate.
- Gate: all service tests, Compose config, healthy stack, E2E smoke, backup and restore drill.

## Phase 3 — Controlled Hosted Beta

Priority: after a hosting decision.

- Provision one staging environment with TLS, external secrets, managed or backed-up MySQL, uptime checks, logs, alerts, and rollback instructions.
- Add refresh sessions, account recovery, support ownership, data retention, and incident handling.
- Gate: manual accessibility sign-off, security review, tested alerts, tested restore, PM launch approval.

## Deferred Commercial Work

These are roadmap items, not implemented product claims:

- Mobile client: build only after beta usage proves the daily-plan viewing and completion flows need native delivery. See `mobile-app/README.md`.
- ClearML operations: add an agent and hosted registry only when training cadence and model ownership justify it. Local prediction must remain independent.
- AWS production topology, autoscaling, multi-region recovery, payments, enterprise roles, calendar integrations, and formal SLA.

## Release Labels

| Label | Evidence required |
| --- | --- |
| Customer Demo MVP / Technical Preview | Superseded by v0.52.0 |
| Private Beta Candidate | Phases 1 and 2 complete |
| Private Beta | Phase 3 deployed and approved |
| Production Ready | Separate production security, operations, support, and business review |
