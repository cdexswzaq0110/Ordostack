# Changelog

All notable MVP changes are recorded here. This project follows incremental issue-based delivery.

## 0.56.0 - 2026-07-11

- Apply a per-user calibration factor to served predictions: the median actual/predicted ratio over the user's recent paired prediction logs, active from three pairs, clamped to [0.5, 2.0], and computed from separately logged raw model outputs so the correction cannot feed back on itself (migration 0006).
- Report the calibration factor and sample count in the predictions API and show the calibration state in the MLOps view; fallback predictions stay uncalibrated.
- Add `scripts/load_test.py` and record a single-machine baseline: dashboard read mix p50 76ms / p95 158ms at 108 req/s, full schedule-generation chain p50 306ms / p95 392ms at 30.6 req/s, zero errors (200/50 requests at concurrency 10).
- Expand backend tests from 65 to 71 covering calibration math, clamping, minimum samples, feedback isolation, served application, and uncalibrated fallback.

## 0.55.0 - 2026-07-10

- Log every served prediction when a plan is generated and pair actual minutes back on task completion (`prediction_logs` table in both stores plus Alembic migration).
- Add `GET /api/ml/prediction-accuracy`: rolling overall and per-day MAE for the model against the raw-estimate baseline, rendered in the MLOps view as headline stats and daily comparison bars.
- Derive prediction confidence from per-category error profiles learned at training time, replacing the hardcoded confidence constants; unseen categories fall back to the global error and legacy artifacts to documented base values.
- Add `training/compare_models.py`, a cross-validated comparison of the production multiplier table against naive-estimate, ridge, and gradient-boosting candidates, with results recorded in `artifacts/model_comparison.json`.
- Expand tests to 106 (backend 65, scheduler 11, ml-service 30); scikit-learn joins the optional training requirements only.

## 0.54.0 - 2026-07-10

- Add optional ClearML integration for the training loop: training runs record tasks, parameters, holdout metrics, and artifacts; gate-passing promotions register the versioned model, all behind `ORDOSTACK_CLEARML_ENABLED=1`.
- Support credential-free verification through ClearML offline mode (`CLEARML_OFFLINE_MODE=1`); every integration point degrades to a logged no-op so the local loop never depends on ClearML.
- Document self-hosted ClearML server and agent bring-up in `clearml/README.md` and align the MLOps plan documents with the implemented mapping.
- Fix training to treat an exported feedback CSV with zero data rows as "no feedback yet" instead of failing.
- Stack the README interface screenshots vertically so GitHub renders them at full width.
- Expand ml-service tests from 19 to 26 covering ClearML enablement, tracking payloads, failure safety, promotion registration fallback, and empty-feedback training.

## 0.53.0 - 2026-07-09

- Redesign the dashboard with a warm editorial design system: ink/warm/canvas palette, display typography with letter-spaced uppercase labels, hairline borders, and square corners throughout.
- Make the sidebar navigation switch dedicated workspace views: Today, Tasks, Schedule, Analytics (per-task estimate / predicted / actual / delta table), MLOps (active model, per-task confidence, fallback chain), and Settings (account, language, shortcuts, demo reset).
- Replace the fabricated plan score with real schedule coverage (scheduled vs selected tasks) in the plan-quality ring.
- Label unscheduled timeline previews explicitly; compute the next fixed event from the current time; highlight the current schedule block with a Now badge.
- Add delete confirmations for tasks and fixed events, and keyboard shortcuts: Alt+Left/Right for day navigation, Alt+T for today, Alt+G for plan generation.
- Close the local ML retraining loop: `scripts/export_duration_feedback.py` pulls completed-task feedback, training merges it with seed data via a seeded holdout split with out-of-sample metrics, and `promote_duration_model.py` performs metrics-gated promotion into the local JSON model registry.
- Add `POST /model/reload` to ml-service so a promoted artifact serves without a container restart; ml-service tests grow from 11 to 19.
- Rewrite the README introduction and installation guide around real dashboard screenshots (`docs/images/`, reproducible via `scripts/capture_readme_screenshots.py`) and record verification evidence in `docs/test-report.md`.
- Move development-history and planning documents into `docs/internal/` so the top-level docs stay product-facing.
- Merge the v0.52.0 private-beta baseline from main, keeping its success-feedback notices, observable dashboard status, and production demo-reset guard on top of the redesigned views.

## 0.52.0 - 2026-06-30

