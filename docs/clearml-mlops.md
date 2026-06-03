# ClearML MLOps

Issue 5 adds a local duration prediction MVP through `ml-service`. Issue 6 adds a local training artifact workflow. Neither step requires ClearML credentials or calls any paid API.

ClearML training tasks, metrics, artifacts, and model registry workflow are planned for a later issue. Credentials must not be committed.

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
