# Support

## Support Scope

This repository currently supports:

- Local Docker Compose demo.
- Backend, scheduler, ML, and dashboard health checks.
- QA scripts under `scripts/`.
- Documentation under `docs/`.

Not supported as completed product work yet:

- Hosted production deployment.
- Mobile app.
- ClearML agent execution.
- External calendar sync.
- Paid API integrations.

## Before Asking

Run:

```powershell
docker compose ps
python scripts\ponytail.py
```

Include:

- OS and shell.
- Command that failed.
- Service logs for the failed service.
- Current Git commit.

## Known Limits

- Docker finalization and hosted deployment remain separate work.
- Production secrets must not be committed.
- Restore into an active database requires explicit manual approval.
