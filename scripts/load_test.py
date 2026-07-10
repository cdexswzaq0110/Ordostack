"""Load-test baseline for the local Docker stack.

Measures two scenarios against a running stack (docker compose up --build -d):

  read-mix   the dashboard load path (tasks, analytics, predictions, latest
             schedule) — each request picks one endpoint round-robin
  generate   POST /schedules/generate, the full backend -> ml-service ->
             scheduler-service -> MySQL chain

Reports per-scenario request count, error count, throughput, and latency
percentiles (p50/p95/p99/max). Standard library only. The run writes demo
data; it resets the demo dataset afterwards unless --keep-data is passed.

    python scripts/load_test.py --requests 200 --concurrency 10
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BACKEND_API_URL = "http://localhost:8000/api"
DEMO_EMAIL = "demo@ordostack.local"
DEMO_PASSWORD = "ordostack-demo"
DEMO_DATE = "2026-06-03"
REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_OUTPUT = Path("artifacts") / "load-test" / "baseline.json"

READ_ENDPOINTS = [
    f"/tasks?target_date={DEMO_DATE}",
    f"/analytics/daily?target_date={DEMO_DATE}",
    f"/ml/duration-predictions?target_date={DEMO_DATE}",
    f"/schedules/history?target_date={DEMO_DATE}&limit=5",
]


def request(path: str, payload: dict[str, Any] | None = None, token: str | None = None) -> None:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    http_request = Request(f"{BACKEND_API_URL}{path}", data=body, method="POST" if payload is not None else "GET")
    http_request.add_header("Content-Type", "application/json")
    if token:
        http_request.add_header("Authorization", f"Bearer {token}")
    with urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        response.read()


def login() -> str:
    body = json.dumps({"email": DEMO_EMAIL, "password": DEMO_PASSWORD}).encode("utf-8")
    http_request = Request(f"{BACKEND_API_URL}/auth/login", data=body, method="POST")
    http_request.add_header("Content-Type", "application/json")
    with urlopen(http_request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))["access_token"]


def percentile(sorted_values: list[float], fraction: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, max(0, round(fraction * (len(sorted_values) - 1))))
    return sorted_values[index]


def run_scenario(
    name: str,
    make_call: Callable[[int], None],
    requests_total: int,
    concurrency: int,
) -> dict[str, Any]:
    latencies_ms: list[float] = []
    errors = 0

    def timed_call(index: int) -> tuple[float, bool]:
        started = time.perf_counter()
        try:
            make_call(index)
            return (time.perf_counter() - started) * 1000, True
        except (HTTPError, URLError, OSError):
            return (time.perf_counter() - started) * 1000, False

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for elapsed_ms, ok in pool.map(timed_call, range(requests_total)):
            if ok:
                latencies_ms.append(elapsed_ms)
            else:
                errors += 1
    wall_seconds = time.perf_counter() - wall_start

    latencies_ms.sort()
    return {
        "scenario": name,
        "requests": requests_total,
        "errors": errors,
        "concurrency": concurrency,
        "wall_seconds": round(wall_seconds, 2),
        "requests_per_second": round(requests_total / wall_seconds, 1) if wall_seconds else 0.0,
        "latency_ms": {
            "p50": round(percentile(latencies_ms, 0.50), 1),
            "p95": round(percentile(latencies_ms, 0.95), 1),
            "p99": round(percentile(latencies_ms, 0.99), 1),
            "max": round(percentile(latencies_ms, 1.0), 1),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure latency baselines against the running stack.")
    parser.add_argument("--requests", type=int, default=200, help="Requests per scenario.")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--generate-requests", type=int, default=50, help="Requests for the generate scenario.")
    parser.add_argument("--keep-data", action="store_true", help="Skip the demo reset after the run.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        token = login()
    except (HTTPError, URLError, OSError) as error:
        print(f"Cannot reach the stack: {error}")
        print("Start it with: docker compose up --build -d")
        return 1

    def read_mix(index: int) -> None:
        request(READ_ENDPOINTS[index % len(READ_ENDPOINTS)], token=token)

    def generate(index: int) -> None:
        request(
            "/schedules/generate",
            payload={"user_id": 1, "target_date": DEMO_DATE, "planning_mode": "balanced"},
            token=token,
        )

    results = {
        "measured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scenarios": [
            run_scenario("read-mix", read_mix, args.requests, args.concurrency),
            run_scenario("generate-full-chain", generate, args.generate_requests, args.concurrency),
        ],
    }

    if not args.keep_data:
        request("/demo/reset", payload={}, token=token)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    for scenario in results["scenarios"]:
        latency = scenario["latency_ms"]
        print(
            f"{scenario['scenario']:>20}: {scenario['requests']} req @ c={scenario['concurrency']} "
            f"| {scenario['requests_per_second']} req/s | errors {scenario['errors']} "
            f"| p50 {latency['p50']}ms p95 {latency['p95']}ms p99 {latency['p99']}ms max {latency['max']}ms"
        )
    print(f"written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
