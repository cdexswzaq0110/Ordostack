# ADR-0003: Local-first runtime with no paid APIs

> **Status:** Accepted | **Date:** 2026-07-08 (retroactive) | **Deciders:** Project owner

## Context and Problem

The project stage is a customer demo MVP. It must be demonstrable on any machine with Docker, by anyone, without cloud accounts, API keys, or recurring cost — and without risking secret leakage through the repository.

## Options Considered

### Option 1: Cloud-backed features (hosted LLM/ML APIs, managed DB, SaaS monitoring)
- **Pros:** Stronger capabilities out of the box.
- **Cons:** Paid keys required to even run the demo; secrets management burden; violates the demo-anywhere goal.
- **Cost/Complexity:** High

### Option 2: Everything local — Docker Compose, local MySQL, local ML artifact
- **Pros:** Clone-and-run demo; zero recurring cost; no secrets needed in development.
- **Cons:** No hosted URL to share; some capabilities (model training at scale, external monitoring) are deferred.
- **Cost/Complexity:** Low

## Decision

**Chosen:** Option 2.

The repository provisions no AWS resources, DNS, TLS, paid API, or external monitoring. `.env.example` files carry empty values only; real secrets stay outside Git.

## Consequences

- **Positive:** Reproducible demo; the quality gates (`ponytail.py`, smoke scripts) run fully offline.
- **Negative:** Public launch requires a separate hosting workstream (tracked in the WBS as M3).
- **Re-evaluate when:** The project moves from Technical Preview to hosted beta.
