# ADR-0002: MySQL with Alembic migrations, in-memory store for tests

> **Status:** Accepted | **Date:** 2026-07-08 (retroactive) | **Deciders:** Project owner

## Context and Problem

The MVP needs durable persistence for users, tasks, fixed events, execution logs, and schedule history, while unit and API tests must stay fast and require no running database.

Constraints:

- Local Docker Compose runtime; no hosted database.
- Schema evolves per issue, so migrations must be repeatable.

## Options Considered

### Option 1: SQLite everywhere
- **Description:** Single-file database for both runtime and tests.
- **Pros:** Zero infrastructure; trivial test setup.
- **Cons:** Diverges from a realistic hosted target; weaker concurrency; MySQL-specific behavior untested.
- **Cost/Complexity:** Low

### Option 2: MySQL in Docker plus an in-memory repository for tests
- **Description:** Repository layer abstracts storage; Docker uses MySQL 8 with Alembic migrations run before `backend-api` starts; tests inject an in-memory store.
- **Pros:** Production-like engine locally; fast dependency-free tests; migration history is explicit.
- **Cons:** Two storage implementations to keep behaviorally consistent.
- **Cost/Complexity:** Medium

## Decision

**Chosen:** Option 2.

The repository layer is the seam: MySQL in Docker, in-memory in tests. Alembic owns schema changes; the older schema bootstrap remains only as a local compatibility fallback.

## Consequences

- **Positive:** Tests run without Docker; schema changes are versioned and reviewable.
- **Negative:** In-memory store can drift from MySQL behavior; E2E smoke against Docker is required for DB-touching changes.
- **Re-evaluate when:** Hosted deployment chooses a managed database, or drift between stores causes recurring bugs.
