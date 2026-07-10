# ClearML MLOps

Issue 5 adds a local duration prediction MVP through `ml-service`. Issue 6 adds a local training artifact workflow. Neither step requires ClearML credentials or calls any paid API.

As of v0.54.0 the ClearML integration is implemented and optional. Training and promotion record tasks, parameters, metrics, and artifacts to ClearML when `ORDOSTACK_CLEARML_ENABLED=1`; with `CLEARML_OFFLINE_MODE=1` the SDK stores sessions locally without an account or server. The integration degrades to a no-op on any failure, so the local loop never depends on it. Setup commands live in [clearml/README.md](../clearml/README.md). Credentials must not be committed.

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

Current artifact metrics (seeded holdout split, out-of-sample):

```json
{
  "baseline_mae": 7.33,
  "model_mae": 4.33,
  "improvement_ratio": 0.4093,
  "evaluation_mode": "holdout",
  "training_rows": 11,
  "evaluation_rows": 3
}
```

## Optional ClearML Tracking

Implemented in `ml-service/training/clearml_utils.py` and wired into training
and promotion. What each run records:

- `project_name`: `OrdoStack`
- training task: `duration-training <timestamp>` with parameters (`model_name`, `model_version`, `seed`, `training_rows`, `feedback_rows`), scalar metrics (`baseline_mae`, `model_mae`, `improvement_ratio`), and artifacts (model JSON, metrics JSON, dataset CSVs)
- promotion task: `duration-promotion <timestamp>` tagged `promoted`, registering the versioned artifact as an output model (task artifact in offline mode)

Enable with `ORDOSTACK_CLEARML_ENABLED=1`; add `CLEARML_OFFLINE_MODE=1` to run
without an account or server. Tracking stays off by default and never blocks
the loop. Do not add credentials to Git.

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
