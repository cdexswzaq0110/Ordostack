# Development Log

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
