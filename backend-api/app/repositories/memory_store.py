from copy import deepcopy
from datetime import UTC, date, datetime
from threading import RLock
from typing import Any

DEMO_USER_ID = 1
DEMO_DATE = date(2026, 6, 3)


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._next_task_id = 1
            self._next_fixed_event_id = 1
            self._next_execution_log_id = 1
            self._next_schedule_run_id = 1
            self._tasks: dict[int, dict[str, Any]] = {}
            self._fixed_events: dict[int, dict[str, Any]] = {}
            self._execution_logs: dict[int, dict[str, Any]] = {}
            self._schedule_runs: dict[int, dict[str, Any]] = {}
            self._seed_demo_data()

    def list_tasks(
        self,
        user_id: int,
        status: str | None = None,
        category: str | None = None,
        target_date: date | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            tasks = [deepcopy(task) for task in self._tasks.values()]

        filtered_tasks = [task for task in tasks if task["user_id"] == user_id and task["deleted_at"] is None]

        if status is not None:
            filtered_tasks = [task for task in filtered_tasks if task["status"] == status]

        if category is not None:
            filtered_tasks = [task for task in filtered_tasks if task["category"] == category]

        if target_date is not None:
            filtered_tasks = [
                task
                for task in filtered_tasks
                if task["deadline"] is not None and task["deadline"].date() == target_date
            ]

        return sorted(filtered_tasks, key=lambda task: (task["status"], -task["priority"], task["id"]))

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            return deepcopy(task) if task is not None and task["deleted_at"] is None else None

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._lock:
            task_id = self._next_task_id
            self._next_task_id += 1
            task = {
                "id": task_id,
                "predicted_minutes": None,
                "status": "pending",
                "created_at": now,
                "updated_at": None,
                "deleted_at": None,
                **payload,
            }
            self._tasks[task_id] = task
            return deepcopy(task)

    def update_task(self, task_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None or task["deleted_at"] is not None:
                return None

            task.update(payload)
            task["updated_at"] = datetime.now(UTC)
            return deepcopy(task)

    def soft_delete_task(self, task_id: int) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None or task["deleted_at"] is not None:
                return False

            task["deleted_at"] = datetime.now(UTC)
            task["updated_at"] = task["deleted_at"]
            return True

    def list_fixed_events(self, user_id: int, target_date: date | None = None) -> list[dict[str, Any]]:
        with self._lock:
            fixed_events = [deepcopy(event) for event in self._fixed_events.values()]

        filtered_events = [
            event for event in fixed_events if event["user_id"] == user_id and event["deleted_at"] is None
        ]

        if target_date is not None:
            filtered_events = [event for event in filtered_events if event["start_time"].date() == target_date]

        return sorted(filtered_events, key=lambda event: (event["start_time"], event["id"]))

    def get_fixed_event(self, fixed_event_id: int) -> dict[str, Any] | None:
        with self._lock:
            fixed_event = self._fixed_events.get(fixed_event_id)
            if fixed_event is None or fixed_event["deleted_at"] is not None:
                return None
            return deepcopy(fixed_event)

    def create_fixed_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._lock:
            fixed_event_id = self._next_fixed_event_id
            self._next_fixed_event_id += 1
            fixed_event = {
                "id": fixed_event_id,
                "created_at": now,
                "updated_at": None,
                "deleted_at": None,
                **payload,
            }
            self._fixed_events[fixed_event_id] = fixed_event
            return deepcopy(fixed_event)

    def update_fixed_event(self, fixed_event_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            fixed_event = self._fixed_events.get(fixed_event_id)
            if fixed_event is None or fixed_event["deleted_at"] is not None:
                return None

            fixed_event.update(payload)
            fixed_event["updated_at"] = datetime.now(UTC)
            return deepcopy(fixed_event)

    def soft_delete_fixed_event(self, fixed_event_id: int) -> bool:
        with self._lock:
            fixed_event = self._fixed_events.get(fixed_event_id)
            if fixed_event is None or fixed_event["deleted_at"] is not None:
                return False

            fixed_event["deleted_at"] = datetime.now(UTC)
            fixed_event["updated_at"] = fixed_event["deleted_at"]
            return True

    def create_execution_log(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._lock:
            execution_log_id = self._next_execution_log_id
            self._next_execution_log_id += 1
            execution_log = {
                "id": execution_log_id,
                "created_at": now,
                **payload,
            }
            self._execution_logs[execution_log_id] = execution_log
            return deepcopy(execution_log)

    def list_execution_logs(
        self,
        user_id: int,
        target_date: date | None = None,
        task_id: int | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            execution_logs = [deepcopy(log) for log in self._execution_logs.values()]

        filtered_logs = [log for log in execution_logs if log["user_id"] == user_id]

        if task_id is not None:
            filtered_logs = [log for log in filtered_logs if log["task_id"] == task_id]

        if target_date is not None:
            filtered_logs = [log for log in filtered_logs if log["occurred_at"].date() == target_date]

        return sorted(filtered_logs, key=lambda log: (log["occurred_at"].replace(tzinfo=None), log["id"]))

    def save_generated_schedule(
        self,
        user_id: int,
        target_date: date,
        request_payload: dict[str, Any],
        schedule: dict[str, Any],
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        with self._lock:
            schedule_run_id = self._next_schedule_run_id
            self._next_schedule_run_id += 1
            schedule_run = {
                "id": schedule_run_id,
                "user_id": user_id,
                "schedule_date": target_date,
                "request_payload": deepcopy(request_payload),
                "schedule": deepcopy(schedule),
                "created_at": now,
            }
            self._schedule_runs[schedule_run_id] = schedule_run
            return deepcopy(schedule_run["schedule"])

    def get_latest_generated_schedule(self, user_id: int, target_date: date) -> dict[str, Any] | None:
        with self._lock:
            schedules = [
                schedule_run
                for schedule_run in self._schedule_runs.values()
                if schedule_run["user_id"] == user_id and schedule_run["schedule_date"] == target_date
            ]

            if not schedules:
                return None

            latest_schedule = max(schedules, key=lambda schedule_run: schedule_run["id"])
            return deepcopy(latest_schedule["schedule"])

    def _seed_demo_data(self) -> None:
        task_seed = [
            {
                "user_id": DEMO_USER_ID,
                "title": "ML course chapter notes",
                "description": "Summarize model evaluation and feature engineering sections.",
                "category": "study",
                "estimated_minutes": 105,
                "priority": 5,
                "difficulty": 4,
                "deadline": datetime(2026, 6, 3, 18, 0),
                "requires_focus": True,
                "is_fixed": False,
                "is_splittable": False,
                "dependency_ids": [],
            },
            {
                "user_id": DEMO_USER_ID,
                "title": "LeetCode dynamic programming",
                "description": "Finish two medium DP problems and record mistakes.",
                "category": "coding",
                "estimated_minutes": 70,
                "priority": 4,
                "difficulty": 4,
                "deadline": datetime(2026, 6, 3, 19, 30),
                "requires_focus": True,
                "is_fixed": False,
                "is_splittable": False,
                "dependency_ids": [],
            },
            {
                "user_id": DEMO_USER_ID,
                "title": "Backend API review",
                "description": "Review task and fixed event API contracts.",
                "category": "backend",
                "estimated_minutes": 50,
                "priority": 3,
                "difficulty": 3,
                "deadline": datetime(2026, 6, 3, 17, 0),
                "requires_focus": False,
                "is_fixed": False,
                "is_splittable": True,
                "dependency_ids": [],
            },
            {
                "user_id": DEMO_USER_ID,
                "title": "Record task execution samples",
                "description": "Create sample actual time records for future analytics.",
                "category": "analytics",
                "estimated_minutes": 35,
                "priority": 2,
                "difficulty": 2,
                "deadline": datetime(2026, 6, 4, 12, 0),
                "requires_focus": False,
                "is_fixed": False,
                "is_splittable": False,
                "dependency_ids": [],
            },
        ]

        for task in task_seed:
            self.create_task(task)

        self.update_task(3, {"status": "completed"})
        self.create_execution_log(
            {
                "user_id": DEMO_USER_ID,
                "task_id": 3,
                "event_type": "start",
                "occurred_at": datetime(2026, 6, 3, 14, 0),
            }
        )
        self.create_execution_log(
            {
                "user_id": DEMO_USER_ID,
                "task_id": 3,
                "event_type": "complete",
                "occurred_at": datetime(2026, 6, 3, 14, 47),
            }
        )

        fixed_event_seed = [
            {
                "user_id": DEMO_USER_ID,
                "title": "Operating systems class",
                "start_time": datetime(2026, 6, 3, 20, 0),
                "end_time": datetime(2026, 6, 3, 23, 0),
                "event_type": "class",
            },
            {
                "user_id": DEMO_USER_ID,
                "title": "Dinner break",
                "start_time": datetime(2026, 6, 3, 18, 20),
                "end_time": datetime(2026, 6, 3, 19, 0),
                "event_type": "rest",
            },
        ]

        for fixed_event in fixed_event_seed:
            self.create_fixed_event(fixed_event)


store = InMemoryStore()
