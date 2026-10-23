"""Fixture CSDL cho test tích hợp (cần `make db-up`).

Biến `CWD_TEST_DATABASE_URL` đổi CSDL thử; mặc định trỏ vào compose.dev.yml.
"""

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

ROOT = Path(__file__).resolve().parents[1]
TEST_URL = os.environ.get(
    "CWD_TEST_DATABASE_URL", "postgresql+asyncpg://cwd:cwd@localhost:5433/cwd_test"
)


@pytest.fixture(scope="session")
def test_database_url() -> Iterator[str]:
    url = make_url(TEST_URL)
    admin = create_engine(url.set(drivername="postgresql+psycopg", database="postgres"),
                          isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
    command.upgrade(cfg, "head")
    yield url.render_as_string(hide_password=False)


@pytest.fixture
async def session(test_database_url: str) -> AsyncIterator[AsyncSession]:
    """Mỗi test chạy trong một giao dịch ngoài và rollback khi xong."""
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    async with engine.connect() as conn:
        outer = await conn.begin()
        async with AsyncSession(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        ) as s:
            yield s
        await outer.rollback()
    await engine.dispose()
