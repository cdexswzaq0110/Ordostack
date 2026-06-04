# Changelog

All notable MVP changes are recorded here. This project follows incremental issue-based delivery.

## 0.30.0 - 2026-06-04

- Add request ID propagation for backend-api, scheduler-service, and ml-service.
- Add structured JSON request logs without request bodies, query strings, authorization headers, cookies, or secret values.
- Add readiness endpoints for backend-api, scheduler-service, and ml-service.
- Add observability runbook and QA checks for local verification.

Suggested commit:

```text
feat(observability): add request readiness baseline
```

## 0.29.0 - 2026-06-04

- Add production environment template with blank secret values.
- Add Nginx reverse-proxy skeleton for future single-node deployment.
- Expand deployment documentation with account requirements, HTTPS plan, validation commands, and hosted smoke checklist.
- Keep Issue 30 deployment baseline account-free and local-verifiable.

Suggested commit:

```text
docs(deploy): add deployment baseline
```

## 0.28.0 - 2026-06-04

- Scope core planner APIs to the authenticated bearer-token user.
- Remove implicit `user_id=1` behavior from tasks, fixed events, schedules, execution logs, analytics, and predictions routes.
- Add cross-user isolation tests for tasks, fixed events, execution events, and schedule history export.
- Update dashboard and E2E smoke script to use demo bearer authentication.

Suggested commit:

```text
feat(auth): scope planner data to current user
```

## 0.27.0 - 2026-06-04

- Add local authentication foundation with register, login, and current-user APIs.
- Add PBKDF2 password hashing and HMAC bearer token signing without external paid services.
- Seed a local demo account for the bundled demo user.
- Add `users` persistence through memory store, MySQL bootstrap, and Alembic revision `20260604_0003`.
- Add dashboard account controls for demo login, register, login, and sign out.

Suggested commit:

```text
feat(auth): add local authentication foundation
```

## 0.26.0 - 2026-06-04

- Add backend runtime configuration validation.
- Share configuration parsing between backend runtime, MySQL repository, service clients, and Alembic.
- Expand `.env.example` and add environment configuration documentation.
- Set explicit `ORDOSTACK_ENV=local` in Docker Compose.
- Align project spec and PM report baseline references to Issue 27 / `v0.26.0`.

Suggested commit:

```text
chore(config): harden environment validation
```

## 0.25.0 - 2026-06-04

- Add PM project status report with launch-readiness assessment.
- Correct documentation baseline references from Issue 20 to Issue 26.
- Correct QA migration expectation to Alembic revision `20260604_0002`.

Suggested commit:

```text
docs(pm): add project status report
```

## 0.24.0 - 2026-06-04

- Add local browser smoke script that captures a dashboard screenshot through headless Edge or Chrome.
- Extend E2E smoke coverage for schedule rename, diff, and export APIs.
- Ignore generated browser smoke artifacts.

Suggested commit:

```text
test(browser): add dashboard screenshot smoke
```

## 0.23.0 - 2026-06-04

- Add schedule history export API for Markdown and CSV.
- Add dashboard Export MD action for the selected generated plan.
- Add backend tests for schedule export content and filenames.

Suggested commit:

```text
feat(schedule): add schedule export
```

## 0.22.0 - 2026-06-04

- Add backend schedule history diff endpoint for comparing two generated runs.
- Add dashboard Compare previous control and compact diff summary.
- Cover added, removed, changed, unchanged, and task-minute delta cases in tests.

Suggested commit:

```text
feat(schedule): add schedule history diff
```

## 0.21.0 - 2026-06-04

- Add schedule history titles for generated plans.
- Add API and dashboard controls to rename schedule history items.
- Add soft delete for schedule history items and exclude deleted runs from latest/history queries.
- Add Alembic migration for schedule history action fields.

Suggested commit:

```text
feat(schedule): add history rename and delete actions
```

## 0.20.0 - 2026-06-04

- Add dashboard task status, category, focus, and sort controls.
- Add active filter count and reset action for customer demo task triage.
- Keep filtering client-side without changing backend contracts.

Suggested commit:

```text
feat(dashboard): add task filters and sorting
```

## 0.19.0 - 2026-06-04

- Refresh the project specification to the current Customer Demo MVP baseline.
- Update architecture, demo, release, QA, README, changelog, and development-log documentation.
- Record current production-readiness gaps and next-phase scope.

Suggested commit:

```text
docs(product): refresh demo mvp specification
```

## 0.18.0 - 2026-06-04

- Add local E2E smoke script for Docker Compose demo verification.
- Cover health checks, dashboard HTML, task edit, fixed event edit, schedule generation, and schedule history.
- Document the local E2E smoke workflow.

Suggested commit:

```text
test(e2e): add local smoke workflow
```

## 0.17.0 - 2026-06-04

- Add demo reset API for the bundled demo user.
- Add dashboard Reset demo control with confirmation.
- Add backend test coverage for restoring seeded demo data.

