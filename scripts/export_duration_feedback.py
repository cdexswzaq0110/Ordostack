"""Export execution-log duration feedback from backend-api into a training CSV.

Pulls the last N days of completed-task feedback through the authenticated
`GET /api/ml/duration-feedback` endpoint and rewrites one merged CSV that
`ml-service/training/train_duration_model.py --feedback` consumes. Rewriting
the whole window each run keeps the export idempotent.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_BASE_URL = "http://localhost:8000/api"
DEFAULT_EMAIL = "demo@ordostack.local"
DEFAULT_PASSWORD = "ordostack-demo"
DEFAULT_DAYS = 14
DEFAULT_OUTPUT = Path("ml-service") / "training" / "data" / "duration_feedback.csv"
CSV_HEADER = "category,estimated_minutes,priority,difficulty,requires_focus,actual_minutes"
REQUEST_TIMEOUT_SECONDS = 10


def request_json(url: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, method="POST" if payload is not None else "GET")
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")

    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def export_feedback(base_url: str, email: str, password: str, days: int, output_path: Path) -> int:
    login = request_json(f"{base_url}/auth/login", payload={"email": email, "password": password})
    token = login["access_token"]

    data_rows: list[str] = []
    today = date.today()
    for day_offset in range(days):
        target_date = (today - timedelta(days=day_offset)).isoformat()
        export = request_json(f"{base_url}/ml/duration-feedback?target_date={target_date}", token=token)
        if export["row_count"] == 0:
            continue

        lines = export["content"].strip().splitlines()
        if lines and lines[0] == CSV_HEADER:
            data_rows.extend(lines[1:])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(CSV_HEADER + "\n" + "\n".join(data_rows) + ("\n" if data_rows else ""), encoding="utf-8")
    return len(data_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export duration feedback from backend-api for retraining.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="How many past days to export, ending today.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        row_count = export_feedback(args.base_url, args.email, args.password, args.days, args.output)
    except (HTTPError, URLError) as error:
        print(f"Feedback export failed: {error}")
        print("Is the Docker stack running? Start it with: docker compose up --build -d")
        return 1

    print(f"Exported {row_count} feedback rows to {args.output}")
    print("Retrain with: python ml-service/training/train_duration_model.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
