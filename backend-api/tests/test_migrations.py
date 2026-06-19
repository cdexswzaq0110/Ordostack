from pathlib import Path


def test_mysql_migrations_do_not_use_add_column_if_not_exists() -> None:
    migration_dir = Path(__file__).resolve().parents[1] / "alembic" / "versions"

    offenders = [
        path.name
        for path in migration_dir.glob("*.py")
        if "ADD COLUMN IF NOT EXISTS" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []
