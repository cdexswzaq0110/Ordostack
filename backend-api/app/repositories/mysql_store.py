from datetime import UTC, date, datetime
import json
import os
from threading import Lock
from typing import Any

from app.repositories.memory_store import DEMO_USER_ID


class MySqlStore:
    _bootstrap_lock = Lock()

    def __init__(self) -> None:
        self._is_ready = False

    def list_tasks(
        self,
        user_id: int,
        status: str | None = None,
        category: str | None = None,
        target_date: date | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_ready()
        query = "SELECT * FROM tasks WHERE user_id=%s AND deleted_at IS NULL"
        params: list[Any] = [user_id]

        if status is not None:
            query += " AND status=%s"
            params.append(status)
        if category is not None:
            query += " AND category=%s"
            params.append(category)
        if target_date is not None:
            query += " AND DATE(deadline)=%s"
            params.append(target_date)

        query += " ORDER BY status ASC, priority DESC, id ASC"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return [self._normalize_task(row) for row in cursor.fetchall()]

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        self._ensure_ready()
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM tasks WHERE id=%s AND deleted_at IS NULL", (task_id,))
                row = cursor.fetchone()
                return self._normalize_task(row) if row else None

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_ready()
        now = datetime.now(UTC)
        row = {
            "predicted_minutes": None,
            "status": "pending",
            "created_at": now,
            "updated_at": None,
            "deleted_at": None,
            **payload,
        }
        fields = [
            "user_id",
            "title",
            "description",
            "category",
            "estimated_minutes",
            "predicted_minutes",
            "priority",
            "difficulty",
            "deadline",
            "requires_focus",
            "is_fixed",
            "is_splittable",
            "dependency_ids",
            "status",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        values = [self._serialize_value(field, row[field]) for field in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO tasks ({', '.join(fields)}) VALUES ({placeholders})",
                    values,
                )
                task_id = cursor.lastrowid
        task = self.get_task(task_id)
        if task is None:
            raise RuntimeError("Created task could not be loaded")
        return task

    def update_task(self, task_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
        self._ensure_ready()
        if not payload:
            return self.get_task(task_id)

        updated_payload = {**payload, "updated_at": datetime.now(UTC)}
        assignments = ", ".join([f"{field}=%s" for field in updated_payload])
        values = [
            self._serialize_value(field, value)
            for field, value in updated_payload.items()
        ]
        values.append(task_id)

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE tasks SET {assignments} WHERE id=%s AND deleted_at IS NULL",
                    values,
                )
                if cursor.rowcount == 0:
                    return None
        return self.get_task(task_id)

    def soft_delete_task(self, task_id: int) -> bool:
        self._ensure_ready()
        now = datetime.now(UTC)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET deleted_at=%s, updated_at=%s WHERE id=%s AND deleted_at IS NULL",
                    (now, now, task_id),
                )
                return cursor.rowcount > 0

    def list_fixed_events(self, user_id: int, target_date: date | None = None) -> list[dict[str, Any]]:
        self._ensure_ready()
        query = "SELECT * FROM fixed_events WHERE user_id=%s AND deleted_at IS NULL"
        params: list[Any] = [user_id]
        if target_date is not None:
            query += " AND DATE(start_time)=%s"
            params.append(target_date)
        query += " ORDER BY start_time ASC, id ASC"

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return list(cursor.fetchall())

    def create_fixed_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_ready()
        now = datetime.now(UTC)
        row = {
            "created_at": now,
            "updated_at": None,
            "deleted_at": None,
            **payload,
        }
        fields = [
            "user_id",
            "title",
            "start_time",
            "end_time",
            "event_type",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        values = [self._serialize_value(field, row[field]) for field in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO fixed_events ({', '.join(fields)}) VALUES ({placeholders})",
                    values,
                )
                fixed_event_id = cursor.lastrowid

                cursor.execute("SELECT * FROM fixed_events WHERE id=%s", (fixed_event_id,))
                return cursor.fetchone()

    def create_execution_log(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_ready()
        now = datetime.now(UTC)
        row = {"created_at": now, **payload}
        fields = ["user_id", "task_id", "event_type", "occurred_at", "created_at"]
        values = [self._serialize_value(field, row[field]) for field in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO execution_logs ({', '.join(fields)}) VALUES ({placeholders})",
                    values,
                )
                execution_log_id = cursor.lastrowid

                cursor.execute("SELECT * FROM execution_logs WHERE id=%s", (execution_log_id,))
                return cursor.fetchone()

    def list_execution_logs(
        self,
        user_id: int,
        target_date: date | None = None,
        task_id: int | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_ready()
        query = "SELECT * FROM execution_logs WHERE user_id=%s"
        params: list[Any] = [user_id]

        if task_id is not None:
            query += " AND task_id=%s"
            params.append(task_id)
        if target_date is not None:
            query += " AND DATE(occurred_at)=%s"
            params.append(target_date)
        query += " ORDER BY occurred_at ASC, id ASC"

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return list(cursor.fetchall())

    def save_generated_schedule(
        self,
        user_id: int,
        target_date: date,
        request_payload: dict[str, Any],
        schedule: dict[str, Any],
    ) -> dict[str, Any]:
        self._ensure_ready()
        now = datetime.now(UTC)

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO schedule_runs (
                      user_id,
                      schedule_date,
                      planning_mode,
                      request_start_hour,
                      request_end_hour,
                      request_buffer_minutes,
                      include_fixed_events,
                      algorithm_summary,
                      created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        target_date,
                        schedule.get("planning_mode", request_payload.get("planning_mode", "balanced")),
                        request_payload.get("start_hour"),
                        request_payload.get("end_hour"),
                        request_payload.get("buffer_minutes"),
                        int(bool(request_payload.get("include_fixed_events", True))),
                        json.dumps(schedule.get("algorithm_summary", {})),
                        now.replace(tzinfo=None),
                    ),
                )
                schedule_run_id = cursor.lastrowid

                for item in schedule.get("items", []):
                    cursor.execute(
                        """
                        INSERT INTO schedule_items (
                          schedule_run_id,
                          item_type,
                          task_id,
                          fixed_event_id,
                          title,
                          start_time,
                          end_time,
                          planned_minutes,
                          order_index,
                          category,
                          requires_focus,
                          score
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            schedule_run_id,
                            item.get("type"),
                            item.get("task_id"),
                            item.get("fixed_event_id"),
                            item.get("title"),
                            self._parse_datetime(item.get("start_time")),
                            self._parse_datetime(item.get("end_time")),
                            item.get("planned_minutes"),
                            item.get("order_index"),
                            item.get("category"),
                            int(bool(item.get("requires_focus", False))),
                            item.get("score"),
                        ),
                    )

        return dict(schedule)

    def get_latest_generated_schedule(self, user_id: int, target_date: date) -> dict[str, Any] | None:
        self._ensure_ready()
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM schedule_runs
                    WHERE user_id=%s AND schedule_date=%s
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    (user_id, target_date),
                )
                schedule_run = cursor.fetchone()
                if schedule_run is None:
                    return None

                cursor.execute(
                    """
                    SELECT *
                    FROM schedule_items
                    WHERE schedule_run_id=%s
                    ORDER BY order_index ASC, id ASC
                    """,
                    (schedule_run["id"],),
                )
                schedule_items = cursor.fetchall()

        return self._normalize_schedule(schedule_run, schedule_items)

    def _ensure_ready(self) -> None:
        if self._is_ready:
            return

        with self._bootstrap_lock:
            if self._is_ready:
                return

            self._create_schema()
            self._is_ready = True
            self._seed_demo_data_if_empty()

    def _create_schema(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                for statement in SCHEMA_STATEMENTS:
                    cursor.execute(statement)

    def _seed_demo_data_if_empty(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS row_count FROM tasks")
                if cursor.fetchone()["row_count"] > 0:
                    return

        created_tasks = [self.create_task(task) for task in demo_task_seed()]
        completed_task = created_tasks[2]

        self.update_task(completed_task["id"], {"status": "completed"})
        self.create_execution_log(
            {
                "user_id": DEMO_USER_ID,
                "task_id": completed_task["id"],
                "event_type": "start",
                "occurred_at": datetime(2026, 6, 3, 14, 0),
            }
        )
        self.create_execution_log(
            {
                "user_id": DEMO_USER_ID,
                "task_id": completed_task["id"],
                "event_type": "complete",
                "occurred_at": datetime(2026, 6, 3, 14, 47),
            }
        )
        for fixed_event in demo_fixed_event_seed():
            self.create_fixed_event(fixed_event)

    def _connect(self):
        import pymysql
        import pymysql.cursors

        return pymysql.connect(
            host=os.getenv("DB_HOST", "mysql"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "ordostack"),
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def _normalize_task(self, row: dict[str, Any]) -> dict[str, Any]:
        task = dict(row)
        dependency_ids = task.get("dependency_ids")
        if isinstance(dependency_ids, str):
            task["dependency_ids"] = json.loads(dependency_ids)
        elif dependency_ids is None:
            task["dependency_ids"] = []
        return task

    def _normalize_schedule(self, schedule_run: dict[str, Any], schedule_items: list[dict[str, Any]]) -> dict[str, Any]:
        schedule_date = schedule_run["schedule_date"]
        if isinstance(schedule_date, date):
            schedule_date_value = schedule_date.isoformat()
        else:
            schedule_date_value = str(schedule_date)

        return {
            "schedule_date": schedule_date_value,
            "planning_mode": schedule_run["planning_mode"],
            "items": [self._normalize_schedule_item(item) for item in schedule_items],
            "algorithm_summary": self._deserialize_json(schedule_run.get("algorithm_summary"), {}),
        }

    def _normalize_schedule_item(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": row["item_type"],
            "title": row["title"],
            "start_time": self._format_datetime(row["start_time"]),
            "end_time": self._format_datetime(row["end_time"]),
            "planned_minutes": row["planned_minutes"],
            "order_index": row["order_index"],
            "task_id": row["task_id"],
            "fixed_event_id": row["fixed_event_id"],
            "category": row["category"],
            "requires_focus": bool(row["requires_focus"]),
            "score": row["score"],
        }

    def _deserialize_json(self, value: Any, fallback: Any) -> Any:
        if value is None:
            return fallback
        if isinstance(value, str):
            return json.loads(value)
        return value

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value is None or isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value).replace(tzinfo=None)
        return value

    def _format_datetime(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    def _serialize_value(self, field: str, value: Any) -> Any:
        if field == "dependency_ids":
            return json.dumps(value or [])
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        return value


def demo_task_seed() -> list[dict[str, Any]]:
    return [
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


def demo_fixed_event_seed() -> list[dict[str, Any]]:
    return [
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


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS tasks (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      title VARCHAR(255) NOT NULL,
      description TEXT NOT NULL,
      category VARCHAR(50) NOT NULL,
      estimated_minutes INT NOT NULL,
      predicted_minutes INT NULL,
      priority INT NOT NULL,
      difficulty INT NOT NULL,
      deadline DATETIME(6) NULL,
      requires_focus BOOLEAN NOT NULL,
      is_fixed BOOLEAN NOT NULL,
      is_splittable BOOLEAN NOT NULL,
      dependency_ids JSON NOT NULL,
      status VARCHAR(20) NOT NULL,
      created_at DATETIME(6) NOT NULL,
      updated_at DATETIME(6) NULL,
      deleted_at DATETIME(6) NULL,
      INDEX idx_tasks_user_status (user_id, status),
      INDEX idx_tasks_deadline (deadline)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fixed_events (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      title VARCHAR(255) NOT NULL,
      start_time DATETIME(6) NOT NULL,
      end_time DATETIME(6) NOT NULL,
      event_type VARCHAR(50) NULL,
      created_at DATETIME(6) NOT NULL,
      updated_at DATETIME(6) NULL,
      deleted_at DATETIME(6) NULL,
      INDEX idx_fixed_events_user_start (user_id, start_time)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS execution_logs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      task_id INT NOT NULL,
      event_type VARCHAR(20) NOT NULL,
      occurred_at DATETIME(6) NOT NULL,
      created_at DATETIME(6) NOT NULL,
      INDEX idx_execution_logs_user_time (user_id, occurred_at),
      INDEX idx_execution_logs_task (task_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS schedule_runs (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      schedule_date DATE NOT NULL,
      planning_mode VARCHAR(50) NOT NULL,
      request_start_hour INT NULL,
      request_end_hour INT NULL,
      request_buffer_minutes INT NULL,
      include_fixed_events BOOLEAN NOT NULL,
      algorithm_summary JSON NOT NULL,
      created_at DATETIME(6) NOT NULL,
      INDEX idx_schedule_runs_user_date (user_id, schedule_date, id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS schedule_items (
      id INT AUTO_INCREMENT PRIMARY KEY,
      schedule_run_id INT NOT NULL,
      item_type VARCHAR(20) NOT NULL,
      task_id INT NULL,
      fixed_event_id INT NULL,
      title VARCHAR(255) NOT NULL,
      start_time DATETIME(6) NOT NULL,
      end_time DATETIME(6) NOT NULL,
      planned_minutes INT NOT NULL,
      order_index INT NOT NULL,
      category VARCHAR(50) NULL,
      requires_focus BOOLEAN NOT NULL,
      score DOUBLE NULL,
      INDEX idx_schedule_items_run_order (schedule_run_id, order_index),
      CONSTRAINT fk_schedule_items_run
        FOREIGN KEY (schedule_run_id) REFERENCES schedule_runs(id)
        ON DELETE CASCADE
    )
    """,
]
