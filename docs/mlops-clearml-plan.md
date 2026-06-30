# ClearML MLOps Plan

ClearML is optional future infrastructure. OrdoStack currently works with a local JSON model artifact and deterministic heuristic fallback; no ClearML server or agent is running.

## Current Local Contract

- Training input: reviewed CSV under `ml-service/training/data/`.
- Training command: `python training/train_duration_model.py` from `ml-service`.
- Outputs: versioned model metadata and evaluation metrics under `ml-service/training/artifacts/`.
- Runtime: `ml-service` loads the selected local artifact, then falls back to the heuristic when unavailable.
- Feedback: backend API exports completed-task duration feedback for manual review.

## ClearML Mapping

| Local concept | Future ClearML object |
| --- | --- |
| Training CSV | Dataset artifact with source and review date |
| Training run | Task named `duration-training/<date>/<git-sha>` |
| Parameters | Feature names, weights, model version, row count |
| Metrics | Baseline MAE and model MAE |
| Model JSON | Output model registered after validation |
| Runtime selection | Approved model version copied to the local artifact contract |

## Promotion Workflow

1. Export and review feedback data; remove invalid or sensitive rows.
2. Create a versioned dataset artifact.
3. Run training reproducibly against a tagged code revision.
4. Compare model MAE with the current approved model and baseline.
5. Review feature compatibility and prediction bounds.
6. Approve the candidate manually.
7. Promote by updating the registry entry and deploy the artifact to staging.
8. Run artifact and fallback prediction tests before beta traffic.
9. Record rollback to the previous artifact version.

## Configuration

The blank `CLEARML_*` variables in `.env.production.example` are examples only. Real values belong in the selected secret store. The product must continue to start and predict without ClearML credentials.

## Deferred Work

- ClearML server selection and cost ownership.
- Agent queue and worker deployment.
- Dataset retention and access policy.
- Automated model promotion or online serving.
- Drift monitoring and retraining cadence.

Add these only after training frequency, data ownership, and an operator are defined. See `docs/clearml-mlops.md` for the local artifact details.
