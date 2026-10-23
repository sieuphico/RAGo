from alembic import context
from sqlalchemy import create_engine

config = context.config


def _url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        from app.core.config import get_settings

        url = get_settings().database_url
    # Alembic dùng driver đồng bộ (CONTRACTS 2.2)
    return url.replace("+asyncpg", "+psycopg")


def run_migrations_offline() -> None:
    context.configure(url=_url(), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_url())
    with engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