- Audit the commercial-beta request against the implemented repository and record verified versus manual-only release gates.
- Add a phased product roadmap that keeps hosted SaaS, mobile, ClearML operations, and production infrastructure as explicit future work.
- Add a UI/UX review with beta-blocking interaction findings and a minimum credible remediation scope.
- Replace dead sidebar links with native section navigation and remove enabled/visible controls that had no action.
- Replace static internal-service `ok` claims with observable dashboard data state.
- Add accessible success feedback for core task, event, schedule, export, and demo actions.
- Disable the demo-reset endpoint in production and cover the environment guard with an API regression test.
- Add explicit AWS deployment, ClearML promotion, security-control, and mobile-client decision documents without claiming those future systems are operational.
- Add a clean-checkout Docker runtime CI gate covering service startup, migrations, product E2E, browser smoke, MySQL restart persistence, backup verification, and isolated restore.
- Reconcile architecture, roadmap, beta readiness, project status, and release documentation with the verified v0.52.0 baseline.

## 0.51.4 - 2026-07-08

- Add the development workflow configuration under `.claude/` (coding rules, task tracking, review and testing commands, workflow templates).
- Add a root `CLAUDE.md` with project instructions, architecture summary, quality gates, and development guardrails.
- Add `docs/adr/` with four retroactive architecture decision records (service split, MySQL with in-memory test store, local-first runtime, ML artifact with heuristic fallback).
- Add a work-breakdown plan at `.claude/taskmaster-data/wbs.md` covering the remaining launch gaps (milestones M2-M4).
- Add a workflow gap audit (now at `docs/internal/vibecoding-gap-analysis.md`) recording what was added and what was deliberately deferred.
- Fix a security-audit false positive where filenames like `task-assignment-...` matched the OpenAI key pattern.

## 0.51.3 - 2026-06-20

- Rewrite the GitHub-facing README, architecture, and project specification into a tighter maintained-document style.
- Remove repeated commit-suggestion blocks from changelog and development history.
- Update documentation indexes and version references to the current MVP baseline.
- Record file cleanup candidates without deleting files that still need owner approval.

## 0.51.2 - 2026-06-20

- Fix authenticated dashboard JSON requests so `Content-Type: application/json` is preserved when `Authorization` headers are added.
- Restore the Generate plan flow, which was sending schedule payloads as plain text and triggering backend 422 validation errors.

## 0.51.1 - 2026-06-19

- Fix MySQL Alembic migration startup by replacing unsupported `ADD COLUMN IF NOT EXISTS` DDL with inspected `add_column` calls.
- Add a migration guard test to prevent the same MySQL-incompatible DDL from returning.
- Upgrade Vite to `6.4.3` and verify `npm audit` reports 0 vulnerabilities.
- Keep release QA output clean by disabling pytest cache writes inside the gate.
- Ignore TypeScript build artifacts generated by the dashboard build.

## 0.51.0 - 2026-06-19

- Add Ponytail clean gate for documentation completeness, release QA, and Git whitespace checks.
- Complete system analysis and documentation completeness matrix.
- Add GitHub-facing contribution, security, and support documents.
- Expand README with problem statement, core features, quick start, clean check, and documentation map.

## 0.50.0 - 2026-06-11

- Add beta readiness review and automated beta readiness check.
- Document remaining Issue 50 Docker finalization and Issue 51 hosted deployment gates.
- Keep the repository positioned as Customer Demo MVP / Technical Preview.

## 0.49.0 - 2026-06-11

- Add manual accessibility QA checklist for keyboard, screen reader, contrast, and responsive checks.
- Keep formal third-party accessibility audit out of the local MVP scope.

## 0.48.0 - 2026-06-11

- Add production backup policy audit.
- Document encryption, off-host storage, retention, restore approval, and temporary restore target requirements.
- Keep scheduled backup execution and cloud storage setup deferred until hosted deployment decisions exist.

## 0.47.0 - 2026-06-11

- Add hosted monitoring baseline plan.
- Add local monitoring probe for health and readiness endpoints.
- Keep hosted monitoring vendor configuration deferred.

## 0.46.0 - 2026-06-11

- Add auth hardening baseline with password policy, configurable token lifetime, production secret validation, and failed-login rate limiting.
- Extend auth and configuration tests.

## 0.45.0 - 2026-06-11

- Add non-Docker release QA gate for service tests, static audits, translation coverage, backup policy, and beta readiness checks.
- Keep frontend build and visual regression strictness configurable for environments without `npm` or reviewed screenshots.

## 0.44.0 - 2026-06-10

- Add local security audit script for common secret and private-key patterns.
- Add dependency update policy notes to QA and release documentation.
- Keep Docker hardening out of this issue batch per product direction.

## 0.43.0 - 2026-06-10

- Add deterministic PNG visual regression comparison script.
- Add local baseline update and threshold compare workflow under ignored artifacts.

## 0.42.0 - 2026-06-10

- Add non-Docker GitHub Actions browser smoke job using Vite preview.
- Upload browser smoke screenshots as CI artifacts.

## 0.41.0 - 2026-06-10

- Add completion forecast endpoint based on daily execution state and remaining workload.
- Add dashboard-ready API coverage for forecast QA.

