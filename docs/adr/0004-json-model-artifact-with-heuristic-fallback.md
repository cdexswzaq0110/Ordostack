# ADR-0004: JSON model artifact with deterministic heuristic fallback

> **Status:** Accepted | **Date:** 2026-07-08 (retroactive) | **Deciders:** Project owner

## Context and Problem

`ml-service` predicts task duration from estimate, category, priority, difficulty, focus requirement, and actuals. The MVP has little training data and no hosted model infrastructure, yet prediction must always return a usable answer (per ADR-0003, without paid APIs).

## Options Considered

### Option 1: Hosted model endpoint or heavyweight framework serving
- **Pros:** Room for sophisticated models.
- **Cons:** Violates local-first constraint; large images; overkill for current data volume.
- **Cost/Complexity:** High

### Option 2: Local JSON model artifact, with a deterministic heuristic when absent
- **Description:** Training exports a small JSON artifact; the service loads it if present, otherwise computes a deterministic heuristic from task attributes.
- **Pros:** No runtime dependency on training; predictions are reproducible; the service never fails for lack of a model.
- **Cons:** Model expressiveness limited by the artifact format; two code paths to test.
- **Cost/Complexity:** Low

## Decision

**Chosen:** Option 2.

The artifact-or-heuristic order is fixed: artifact first, heuristic fallback. Model metadata is exposed so callers can tell which path produced a prediction.

## Consequences

- **Positive:** Demo works with zero ML setup; the training loop can improve independently.
- **Negative:** No model registry or promotion workflow yet (tracked in WBS 5.1); heuristic quality bounds prediction usefulness early on.
- **Re-evaluate when:** Real usage data accumulates or a production model registry (ClearML) becomes operational.
