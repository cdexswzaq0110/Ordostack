"""add product mvp hardening fields

Revision ID: 20260610_0004
Revises: 20260604_0003
Create Date: 2026-06-10
"""

from alembic import op

revision = "20260610_0004"
down_revision = "20260604_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE fixed_events ADD COLUMN IF NOT EXISTS recurrence_id VARCHAR(64) NULL")
    op.execute("ALTER TABLE fixed_events ADD COLUMN IF NOT EXISTS recurrence_rule VARCHAR(255) NULL")
    op.execute("ALTER TABLE schedule_items ADD COLUMN IF NOT EXISTS locked BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("ALTER TABLE schedule_items ADD COLUMN IF NOT EXISTS manual_override BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS schedule_templates (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          name VARCHAR(120) NOT NULL,
          planning_mode VARCHAR(50) NOT NULL,
          start_hour INT NOT NULL,
          end_hour INT NOT NULL,
          buffer_minutes INT NOT NULL,
          include_fixed_events BOOLEAN NOT NULL,
          created_at DATETIME(6) NOT NULL,
          updated_at DATETIME(6) NULL,
          deleted_at DATETIME(6) NULL,
          INDEX idx_schedule_templates_user_active (user_id, deleted_at, name)
        )
        """
    )


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
