# ClearML MLOps

Issue 5 adds a local duration prediction MVP through `ml-service`. Issue 6 adds a local training artifact workflow. Neither step requires ClearML credentials or calls any paid API.

Issue 39 adds a disabled-by-default local ClearML tracking baseline. It records the intended experiment metadata shape but does not require a ClearML account, server, agent, or paid API. Credentials must not be committed.

Current ML boundary:

- `ml-service` owns duration prediction logic.
- `backend-api` forwards task features and execution actual minutes.
- `scheduler-service` consumes `predicted_minutes` when available.
- Dashboard displays predicted minutes and model metadata.

## Local Training Artifact MVP

Windows PowerShell:

```powershell
cd ml-service
..\.venv\Scripts\python.exe training\train_duration_model.py
```

Linux / WSL:

```bash
cd ml-service
../.venv/bin/python training/train_duration_model.py
```

Outputs:

- `training/artifacts/duration_model.json`
- `training/artifacts/duration_metrics.json`

The Docker image copies `ml-service/training` so `ml-service` can load `training/artifacts/duration_model.json` at runtime. If the artifact is missing, it falls back to `heuristic-duration`.

Current artifact metrics:

```json
{
  "baseline_mae": 14.14,
  "model_mae": 6.57,
  "training_rows": 14
}
```

## Optional ClearML Local Tracking Baseline

No account is required for this issue.

Local metadata to track before a real ClearML server exists:

- `project_name`: `OrdoStack`
- `task_name`: training script name and date
- `model_name`: active duration model name
- `model_version`: semantic model version
- `metrics`: `baseline_mae`, `model_mae`, `training_rows`
- `artifacts`: model JSON, metrics JSON, and future registry entry

When ClearML is introduced later, the local metadata should map directly to ClearML Task parameters, scalar metrics, and artifact uploads. Until then, keep tracking disabled and do not add credentials to Git.

## Local Model Registry Baseline

Issue 40 adds a local JSON registry abstraction:

- Example: `ml-service/training/artifacts/model_registry.example.json`
- Runtime endpoint: `GET /model/registry`
- Fallback: if no registry exists, `ml-service` continues to use `duration_model.json`, then `heuristic-duration`.

This is intentionally local-only and does not require Docker or hosted infrastructure.

## Duration Feedback Loop

Issue 41 adds a backend export endpoint for completed task feedback:

```text
GET /api/ml/duration-feedback?target_date=YYYY-MM-DD
```

The endpoint returns CSV rows for completed tasks with actual minutes, suitable for appending to the local training dataset after review.
