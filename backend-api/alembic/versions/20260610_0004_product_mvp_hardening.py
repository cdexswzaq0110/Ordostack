"""add product mvp hardening fields

Revision ID: 20260610_0004
Revises: 20260604_0003
Create Date: 2026-06-10
"""

from alembic import op
import sqlalchemy as sa

revision = "20260610_0004"
down_revision = "20260604_0003"
branch_labels = None
depends_on = None


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    existing_columns = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table_name)}
    if column.name not in existing_columns:
        op.add_column(table_name, column)


def upgrade() -> None:
    _add_column_if_missing("fixed_events", sa.Column("recurrence_id", sa.String(length=64), nullable=True))
    _add_column_if_missing("fixed_events", sa.Column("recurrence_rule", sa.String(length=255), nullable=True))
    _add_column_if_missing(
        "schedule_items",
        sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    _add_column_if_missing(
        "schedule_items",
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
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