## 0.40.0 - 2026-06-10

- Add duration feedback CSV export for completed tasks with actual minutes.
- Keep training data updates manual so local datasets are not overwritten automatically.

## 0.39.0 - 2026-06-10

- Add local JSON model registry abstraction to ml-service.
- Add `/model/registry` endpoint and registry example file.
- Preserve duration artifact and heuristic fallback behavior.

## 0.38.0 - 2026-06-10

- Add disabled-by-default ClearML local tracking baseline documentation.
- Clarify that real ClearML server and agent execution belongs to a later deployment phase.

## 0.37.0 - 2026-06-10

- Add a dashboard accessibility static audit script.
- Extend focus-visible styling to select controls.
- Label new schedule adjustment controls for keyboard and assistive technology use.

## 0.36.0 - 2026-06-10

- Add local PDF schedule export without paid APIs.
- Add dashboard PDF export button and base64 download handling.

## 0.35.0 - 2026-06-10

- Add named schedule template CRUD APIs.
- Persist reusable planning mode, start/end hour, buffer, and fixed-event inclusion settings.

## 0.34.0 - 2026-06-10

- Add weekly recurring fixed event expansion endpoint.
- Store recurrence metadata on generated dated fixed events.

## 0.33.0 - 2026-06-10

- Add schedule item locking and manual time adjustment APIs.
- Preserve locked schedule items during later schedule generation.
- Add dashboard timeline controls for lock, move earlier, and move later.
- Validate manual schedule adjustments against fixed-event conflicts.

## 0.32.0 - 2026-06-04

- Add dashboard language switcher with English as the default locale.
- Add Traditional Chinese dashboard UI copy for core navigation, controls, states, forms, analytics, and schedule views.
- Persist the selected dashboard language in local storage.
- Keep user-created task and event content unchanged.

## 0.31.0 - 2026-06-04

- Add non-destructive MySQL backup scripts for Windows PowerShell and Linux / WSL.
- Add backup verification scripts that reject empty files and destructive SQL statements.
- Add backup and restore drill runbook for temporary restore targets.
- Update QA and release documentation with backup verification checks.
- Harden browser screenshot smoke for Windows headless Edge/Chrome execution.

## 0.30.0 - 2026-06-04

- Add request ID propagation for backend-api, scheduler-service, and ml-service.
- Add structured JSON request logs without request bodies, query strings, authorization headers, cookies, or secret values.
- Add readiness endpoints for backend-api, scheduler-service, and ml-service.
- Add observability runbook and QA checks for local verification.

## 0.29.0 - 2026-06-04

- Add production environment template with blank secret values.
- Add Nginx reverse-proxy skeleton for future single-node deployment.
- Expand deployment documentation with account requirements, HTTPS plan, validation commands, and hosted smoke checklist.
- Keep Issue 30 deployment baseline account-free and local-verifiable.

## 0.28.0 - 2026-06-04

- Scope core planner APIs to the authenticated bearer-token user.
- Remove implicit `user_id=1` behavior from tasks, fixed events, schedules, execution logs, analytics, and predictions routes.
- Add cross-user isolation tests for tasks, fixed events, execution events, and schedule history export.
- Update dashboard and E2E smoke script to use demo bearer authentication.

## 0.27.0 - 2026-06-04

- Add local authentication foundation with register, login, and current-user APIs.
- Add PBKDF2 password hashing and HMAC bearer token signing without external paid services.
- Seed a local demo account for the bundled demo user.
- Add `users` persistence through memory store, MySQL bootstrap, and Alembic revision `20260604_0003`.
- Add dashboard account controls for demo login, register, login, and sign out.

## 0.26.0 - 2026-06-04

- Add backend runtime configuration validation.
- Share configuration parsing between backend runtime, MySQL repository, service clients, and Alembic.
- Expand `.env.example` and add environment configuration documentation.
- Set explicit `ORDOSTACK_ENV=local` in Docker Compose.
- Align project spec and PM report baseline references to Issue 27 / `v0.26.0`.

## 0.25.0 - 2026-06-04

- Add PM project status report with launch-readiness assessment.
- Correct documentation baseline references from Issue 20 to Issue 26.
- Correct QA migration expectation to Alembic revision `20260604_0002`.

## 0.24.0 - 2026-06-04

- Add local browser smoke script that captures a dashboard screenshot through headless Edge or Chrome.
- Extend E2E smoke coverage for schedule rename, diff, and export APIs.
- Ignore generated browser smoke artifacts.

## 0.23.0 - 2026-06-04

- Add schedule history export API for Markdown and CSV.
- Add dashboard Export MD action for the selected generated plan.
- Add backend tests for schedule export content and filenames.

## 0.22.0 - 2026-06-04

- Add backend schedule history diff endpoint for comparing two generated runs.
- Add dashboard Compare previous control and compact diff summary.
- Cover added, removed, changed, unchanged, and task-minute delta cases in tests.

