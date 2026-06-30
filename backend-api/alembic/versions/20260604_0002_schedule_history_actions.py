"""add schedule history actions

Revision ID: 20260604_0002
Revises: 20260603_0001
Create Date: 2026-06-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260604_0002"
down_revision = "20260603_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("schedule_runs", sa.Column("title", sa.String(length=120), nullable=False, server_default="Generated plan"))
    op.add_column("schedule_runs", sa.Column("updated_at", sa.DateTime(timezone=False), nullable=True))
    op.add_column("schedule_runs", sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True))
    op.create_index(
        "idx_schedule_runs_user_date_active",
        "schedule_runs",
        ["user_id", "schedule_date", "deleted_at", "id"],
    )


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
