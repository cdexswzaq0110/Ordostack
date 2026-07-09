# ADR-0001: Split scheduling and ML prediction into dedicated services

> **Status:** Accepted | **Date:** 2026-07-08 (retroactive) | **Deciders:** Project owner

## Context and Problem

OrdoStack combines CRUD-style product data (tasks, events, logs) with two kinds of computation: schedule generation and duration prediction. Mixing algorithm code into backend routes makes the algorithms hard to test in isolation, and makes it hard to later swap the prediction model or scheduling strategy.

Constraints:

- The whole stack must run locally with Docker Compose.
- Algorithms must stay small, readable, and unit-testable.

## Options Considered

### Option 1: Single FastAPI monolith
- **Description:** All logic in `backend-api`.
- **Pros:** Fewer containers, simpler deployment, no inter-service HTTP.
- **Cons:** Scheduling and ML logic tangles with product routes; harder to test and replace independently.
- **Cost/Complexity:** Low

### Option 2: Dedicated `scheduler-service` and `ml-service` behind `backend-api`
- **Description:** `backend-api` remains the only public API and orchestrates calls to two internal FastAPI services.
- **Pros:** Clear responsibility boundaries; algorithms testable in isolation; either service can be reworked without touching product data paths.
- **Cons:** Three services to run and version; internal HTTP hops.
- **Cost/Complexity:** Medium

## Decision

**Chosen:** Option 2.

The dashboard talks only to `backend-api`; `scheduler-service` owns timeline generation and persists nothing; `ml-service` owns duration prediction. This keeps the product API thin and the computation replaceable.

## Consequences

- **Positive:** Scheduler algorithms have dedicated unit tests; ML backend can change (artifact vs heuristic) without API changes.
- **Negative:** Local stack needs four containers plus MySQL; internal service contracts must stay compatible.
- **Re-evaluate when:** Hosted deployment introduces real scaling or latency requirements.
