# ClearML

OrdoStack ships an optional ClearML integration for the duration-model
training loop. It is disabled by default: the product, the quality gates, and
the retraining loop all run with no ClearML package, credentials, or server.

## What Is Integrated

| Step | ClearML object | Where |
| --- | --- | --- |
| Training run | Task `duration-training <timestamp>` with parameters (model name/version, seed, row counts), scalar metrics (baseline MAE, model MAE, improvement ratio), and artifacts (model JSON, metrics JSON, dataset CSVs) | `ml-service/training/train_duration_model.py` |
| Gate-passing promotion | Task `duration-promotion <timestamp>` tagged `promoted` with the versioned artifact registered as an output model (or task artifact when the SDK runs offline) | `ml-service/training/promote_duration_model.py` |

The local JSON registry stays the source of truth for serving. ClearML only
observes the loop; a ClearML outage or misconfiguration can never break
training, promotion, or prediction — every integration point degrades to a
logged no-op (covered by `ml-service/tests/test_clearml_integration.py`).

## Enabling It

Install the training-time dependency (not part of any service image):

```powershell
python -m pip install -r ml-service\training\requirements-training.txt
```

### Offline mode (no account, no server)

Records each run as a local session zip under `~/.clearml/cache/offline/`.
This is how the integration is verified in this repository:

```powershell
$env:ORDOSTACK_CLEARML_ENABLED = "1"
$env:CLEARML_OFFLINE_MODE = "1"
python ml-service\training\train_duration_model.py
python ml-service\training\promote_duration_model.py
```

Offline sessions can be imported later with
`Task.import_offline_session("<session zip>")` once a server exists.

### Against a server

Point the SDK at a server, then enable the flag:

```powershell
clearml-init   # writes ~/clearml.conf; or set the CLEARML_API_* variables
$env:ORDOSTACK_CLEARML_ENABLED = "1"
python ml-service\training\train_duration_model.py
```

Credentials belong in `clearml.conf` or environment variables, never in Git.
The blank `CLEARML_API_*` keys in `.env.example` only document the names.

## Self-Hosted Server and Agent

A free self-hosted server keeps everything local-first:

```bash
# Linux / WSL with Docker
curl -o docker-compose.clearml.yml https://raw.githubusercontent.com/clearml/clearml-server/master/docker/docker-compose.yml
docker compose -f docker-compose.clearml.yml up -d
# Web UI on http://localhost:8080, API on :8008, file server on :8081
```

To execute training runs through a worker instead of your shell:

```bash
python -m pip install clearml-agent
clearml-agent daemon --queue default
```

Then clone a recorded `duration-training` task in the web UI and enqueue it to
`default`. The agent reproduces the environment and runs the same script.

Server and agent operation is a deployment decision (resource ownership,
retention, access policy) and is intentionally not wired into the product
Compose stack. See `docs/mlops-clearml-plan.md` for the promotion workflow and
`docs/internal/mlops-production-roadmap.md` for when to adopt it.
