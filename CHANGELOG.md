# Changelog

All notable MVP changes are recorded here. This project follows incremental issue-based delivery.

## 0.53.0 - 2026-07-09

- Redesign the dashboard with a warm editorial design system: ink/warm/canvas palette, display typography with letter-spaced uppercase labels, hairline borders, and square corners throughout.
- Make the sidebar navigation functional: Today, Tasks, Schedule, Analytics, MLOps, and Settings now switch dedicated workspace views.
- Add an Analytics view with a per-task estimate / predicted / actual / delta table.
- Add an MLOps view showing the active prediction model, per-task predictions with confidence, and how the fallback chain works.
- Add a Settings view with account details, interface language, keyboard shortcut reference, and demo reset; the top bar keeps only date, search, account, and Generate Plan.
- Replace the fabricated plan score with real schedule coverage (scheduled vs selected tasks) in the plan-quality ring.
- Label unscheduled timeline previews explicitly and remove the remaining non-functional buttons (notifications, command palette, more-options).
- Make the bottom rail honest: the next fixed event is now computed from the current time and the third slot shows the active prediction model.
- Refresh the visual regression baseline and all README screenshots for the new design.

## 0.52.0 - 2026-07-08

- Close the local ML retraining loop: `scripts/export_duration_feedback.py` pulls completed-task feedback, training merges it with seed data, and `promote_duration_model.py` performs metrics-gated promotion into the local JSON model registry.
- Report honest out-of-sample metrics: training now uses a seeded holdout split and records baseline MAE, model MAE, and improvement ratio instead of in-sample error.
- Add `POST /model/reload` to ml-service so a promoted artifact serves without a container restart.
- Add delete confirmations for tasks and fixed events in the dashboard.
- Replace hardcoded model version text in the plan-quality panel with the real duration-model name and version plus applied scheduler algorithm count.
- Highlight the current schedule block with a Now badge that refreshes every minute.
- Add keyboard shortcuts: Alt+Left/Right for day navigation, Alt+T for today, Alt+G for plan generation.
- Document the frontend UX roadmap (`docs/frontend-ux-improvement-plan.md`) and the MLOps production launch roadmap (`docs/mlops-production-roadmap.md`).
- Expand ml-service tests from 11 to 19 covering holdout metrics, feedback merge, determinism, promotion gates, and hot reload.
- Add a verification test report (`docs/test-report.md`) with the full v0.52.0 evidence: 89 unit/integration tests, static gates, and Docker runtime checks.
- Rewrite the README introduction and installation guide with real dashboard screenshots (`docs/images/`), a requirements table, first-login walkthrough, and troubleshooting notes.
- Add `scripts/capture_readme_screenshots.py` to reproduce the README screenshots against the running stack.
- Move development-history and planning documents (rulebooks, development log, status report, beta-readiness review, branching notes, UX plan, MLOps roadmap) into `docs/internal/` so the top-level docs stay product-facing.

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
