# Deployment

Issue 30 defines the deployment baseline. It does not deploy OrdoStack to AWS or any hosted provider.

Current runnable support remains local Docker Compose. The production material in this repository is a checklist and skeleton for a future single-node Linux deployment.

## Account Requirements

No external account is required for Issue 30.

You only need an AWS account if the project later deploys to EC2. The same deployment baseline can also be used for any VPS provider.

## Deployment Files

| File | Purpose |
| --- | --- |
| `.env.production.example` | Production environment template with blank secrets |
| `docker-compose.prod.yml` | Production reverse-proxy overlay skeleton |
| `infra/nginx/ordostack.conf` | Nginx HTTP reverse-proxy skeleton |
| `docs/environment.md` | Runtime configuration contract |

Do not commit `.env.production`.

## Single-Node Target Architecture

```text
Internet
  -> HTTPS / domain
  -> Nginx reverse proxy
  -> web-dashboard
  -> backend-api
  -> scheduler-service
  -> ml-service
  -> MySQL volume or managed MySQL
```

For a private beta, the minimal hosted target is one Linux VM with Docker and Docker Compose. Public launch needs a stronger security review, managed TLS renewal, database backup automation, monitoring, and an incident runbook.

## Production Environment Setup

1. Copy `.env.production.example` to `.env.production` on the server.
2. Fill every required value.
3. Use a non-empty `DB_PASSWORD`.
4. Use a long random `AUTH_TOKEN_SECRET`.
5. Set `VITE_API_BASE_URL` to the deployed HTTPS API URL.
6. Keep `.env.production` out of Git.

The local Docker defaults intentionally allow an empty MySQL password and a fallback auth token secret. Do not use those local-only behaviors in production.

## Reverse Proxy Baseline

`infra/nginx/ordostack.conf` proxies:

- `/api/` to `backend-api:8000`
- `/` to `web-dashboard:5173`

The checked-in Nginx file listens on HTTP port `80` only. A real hosted deployment must terminate HTTPS through one of these options:

- Nginx with Certbot-managed certificates.
- Cloud or VPS load balancer with managed TLS.
- A platform-managed reverse proxy.

## Baseline Validation

Windows PowerShell:

```powershell
docker compose config
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile production config
```

Linux / WSL:

```bash
docker compose config
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile production config
```

## Hosted Smoke Checklist

After a future hosted deployment:

1. Open the deployed dashboard URL.
2. Login with a seeded or manually created local user.
3. Call `GET /api/health`.
4. Call `GET /api/auth/me` with a bearer token.
5. Create a task.
6. Create a fixed event.
7. Generate a schedule.
8. Confirm schedule history reloads after refresh.
9. Confirm backend logs contain no secrets.
10. Confirm MySQL backup is configured before customer data is entered.

## Non-Goals

- No AWS resources are created by Issue 30.
- No domain or TLS certificate is provisioned by Issue 30.
- No paid API or external identity provider is used.
- No production secrets are stored in the repository.
