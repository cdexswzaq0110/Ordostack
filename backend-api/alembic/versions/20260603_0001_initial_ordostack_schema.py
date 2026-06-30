"""initial ordostack schema

Revision ID: 20260603_0001
Revises:
Create Date: 2026-06-03
"""

from alembic import op

revision = "20260603_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
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
        """
    )
    op.execute(
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
        """
    )
    op.execute(
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
        """
    )
    op.execute(
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
        """
    )
    op.execute(
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
        """
    )


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
