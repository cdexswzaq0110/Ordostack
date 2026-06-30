"""add authentication users

Revision ID: 20260604_0003
Revises: 20260604_0002
Create Date: 2026-06-04
"""

from alembic import op

revision = "20260604_0003"
down_revision = "20260604_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
          id INT AUTO_INCREMENT PRIMARY KEY,
          email VARCHAR(255) NOT NULL,
          display_name VARCHAR(120) NOT NULL,
          password_hash VARCHAR(255) NOT NULL,
          created_at DATETIME(6) NOT NULL,
          updated_at DATETIME(6) NULL,
          UNIQUE KEY uq_users_email (email)
        )
        """
    )


def downgrade() -> None:
    # Destructive schema downgrade is intentionally not supported in the MVP.
    pass