## 0.21.0 - 2026-06-04

- Add schedule history titles for generated plans.
- Add API and dashboard controls to rename schedule history items.
- Add soft delete for schedule history items and exclude deleted runs from latest/history queries.
- Add Alembic migration for schedule history action fields.

## 0.20.0 - 2026-06-04

- Add dashboard task status, category, focus, and sort controls.
- Add active filter count and reset action for customer demo task triage.
- Keep filtering client-side without changing backend contracts.

## 0.19.0 - 2026-06-04

- Refresh the project specification to the current Customer Demo MVP baseline.
- Update architecture, demo, release, QA, README, changelog, and development-log documentation.
- Record current production-readiness gaps and next-phase scope.

## 0.18.0 - 2026-06-04

- Add local E2E smoke script for Docker Compose demo verification.
- Cover health checks, dashboard HTML, task edit, fixed event edit, schedule generation, and schedule history.
- Document the local E2E smoke workflow.

## 0.17.0 - 2026-06-04

- Add demo reset API for the bundled demo user.
- Add dashboard Reset demo control with confirmation.
- Add backend test coverage for restoring seeded demo data.

## 0.16.0 - 2026-06-04

- Add dashboard empty states for timeline, schedule history, and fixed events.
- Add Retry action to the error banner.
- Improve compact empty-state styling for demo usability.

## 0.15.0 - 2026-06-04

- Add schedule history API for recent generated plans.
- Add dashboard schedule history panel with selectable generated runs.
- Refresh schedule history after plan generation and date changes.

## 0.14.0 - 2026-06-04

- Add dashboard date picker for arbitrary date selection.
- Add Today shortcut beside previous and next day navigation.
- Close date-scoped forms and edit panels when the selected date changes.

## 0.13.0 - 2026-06-04

- Add fixed event update and soft delete APIs.
- Add dashboard inline fixed event editing and delete controls.
- Validate fixed event title, type, start time, and end time before create and update requests.

## 0.12.0 - 2026-06-03

- Add dashboard task editing for title, category, estimate, priority, difficulty, deadline time, and focus requirement.
- Reuse a shared task form component for create and edit flows.
- Add task form validation before create and update requests.
- Add inline edit controls in Task queue backed by `PATCH /api/tasks/{task_id}`.

## 0.11.0 - 2026-06-03

- Add dashboard previous day and next day navigation.
- Reload tasks, fixed events, analytics, duration predictions, and latest saved schedule by selected date.
- Create tasks and fixed events against the currently selected date.

## 0.10.1 - 2026-06-03

- Add `VERSION` file for release tracking.
- Add release process and baseline commit checklist.
- Establish the repository baseline plan for real branch-based development.

## 0.10.0 - 2026-06-03

- Add GitHub Actions CI workflow for Python services, web-dashboard build, and Docker Compose config validation.
- Add pull request template with verification checklist.
- Document branch naming and pull request flow.
- Update development rulebook with branch and CI expectations.

## 0.9.0 - 2026-06-03

- Add Alembic migration baseline for the current MySQL schema.
- Run `alembic upgrade head` before backend-api starts in Docker.
- Keep non-destructive fallback schema bootstrap for local compatibility.
- Document migration commands and current migration revision.

## 0.8.0 - 2026-06-03

- Persist generated schedule runs and schedule items in MySQL.
- Add `GET /api/schedules/latest` for the latest saved daily plan.
- Load latest saved schedule in the dashboard on startup.
- Add version history and development log records.

## 0.7.0 - 2026-06-03

- Add Docker Compose MySQL service.
- Add backend store selector for memory and MySQL.
- Persist tasks, fixed events, and execution logs in Docker.
- Add local database schema documentation.

## 0.6.0 - 2026-06-03

- Add local duration training dataset.
- Add training script and bundled JSON model artifact.
- Load `local-duration-regressor` in ml-service.

## 0.5.0 - 2026-06-02

- Add duration prediction endpoint.
- Wire backend duration predictions into schedule generation.
- Show estimated, predicted, and actual minutes in dashboard task rows.

## 0.4.0 - 2026-06-02

- Add task execution start, pause, complete, and skip endpoints.
- Add execution logs and daily analytics.
- Add dashboard execution controls and actual-time metrics.

## 0.3.0 - 2026-06-02

- Add scheduler-service schedule generation endpoint.
- Add backend schedule proxy endpoint.
- Render generated schedules in dashboard.

## 0.2.0 - 2026-06-02

- Add task and fixed event APIs.
- Add seeded in-memory repository.
- Wire dashboard task and fixed event workflows.

## 0.1.0 - 2026-06-02

- Initialize repository structure.
- Add service skeletons and health endpoints.
- Add Docker Compose skeleton and dashboard landing page.
