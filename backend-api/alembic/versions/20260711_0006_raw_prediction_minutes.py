"""record the raw model prediction alongside the served value

Revision ID: 20260711_0006
Revises: 20260710_0005
Create Date: 2026-07-11
"""

from alembic import op
import sqlalchemy as sa

revision = "20260711_0006"
down_revision = "20260710_0005"
branch_labels = None
depends_on = None


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    existing_columns = {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table_name)}
    if column.name not in existing_columns:
        op.add_column(table_name, column)


def upgrade() -> None:
    # Per-user calibration derives its factor from the raw model output so the
    # correction cannot feed back on already-calibrated served values.
    _add_column_if_missing("prediction_logs", sa.Column("raw_predicted_minutes", sa.Integer(), nullable=True))


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
