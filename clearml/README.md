# ClearML

Issue 39 adds a disabled-by-default local tracking baseline. It does not require a ClearML account, server, agent, or paid API.

Current boundaries:

- Local training still writes JSON artifacts under `ml-service/training/artifacts`.
- Optional ClearML metadata is documented only; credentials must stay outside the repository.
- Real ClearML server/agent execution belongs to the later deployment/Docker phase.
