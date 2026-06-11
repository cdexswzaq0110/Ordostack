from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_ENDPOINTS = [
    "http://localhost:8000/api/health",
    "http://localhost:8000/api/ready",
    "http://localhost:8100/health",
    "http://localhost:8200/health",
]


@dataclass(frozen=True)
class ProbeResult:
    url: str
    ok: bool
    status_code: int | None
    duration_ms: int
    detail: str


def probe(url: str, timeout_seconds: float) -> ProbeResult:
    started_at = time.perf_counter()
    request = Request(url, headers={"User-Agent": "ordostack-monitoring-baseline"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            status_code = response.status
    except HTTPError as error:
        return ProbeResult(
            url=url,
            ok=False,
            status_code=error.code,
            duration_ms=elapsed_ms(started_at),
            detail=f"http error {error.code}",
        )
    except URLError as error:
        return ProbeResult(
            url=url,
            ok=False,
            status_code=None,
            duration_ms=elapsed_ms(started_at),
            detail=str(error.reason),
        )

    if status_code >= 400:
        return ProbeResult(url=url, ok=False, status_code=status_code, duration_ms=elapsed_ms(started_at), detail=body)

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {}

    health_status = str(payload.get("status", "")).lower()
    if health_status not in {"ok", "ready"}:
        return ProbeResult(
            url=url,
            ok=False,
            status_code=status_code,
            duration_ms=elapsed_ms(started_at),
            detail=f"unexpected status payload: {body[:160]}",
        )

    return ProbeResult(
        url=url,
        ok=True,
        status_code=status_code,
        duration_ms=elapsed_ms(started_at),
        detail=f"status={health_status}",
    )


def elapsed_ms(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe local OrdoStack health and readiness endpoints.")
    parser.add_argument("--endpoint", action="append", dest="endpoints", help="Endpoint URL to probe.")
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()

    endpoints = args.endpoints or DEFAULT_ENDPOINTS
    results = [probe(url, args.timeout) for url in endpoints]

    for result in results:
        status = "PASS" if result.ok else "FAIL"
        status_code = result.status_code if result.status_code is not None else "n/a"
        print(f"{status} {result.url} {status_code} {result.duration_ms}ms {result.detail}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
