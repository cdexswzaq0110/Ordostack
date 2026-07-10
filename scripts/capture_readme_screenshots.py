"""Capture real dashboard screenshots for the README.

Requires the Docker stack (docker compose up --build -d) and a local Edge or
Chrome installation. Uses Playwright against the system browser, so no browser
download is needed:

    python -m pip install playwright
    python scripts/capture_readme_screenshots.py

The script resets the demo dataset, generates a plan for today, signs in as the
demo user, and writes PNG files under docs/images/.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

BACKEND_API_URL = os.getenv("ORDOSTACK_API_URL", "http://localhost:8000/api")
DASHBOARD_URL = os.getenv("ORDOSTACK_DASHBOARD_URL", "http://localhost:5173")
OUTPUT_DIR = Path("docs") / "images"
VIEWPORT = {"width": 1440, "height": 1000}
AUTH_TOKEN_STORAGE_KEY = "ordostack.authToken"
DEMO_EMAIL = "demo@ordostack.local"
DEMO_PASSWORD = "ordostack-demo"
# The dashboard opens on the bundled demo dataset date (DEFAULT_SELECTED_DATE in App.tsx).
DEMO_DATASET_DATE = "2026-06-03"


def request_json(url: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, method="POST" if payload is not None else "GET")
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def browser_executable() -> str:
    candidates = [
        shutil.which("msedge"),
        str(Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe"),
        str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe"),
        shutil.which("chrome"),
        str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"),
        shutil.which("chromium"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("No local Edge or Chrome executable found")


def prepare_demo_data() -> str:
    login = request_json(f"{BACKEND_API_URL}/auth/login", payload={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    token = login["access_token"]
    request_json(f"{BACKEND_API_URL}/demo/reset", payload={}, token=token)
    request_json(
        f"{BACKEND_API_URL}/schedules/generate",
        payload={"target_date": DEMO_DATASET_DATE, "planning_mode": "balanced"},
        token=token,
    )
    # Complete one task after generation so the MLOps view has a paired
    # prediction and the live-accuracy panel renders with data.
    tasks = request_json(f"{BACKEND_API_URL}/tasks?target_date={DEMO_DATASET_DATE}", token=token)
    pending_task = next(task for task in tasks if task["status"] == "pending")
    request_json(
        f"{BACKEND_API_URL}/tasks/{pending_task['id']}/execution/start",
        payload={"occurred_at": f"{DEMO_DATASET_DATE}T15:00:00"},
        token=token,
    )
    request_json(
        f"{BACKEND_API_URL}/tasks/{pending_task['id']}/execution/complete",
        payload={"occurred_at": f"{DEMO_DATASET_DATE}T16:22:00"},
        token=token,
    )
    return token


def capture(token: str) -> list[Path]:
    from playwright.sync_api import sync_playwright

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with sync_playwright() as playwright_api:
        browser = playwright_api.chromium.launch(executable_path=browser_executable(), headless=True)
        context = browser.new_context(viewport=VIEWPORT, locale="en-US")
        context.add_init_script(
            f'window.localStorage.setItem("{AUTH_TOKEN_STORAGE_KEY}", {json.dumps(token)});'
        )
        page = context.new_page()
        page.goto(DASHBOARD_URL, wait_until="networkidle")
        page.wait_for_selector(".timeline, .empty-state", timeout=20_000)

        overview_path = OUTPUT_DIR / "dashboard-overview.png"
        page.screenshot(path=str(overview_path))
        written.append(overview_path)

        timeline = page.locator(".timeline-surface")
        timeline_path = OUTPUT_DIR / "schedule-timeline.png"
        timeline.screenshot(path=str(timeline_path))
        written.append(timeline_path)

        queue = page.locator(".queue-surface")
        queue_path = OUTPUT_DIR / "task-queue.png"
        queue.screenshot(path=str(queue_path))
        written.append(queue_path)

        page.get_by_role("button", name="Analytics").click()
        page.wait_for_selector(".data-table, .empty-state", timeout=10_000)
        analytics_path = OUTPUT_DIR / "analytics-view.png"
        page.screenshot(path=str(analytics_path))
        written.append(analytics_path)

        page.get_by_role("button", name="MLOps").click()
        page.wait_for_selector(".accuracy-panel, .empty-state", timeout=10_000)
        mlops_path = OUTPUT_DIR / "mlops-view.png"
        page.screenshot(path=str(mlops_path))
        written.append(mlops_path)

        browser.close()

    return written


def main() -> int:
    token = prepare_demo_data()
    written = capture(token)
    for path in written:
        print(f"wrote {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
