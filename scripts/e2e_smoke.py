from __future__ import annotations

from datetime import datetime
import json
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BACKEND_API_URL = "http://localhost:8000/api"
SCHEDULER_URL = "http://localhost:8100"
ML_URL = "http://localhost:8200"
DASHBOARD_URL = "http://localhost:5173"
DEMO_USER_ID = 1
TARGET_DATE = "2026-06-03"


def request_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=10) as response:
        content = response.read().decode("utf-8")
        if not content:
            return None
        return json.loads(content)


def request_text(url: str) -> str:
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> int:
    timestamp = int(time.time())
    task_title = f"E2E smoke task {timestamp}"
    edited_task_title = f"{task_title} edited"
    event_title = f"E2E smoke event {timestamp}"
    edited_event_title = f"{event_title} edited"

    try:
        backend_health = request_json(f"{BACKEND_API_URL}/health")
        scheduler_health = request_json(f"{SCHEDULER_URL}/health")
        ml_health = request_json(f"{ML_URL}/health")
        dashboard_html = request_text(DASHBOARD_URL)

        assert_equal(backend_health["status"], "ok", "backend-api health")
        assert_equal(scheduler_health["status"], "ok", "scheduler-service health")
        assert_equal(ml_health["status"], "ok", "ml-service health")
        assert_true("OrdoStack" in dashboard_html, "dashboard HTML contains OrdoStack")

        created_task = request_json(
            f"{BACKEND_API_URL}/tasks",
            method="POST",
            payload={
                "user_id": DEMO_USER_ID,
                "title": task_title,
                "description": "",
                "category": "e2e",
                "estimated_minutes": 30,
                "priority": 4,
                "difficulty": 2,
                "deadline": f"{TARGET_DATE}T17:00:00",
                "requires_focus": True,
                "is_fixed": False,
                "is_splittable": False,
                "dependency_ids": [],
            },
        )
        updated_task = request_json(
            f"{BACKEND_API_URL}/tasks/{created_task['id']}",
            method="PATCH",
            payload={"title": edited_task_title, "estimated_minutes": 35},
        )
        assert_equal(updated_task["title"], edited_task_title, "task edit title")
        assert_equal(updated_task["estimated_minutes"], 35, "task edit minutes")

        created_event = request_json(
            f"{BACKEND_API_URL}/fixed-events",
            method="POST",
            payload={
                "user_id": DEMO_USER_ID,
                "title": event_title,
                "event_type": "e2e",
                "start_time": f"{TARGET_DATE}T15:00:00",
                "end_time": f"{TARGET_DATE}T15:30:00",
            },
        )
        updated_event = request_json(
            f"{BACKEND_API_URL}/fixed-events/{created_event['id']}",
            method="PATCH",
            payload={
                "title": edited_event_title,
                "event_type": "e2e-edited",
                "start_time": f"{TARGET_DATE}T15:10:00",
                "end_time": f"{TARGET_DATE}T15:40:00",
            },
        )
        assert_equal(updated_event["title"], edited_event_title, "fixed event edit title")
        assert_equal(updated_event["event_type"], "e2e-edited", "fixed event edit type")

        schedule = request_json(
            f"{BACKEND_API_URL}/schedules/generate",
            method="POST",
            payload={
                "user_id": DEMO_USER_ID,
                "target_date": TARGET_DATE,
                "planning_mode": "balanced",
                "start_hour": 9,
                "end_hour": 23,
                "buffer_minutes": 10,
                "include_fixed_events": True,
            },
        )
        assert_true(len(schedule["items"]) >= 1, "generated schedule has items")

        second_schedule = request_json(
            f"{BACKEND_API_URL}/schedules/generate",
            method="POST",
            payload={
                "user_id": DEMO_USER_ID,
                "target_date": TARGET_DATE,
                "planning_mode": "balanced",
                "start_hour": 9,
                "end_hour": 23,
                "buffer_minutes": 10,
                "include_fixed_events": True,
            },
        )
        assert_true(len(second_schedule["items"]) >= 1, "second generated schedule has items")

        history = request_json(f"{BACKEND_API_URL}/schedules/history?user_id=1&target_date={TARGET_DATE}&limit=5")
        assert_true(len(history) >= 2, "schedule history has at least two runs")
        assert_equal(history[0]["schedule"]["schedule_date"], TARGET_DATE, "history target date")

        renamed_schedule = request_json(
            f"{BACKEND_API_URL}/schedules/history/{history[0]['id']}?user_id={DEMO_USER_ID}",
            method="PATCH",
            payload={"title": f"E2E smoke plan {timestamp}"},
        )
        assert_true(renamed_schedule["title"].startswith("E2E smoke plan"), "schedule rename")

        schedule_diff = request_json(
            f"{BACKEND_API_URL}/schedules/history/{history[0]['id']}/diff?user_id={DEMO_USER_ID}&against_run_id={history[1]['id']}",
        )
        assert_equal(schedule_diff["compare_run_id"], history[0]["id"], "schedule diff compare run")
        assert_equal(schedule_diff["base_run_id"], history[1]["id"], "schedule diff base run")

        exported_schedule = request_json(
            f"{BACKEND_API_URL}/schedules/history/{history[0]['id']}/export?user_id={DEMO_USER_ID}&format=markdown",
        )
        assert_true(exported_schedule["filename"].endswith(".md"), "schedule export filename")
        assert_true(exported_schedule["content"].startswith("# E2E smoke plan"), "schedule export content")

        print(
            json.dumps(
                {
                    "status": "ok",
                    "checked_at": datetime.now().isoformat(timespec="seconds"),
                    "task_id": created_task["id"],
                    "fixed_event_id": created_event["id"],
                    "schedule_run_id": history[0]["id"],
                    "history_runs": len(history),
                },
                indent=2,
            )
        )
        return 0
    except (AssertionError, HTTPError, URLError, TimeoutError) as error:
        print(f"E2E smoke failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
