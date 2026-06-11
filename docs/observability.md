# Observability Baseline

Issue 31 adds local observability primitives that can be verified without paid APIs, cloud accounts, or an external monitoring vendor.

## Scope

- Request ID propagation through `X-Request-ID`.
- JSON request logs for each FastAPI service.
- Liveness health endpoints remain separate from readiness endpoints.
- Operational runbook for local QA and future hosted smoke checks.

## Request IDs

Clients may send:

```text
X-Request-ID: qa-run-001
```

If the header is present and matches the accepted format, the service returns the same value in the response. If it is missing or invalid, the service creates a UUID.

Accepted request ID characters:

```text
A-Z a-z 0-9 . _ : -
```

Maximum length: `128` characters.

## Request Logs

Each service logs one compact JSON object per HTTP request:

```json
{"event":"http_request","service":"backend-api","request_id":"qa-run-001","method":"GET","path":"/api/health","status_code":200,"duration_ms":2}
```

The baseline intentionally excludes:

- Request body.
- Response body.
- Query string.
- Authorization header.
- Cookies.
- Database password or runtime secret values.

## Health And Readiness

Health endpoints answer whether the process is alive:

| Service | Health endpoint |
| --- | --- |
| backend-api | `GET /api/health` and `GET /health` |
| scheduler-service | `GET /health` |
| ml-service | `GET /health` |

Readiness endpoints answer whether the service is ready to serve product traffic:

| Service | Readiness endpoint | Baseline check |
| --- | --- | --- |
| backend-api | `GET /api/ready` and `GET /ready` | Runtime configuration parses successfully |
| scheduler-service | `GET /ready` | Schedule generator is available |
| ml-service | `GET /ready` | Duration model metadata is available |

## Local Verification

Windows PowerShell:

```powershell
python scripts\monitoring_baseline.py
Invoke-RestMethod -Uri "http://localhost:8000/api/ready" -Headers @{ "X-Request-ID" = "qa-backend-ready" }
Invoke-RestMethod -Uri "http://localhost:8100/ready" -Headers @{ "X-Request-ID" = "qa-scheduler-ready" }
Invoke-RestMethod -Uri "http://localhost:8200/ready" -Headers @{ "X-Request-ID" = "qa-ml-ready" }
docker compose logs backend-api
docker compose logs scheduler-service
docker compose logs ml-service
```

Linux / WSL:

```bash
python scripts/monitoring_baseline.py
curl -H "X-Request-ID: qa-backend-ready" http://localhost:8000/api/ready
curl -H "X-Request-ID: qa-scheduler-ready" http://localhost:8100/ready
curl -H "X-Request-ID: qa-ml-ready" http://localhost:8200/ready
docker compose logs backend-api
docker compose logs scheduler-service
docker compose logs ml-service
```

Expected:

- Each response returns `status: ready`.
- Each response includes `X-Request-ID`.
- Logs contain matching `request_id` values.

## Hosted Monitoring Baseline

Issue 48 defines the hosted monitoring baseline without creating accounts or using paid APIs.

Minimum private-beta monitoring target:

- Uptime probe: every 60 seconds against dashboard, backend ready, scheduler ready, and ML ready endpoints.
- Availability alert: trigger after 3 consecutive failed probes.
- Latency alert: trigger when p95 backend ready latency stays above 1000 ms for 5 minutes.
- Error-rate alert: trigger when 5xx responses exceed 2 percent for 10 minutes.
- Alert route: product owner and engineering owner must both be named before hosted beta.
- Log retention: keep application request logs for at least 14 days during private beta.
- Privacy rule: request logs must continue excluding request bodies, query strings, auth headers, cookies, and secrets.

The repository does not configure a hosted vendor yet. Acceptable future choices include a self-hosted monitor, cloud-native monitor, or external uptime service after the deployment target is chosen.

## Future Work

- Metrics endpoint or OpenTelemetry exporter.
- Trace propagation across backend-api to scheduler-service and ml-service calls.
- Hosted uptime monitor.
- Alert routing and incident escalation.
- Log retention and privacy policy.
