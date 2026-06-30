from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL

from app.config import load_runtime_config

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def build_database_url() -> str:
    runtime_config = load_runtime_config()
    database_url = URL.create(
        "mysql+pymysql",
        username=runtime_config.db_user,
        password=runtime_config.db_password,
        host=runtime_config.db_host,
        port=runtime_config.db_port,
        database=runtime_config.db_name,
    )
    return database_url.render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    context.configure(
        url=build_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = build_database_url()
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
