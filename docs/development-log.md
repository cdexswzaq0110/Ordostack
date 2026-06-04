# Development Log

## 2026-06-04 - Issue 24 - Schedule Export MVP

Branch:

```text
feature/issue-24-schedule-export
```

Scope:

- Add schedule history export API for Markdown and CSV.
- Add dashboard Export MD action for the selected generated plan.
- Generate filenames and text content from persisted schedule history.

MVP boundaries:

- Export is text-based only.
- No PDF export.
- No cloud share link.

Suggested git commit:

```text
feat(schedule): add schedule export
```

Verification:

- Schedule API tests must pass locally.
- web-dashboard production build must pass.

## 2026-06-04 - Issue 23 - Schedule Diff MVP

Branch:

```text
feature/issue-23-schedule-diff
```

Scope:

- Add schedule history diff API for comparing a selected run with another run.
- Add dashboard Compare previous action.
- Show added, removed, changed, unchanged, and task-minute delta summary.

MVP boundaries:

- Diff is read-only.
- Diff compares generated schedule items, not raw task field history.
- No side-by-side timeline view yet.

Suggested git commit:

```text
feat(schedule): add schedule history diff
```

Verification:

- Schedule API tests must pass locally.
- web-dashboard production build must pass.

## 2026-06-04 - Issue 22 - Schedule History Actions MVP

Branch:

```text
feature/issue-22-schedule-history-actions
```

Scope:

- Add title metadata to generated schedule runs.
- Add schedule history rename API and dashboard inline rename control.
- Add schedule history soft delete API and dashboard delete control.
- Exclude soft-deleted runs from latest and history queries.
- Add Alembic migration for `schedule_runs.title`, `updated_at`, and `deleted_at`.

MVP boundaries:

- Soft delete only; no hard delete UI.
- No schedule diff yet.
- No named schedule templates.

Suggested git commit:

```text
feat(schedule): add history rename and delete actions
```

Verification:

- Schedule API tests must pass locally.
- web-dashboard production build must pass.

## 2026-06-04 - Issue 21 - Task Filter And Sort MVP

Branch:

```text
feature/issue-21-task-filter-sort
```

Scope:

- Add task queue filters for status, category, and focus requirement.
- Add task queue sorting by priority, deadline, estimate, or status.
- Add active filter count and reset action.

MVP boundaries:

- Client-side filtering only.
- No saved user filter presets.
- No backend query contract changes.

Suggested git commit:

```text
feat(dashboard): add task filters and sorting
```

Verification:

- web-dashboard production build must pass.

## 2026-06-04 - Issue 20 - Demo MVP Documentation Baseline

Branch:

```text
feature/issue-20-docs-refresh
```

Scope:

- Refresh the project specification to the current Customer Demo MVP baseline.
- Update architecture documentation for current runtime boundaries, persistence, and data flow.
- Update demo, release, QA, README, changelog, and development-log records for version `0.19.0`.

MVP boundaries:

- Documentation-only issue.
- No production deployment work.
- No new product behavior.

Suggested git commit:

```text
docs(product): refresh demo mvp specification
```

Verification:

- Documentation diff must not introduce secrets.
- Full release checklist should pass before tagging `v0.19.0`.

## 2026-06-04 - Issue 19 - E2E Smoke Workflow MVP

Branch:

```text
feature/issue-19-e2e-smoke
```

Scope:

- Add local E2E smoke script for Docker Compose demo verification.
- Verify service health, dashboard HTML, task edit, fixed event edit, schedule generation, and schedule history.
- Document smoke script usage.

MVP boundaries:

- No headless browser screenshot test yet.
- No GitHub Actions Docker runtime E2E yet.
- Smoke script creates local test records and does not clean them up.

Suggested git commit:

```text
test(e2e): add local smoke workflow
```

Verification:

- Run after `docker compose up --build -d`.
- Script must exit with status code `0`.

## 2026-06-04 - Issue 18 - Demo Seed And Reset Control MVP

