# Scripts

Operational scripts for local development and QA.

## E2E Smoke

Windows PowerShell:

```powershell
python scripts\e2e_smoke.py
```

Linux / WSL:

```bash
python scripts/e2e_smoke.py
```

The smoke script expects `docker compose up --build -d` to be running locally.

## Browser Smoke

Windows PowerShell:

```powershell
python scripts\browser_smoke.py
```

Linux / WSL:

```bash
python scripts/browser_smoke.py
```

The browser smoke script expects Docker Compose to be running and a local Edge or Chrome executable to be installed. It writes screenshot artifacts under `artifacts/browser-smoke`, which is ignored by Git.
