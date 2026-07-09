# Branching Strategy

OrdoStack uses short-lived feature branches.

## Branch Names

- `feature/issue-<number>-<short-name>` for product features.
- `fix/issue-<number>-<short-name>` for bug fixes.
- `chore/issue-<number>-<short-name>` for infrastructure, CI, dependency, and maintenance work.
- `docs/issue-<number>-<short-name>` for documentation-only changes.

Current branch for Issue 10:

```text
feature/issue-10-ci-quality-gate
```

## Flow

1. Create or switch to an issue branch.
2. Keep the branch focused on one issue.
3. Update tests and documentation with the change.
4. Run local verification before opening a pull request.
5. Open a pull request into `main`.
6. Merge only after CI passes.

## Commit Messages

Use Conventional Commits:

```text
feat(schedule): persist generated schedule runs
fix(api): reject invalid fixed event ranges
chore(db): add alembic migration baseline
ci(github): add quality gate workflow
docs(process): document branching strategy
```

## Main Branch

`main` should represent a runnable MVP. Direct product work should not happen on `main` after the repository has an initial baseline commit.

## Local Verification

Windows PowerShell:

```powershell
cd backend-api
..\.venv\Scripts\python.exe -m pytest tests
cd ..\scheduler-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..\ml-service
..\.venv\Scripts\python.exe -m pytest tests
cd ..
docker compose config
docker compose up --build -d
```

Linux / WSL:

```bash
cd backend-api
../.venv/bin/python -m pytest tests
cd ../scheduler-service
../.venv/bin/python -m pytest tests
cd ../ml-service
../.venv/bin/python -m pytest tests
cd ..
docker compose config
docker compose up --build -d
```