Branch:

```text
feature/issue-18-demo-reset
```

Scope:

- Add demo-only reset API for the bundled demo user.
- Add dashboard Reset demo control with confirmation.
- Restore seeded tasks, fixed events, and execution sample data.

MVP boundaries:

- Demo reset is not a production user-data feature.
- No per-tenant data retention policy.
- No cloud backup restore flow.

Suggested git commit:

```text
feat(demo): add demo data reset control
```

Verification:

- Demo API tests must pass locally.
- web-dashboard production build must pass.
- Browser smoke should verify the Reset demo button renders and prompts for confirmation.

## 2026-06-04 - Issue 17 - Dashboard UX Polish MVP

Branch:

```text
feature/issue-17-dashboard-ux-polish
```

Scope:

- Add empty states for timeline, schedule history, and fixed events.
- Add Retry action to the dashboard error banner.
- Improve compact empty-state styling for demo usability.

MVP boundaries:

- No full redesign.
- No new design system package.
- No animation-heavy marketing UI.

Suggested git commit:

```text
feat(dashboard): polish demo empty states
```

Verification:

- web-dashboard production build must pass.
- Browser smoke should verify no-data dates render coherent empty states.

## 2026-06-04 - Issue 16 - Schedule History Management MVP

Branch:

```text
feature/issue-16-schedule-history
```

Scope:

- Add schedule history API for recent generated schedule runs.
- Add dashboard schedule history panel.
- Allow users to switch the timeline to a previous generated plan.
- Refresh history after plan generation and date changes.

MVP boundaries:

- No schedule diff view.
- No schedule deletion.
- No named schedule versions.

Suggested git commit:

```text
feat(schedule): add schedule history view
```

Verification:

- Schedule API tests must pass locally.
- web-dashboard production build must pass.
- Browser smoke must verify generating multiple plans and selecting a history row.

## 2026-06-04 - Issue 15 - Date Picker Navigation MVP

Branch:

```text
feature/issue-15-date-picker
```

Scope:

- Add date picker for arbitrary dashboard date selection.
- Add Today shortcut next to previous and next day navigation.
- Close date-scoped create/edit panels when selected date changes.

MVP boundaries:

- No week or month calendar view.
- No recurring event expansion.
- No timezone settings UI.

Suggested git commit:

```text
feat(dashboard): add date picker navigation
```

Verification:

- web-dashboard production build must pass.
- Browser smoke must verify date picker and Today shortcut reload date-scoped data.

## 2026-06-04 - Issue 14 - Fixed Event Editing MVP

Branch:

```text
feature/issue-14-fixed-event-editing
```

Scope:

- Add fixed event update and soft delete APIs.
- Add inline fixed event editing in the dashboard Protected time panel.
- Add fixed event delete controls backed by soft delete.
- Validate fixed event title, type, and `HH:MM` time ranges before create and update.

MVP boundaries:

- No recurring fixed events.
- No drag-and-drop schedule editing.
- No calendar sync.

Suggested git commit:

```text
feat(fixed-events): add edit and delete workflows
```

Verification:

- Fixed event API tests must pass locally.
- web-dashboard production build must pass.
- Docker Compose services must remain healthy.
- Browser smoke must verify fixed event edit and delete.

## 2026-06-03 - Issue 13 - Task Editing MVP

Branch:

```text
feature/issue-13-task-editing
```

Scope:

- Add inline task editing in the dashboard Task queue.
- Support editing title, category, estimate, priority, difficulty, deadline time, and focus requirement.
- Reuse a shared task form field component for create and edit flows.
- Save edits through the existing backend `PATCH /api/tasks/{task_id}` endpoint.

MVP boundaries:

- No drag-and-drop ordering.
- No batch edit.
- No recurring task edit workflow.
- No arbitrary date picker.

Suggested git commit:

```text
feat(tasks): add dashboard task editing
```

Verification:

