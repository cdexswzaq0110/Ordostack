# Architecture Decision Records

This directory records significant architecture decisions for OrdoStack. Each record uses a compact Context, Options, Decision, Consequences format.

ADRs 0001-0004 were written retroactively on 2026-07-08 to document decisions already implemented in the MVP.

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-service-split.md) | Split scheduling and ML prediction into dedicated services | Accepted |
| [0002](0002-mysql-with-in-memory-test-store.md) | MySQL with Alembic migrations, in-memory store for tests | Accepted |
| [0003](0003-local-first-no-paid-apis.md) | Local-first runtime with no paid APIs | Accepted |
| [0004](0004-json-model-artifact-with-heuristic-fallback.md) | JSON model artifact with deterministic heuristic fallback | Accepted |

## Adding a New ADR

1. Copy the structure of an existing ADR.
2. Number it sequentially (`0005-...`).
3. Set status: Proposed / Accepted / Superseded / Deprecated.
4. Add a row to the table above.

Write an ADR whenever a decision is expensive to reverse: service boundaries, storage engines, auth model, hosting, public API shape.
