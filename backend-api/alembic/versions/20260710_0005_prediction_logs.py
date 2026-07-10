"""add prediction serving logs

Revision ID: 20260710_0005
Revises: 20260610_0004
Create Date: 2026-07-10
"""

from alembic import op

revision = "20260710_0005"
down_revision = "20260610_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_logs (
          id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          task_id INT NOT NULL,
          target_date DATE NOT NULL,
          model_name VARCHAR(120) NOT NULL,
          model_version VARCHAR(40) NOT NULL,
          predicted_minutes INT NOT NULL,
          estimated_minutes INT NOT NULL,
          actual_minutes INT NULL,
          actual_recorded_at DATETIME(6) NULL,
          created_at DATETIME(6) NOT NULL,
          INDEX idx_prediction_logs_user_date (user_id, target_date),
          INDEX idx_prediction_logs_unpaired (user_id, task_id, actual_minutes)
        )
        """
    )


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