- Python service tests must pass locally.
- `docker compose config` must pass locally.
- web-dashboard production build must pass.
- Browser smoke must verify task edit, save, and visible refresh.

## 2026-06-03 - Issue 12 - Date Navigation MVP

Branch:

```text
feature/issue-12-date-navigation
```

Scope:

- Replace hard-coded dashboard date usage with selected date state.
- Enable previous day and next day navigation.
- Reload date-scoped API data when selected date changes.
- Ensure task and fixed event creation uses the selected date.

MVP boundaries:

- No week or month calendar view.
- No arbitrary date picker yet.
- No cross-day recurring events.

Suggested git commit:

```text
feat(dashboard): add date navigation
```

Verification:

- Python service tests must pass locally.
- `docker compose config` must pass locally.
- web-dashboard production build must pass.
- Browser smoke must verify previous and next day navigation.

## 2026-06-03 - Issue 11 - Repository Baseline And Release Process

Branch:

```text
feature/issue-10-ci-quality-gate
```

Scope:

- Add `VERSION` file.
- Add release process documentation.
- Establish the first Git baseline commit for future branch-based development.
- Keep current product functionality unchanged.

MVP boundaries:

- No deployment tag is pushed.
- No GitHub branch protection is configured locally.
- No files or database volumes are deleted.

Suggested git commit:

```text
chore(repo): establish ordostack mvp baseline
```

Verification:

- Python service tests must pass locally.
- `docker compose config` must pass locally.
- Existing runtime smoke must remain healthy.
- Secrets scan must not find real credentials.

## 2026-06-03 - Issue 10 - CI Quality Gate MVP

Branch:

```text
feature/issue-10-ci-quality-gate
```

Scope:

- Add GitHub Actions CI checks for backend-api, scheduler-service, ml-service, web-dashboard, and Docker Compose config.
- Add pull request template.
- Add branching strategy documentation.
- Update development rulebook with branch and CI expectations.

MVP boundaries:

- CI validates build/test/config only.
- No full Docker runtime e2e in GitHub Actions yet.
- No deployment pipeline yet.

Suggested git commit:

```text
ci(github): add quality gate workflow
```

Verification:

- Python service tests must pass locally.
- `docker compose config` must pass locally.
- Existing Docker Compose runtime smoke must remain healthy.

## 2026-06-03 - Issue 9 - Database Migration Baseline

Scope:

- Add Alembic configuration to backend-api.
- Add initial idempotent migration for the current MySQL schema.
- Run migrations before backend-api starts in Docker.
- Keep downgrade non-destructive for MVP safety.

MVP boundaries:

- No destructive downgrade.
- No SQLAlchemy ORM refactor yet.
- No production credential management.

Suggested git commit:

```text
chore(db): add alembic migration baseline
```

Verification:

- Backend tests must pass.
- Docker Compose must build successfully.
- `docker compose exec backend-api alembic current` must show `20260603_0001`.
- Existing API health and schedule latest checks must still pass.

## 2026-06-03 - Issue 8 - Generated Schedule Persistence MVP

Scope:

- Persist generated schedules after `POST /api/schedules/generate`.
- Add `GET /api/schedules/latest` for the latest saved plan.
- Load the latest saved schedule in the dashboard on startup.
- Keep schedule history append-only for now.

MVP boundaries:

- No schedule editing.
- No schedule version comparison UI.
- No deletion or cleanup job.
- No production migration chain yet.

Suggested git commit:

```text
feat(schedule): persist generated schedule runs
```

Verification:

- Backend tests must pass.
- Docker Compose must build and report all services healthy.
- `GET /api/schedules/latest` must return a generated schedule after `POST /api/schedules/generate`.

## 2026-06-03 - Issue 7 - MySQL Persistence MVP

Scope:

- Add local MySQL service.
- Persist tasks, fixed events, and execution logs.
- Keep local tests on memory store by default.

Suggested git commit:

```text
feat(storage): add mysql persistence for mvp data
```