Suggested commit:

```text
feat(demo): add demo data reset control
```

## 0.16.0 - 2026-06-04

- Add dashboard empty states for timeline, schedule history, and fixed events.
- Add Retry action to the error banner.
- Improve compact empty-state styling for demo usability.

Suggested commit:

```text
feat(dashboard): polish demo empty states
```

## 0.15.0 - 2026-06-04

- Add schedule history API for recent generated plans.
- Add dashboard schedule history panel with selectable generated runs.
- Refresh schedule history after plan generation and date changes.

Suggested commit:

```text
feat(schedule): add schedule history view
```

## 0.14.0 - 2026-06-04

- Add dashboard date picker for arbitrary date selection.
- Add Today shortcut beside previous and next day navigation.
- Close date-scoped forms and edit panels when the selected date changes.

Suggested commit:

```text
feat(dashboard): add date picker navigation
```

## 0.13.0 - 2026-06-04

- Add fixed event update and soft delete APIs.
- Add dashboard inline fixed event editing and delete controls.
- Validate fixed event title, type, start time, and end time before create and update requests.

Suggested commit:

```text
feat(fixed-events): add edit and delete workflows
```

## 0.12.0 - 2026-06-03

- Add dashboard task editing for title, category, estimate, priority, difficulty, deadline time, and focus requirement.
- Reuse a shared task form component for create and edit flows.
- Add task form validation before create and update requests.
- Add inline edit controls in Task queue backed by `PATCH /api/tasks/{task_id}`.

Suggested commit:

```text
feat(tasks): add dashboard task editing
```

## 0.11.0 - 2026-06-03

- Add dashboard previous day and next day navigation.
- Reload tasks, fixed events, analytics, duration predictions, and latest saved schedule by selected date.
- Create tasks and fixed events against the currently selected date.

Suggested commit:

```text
feat(dashboard): add date navigation
```

## 0.10.1 - 2026-06-03

- Add `VERSION` file for release tracking.
- Add release process and baseline commit checklist.
- Establish the repository baseline plan for real branch-based development.

Suggested commit:

```text
chore(repo): establish ordostack mvp baseline
```

## 0.10.0 - 2026-06-03

- Add GitHub Actions CI workflow for Python services, web-dashboard build, and Docker Compose config validation.
- Add pull request template with verification checklist.
- Document branch naming and pull request flow.
- Update development rulebook with branch and CI expectations.

Suggested commit:

```text
ci(github): add quality gate workflow
```

## 0.9.0 - 2026-06-03

- Add Alembic migration baseline for the current MySQL schema.
- Run `alembic upgrade head` before backend-api starts in Docker.
- Keep non-destructive fallback schema bootstrap for local compatibility.
- Document migration commands and current migration revision.

Suggested commit:

```text
chore(db): add alembic migration baseline
```

## 0.8.0 - 2026-06-03

- Persist generated schedule runs and schedule items in MySQL.
- Add `GET /api/schedules/latest` for the latest saved daily plan.
- Load latest saved schedule in the dashboard on startup.
- Add version history and development log records.

Suggested commit:

```text
feat(schedule): persist generated schedule runs
```

## 0.7.0 - 2026-06-03

- Add Docker Compose MySQL service.
- Add backend store selector for memory and MySQL.
- Persist tasks, fixed events, and execution logs in Docker.
- Add local database schema documentation.

Suggested commit:

```text
feat(storage): add mysql persistence for mvp data
```

## 0.6.0 - 2026-06-03

- Add local duration training dataset.
- Add training script and bundled JSON model artifact.
- Load `local-duration-regressor` in ml-service.

Suggested commit:

```text
feat(ml): add local duration training artifact
```

## 0.5.0 - 2026-06-02

- Add duration prediction endpoint.
- Wire backend duration predictions into schedule generation.
- Show estimated, predicted, and actual minutes in dashboard task rows.

Suggested commit:

```text
feat(ml): add duration prediction mvp
```

## 0.4.0 - 2026-06-02

- Add task execution start, pause, complete, and skip endpoints.
- Add execution logs and daily analytics.
- Add dashboard execution controls and actual-time metrics.

Suggested commit:

```text
feat(analytics): track task execution logs
```

## 0.3.0 - 2026-06-02

- Add scheduler-service schedule generation endpoint.
- Add backend schedule proxy endpoint.
- Render generated schedules in dashboard.

Suggested commit:

```text
feat(schedule): generate daily plans
```

## 0.2.0 - 2026-06-02

- Add task and fixed event APIs.
- Add seeded in-memory repository.
- Wire dashboard task and fixed event workflows.

Suggested commit:

```text
feat(tasks): add task and fixed event mvp
```

## 0.1.0 - 2026-06-02

- Initialize repository structure.
- Add service skeletons and health endpoints.
- Add Docker Compose skeleton and dashboard landing page.

Suggested commit:

```text
chore(repo): initialize ordostack skeleton
```
