# ClearML MLOps Plan

ClearML is optional infrastructure. OrdoStack works with a local JSON model artifact and deterministic heuristic fallback; no ClearML server or agent is required. As of v0.54.0 the SDK integration is implemented (see [clearml/README.md](../clearml/README.md)): training and promotion record tasks, metrics, and artifacts when `ORDOSTACK_CLEARML_ENABLED=1`, verified end to end in offline mode.

## Current Local Contract

- Training input: reviewed CSV under `ml-service/training/data/`.
- Training command: `python training/train_duration_model.py` from `ml-service`.
- Outputs: versioned model metadata and evaluation metrics under `ml-service/training/artifacts/`.
- Runtime: `ml-service` loads the selected local artifact, then falls back to the heuristic when unavailable.
- Feedback: backend API exports completed-task duration feedback for manual review.

## ClearML Mapping

| Local concept | ClearML object | Status |
| --- | --- | --- |
| Training CSV | Dataset artifacts uploaded with each training task | Implemented |
| Training run | Task named `duration-training <timestamp>` | Implemented |
| Parameters | Model name/version, seed, training and feedback row counts | Implemented |
| Metrics | Baseline MAE, model MAE, improvement ratio (holdout) | Implemented |
| Model JSON | Output model registered on gate-passing promotion | Implemented (task artifact in offline mode) |
| Runtime selection | Approved model version copied to the local artifact contract | Local JSON registry remains authoritative |

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

Tracking is opt-in via `ORDOSTACK_CLEARML_ENABLED=1`; `CLEARML_OFFLINE_MODE=1` records local sessions with no account or server. The blank `CLEARML_API_*` variables in `.env.production.example` document the SDK's server credentials and are examples only; real values belong in the selected secret store. The product must continue to start and predict without ClearML credentials — the integration degrades to a no-op and the local JSON registry stays authoritative.

## Deferred Work

- ClearML server selection and cost ownership (self-hosted bring-up steps are documented in `clearml/README.md`).
- Agent queue and worker deployment.
- Dataset retention and access policy.
- Automated model promotion or online serving.
- Drift monitoring and retraining cadence.

Add these only after training frequency, data ownership, and an operator are defined. See `docs/clearml-mlops.md` for the local artifact details.
