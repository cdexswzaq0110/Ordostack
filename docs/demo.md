# Demo

This is the local Customer Demo MVP flow for OrdoStack 0.19.0.

## Start

Windows PowerShell:

```powershell
docker compose up --build -d
```

Linux / WSL:

```bash
docker compose up --build -d
```

Open:

```text
http://localhost:5173
```

## Demo Script

1. Confirm the dashboard loads without a red error banner.
2. Review the selected date control, Task queue, Protected time, Plan quality, AI review, and Today timeline.
3. Add a task for the selected date.
4. Edit the task title, estimate, priority, or deadline time.
5. Add a fixed event for the selected date.
6. Edit the fixed event title or time range.
7. Click `Generate Plan`.
8. Confirm the timeline shows generated task blocks and protected fixed-event blocks.
9. Confirm the AI review panel shows the scheduler algorithm summary.
10. Generate another plan.
11. Select an older item from Recent generated plans.
12. Complete, pause, skip, or reopen a task and review the analytics change.
13. Select a date with no records and confirm empty states render correctly.
14. Use Reset demo only when the local demo dataset should be restored.

## Automated Smoke

After Docker Compose is running:

Windows PowerShell:

```powershell
python scripts\e2e_smoke.py
```

Linux / WSL:

```bash
python scripts/e2e_smoke.py
```

Expected:

- Output contains `"status": "ok"`.
- Script exits with status code `0`.
- Local smoke task and fixed-event records are created for traceability.

## Demo Reset

The dashboard Reset demo button calls:

```text
POST http://localhost:8000/api/demo/reset?user_id=1
```

This endpoint is demo-only. It restores the bundled demo user's seeded tasks, fixed events, and execution samples. It is not a production user-data recovery feature.
