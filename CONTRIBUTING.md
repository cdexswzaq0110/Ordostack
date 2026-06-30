# Contributing

Keep changes small, runnable, and easy to review.

## Local Setup

```powershell
docker compose up --build -d
```

Open:

```text
http://localhost:5173
```

Demo account:

```text
demo@ordostack.local
ordostack-demo
```

## Quality Gate

Before opening a pull request, run:

```powershell
python scripts\ponytail.py --include-compose-config
```

If Docker is not available, run:

```powershell
python scripts\ponytail.py
```

## No Secrets

Do not commit `.env`, `.env.production`, API keys, database passwords, cloud credentials, ClearML credentials, private keys, or personal tokens.

## Branching

Use a focused branch:

```text
codex/<short-scope>
```

Prefer existing patterns. For non-trivial logic, add one runnable check that would fail if the logic breaks.
