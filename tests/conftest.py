"""Fixture CSDL cho test tích hợp (cần `make db-up`).

Biến `CWD_TEST_DATABASE_URL` đổi CSDL thử; mặc định trỏ vào compose.dev.yml.
"""

import os
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import httpx
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

# Migration đọc Settings (embedding_dim); giá trị thử, không phải bí mật
for _key, _value in {
    "CWD_DATABASE_URL": "postgresql+asyncpg://cwd:cwd@localhost:5433/cwd_test",
    "CWD_SESSION_SECRET": "s" * 32,
    "CWD_TELEMETRY_SECRET": "t" * 32,
    "CWD_STORAGE_ROOT": "./var/test-storage",
    "CWD_EMBEDDING_DIM": "384",
}.items():
    os.environ.setdefault(_key, _value)

ROOT = Path(__file__).resolve().parents[1]
TEST_URL = os.environ.get(
    "CWD_TEST_DATABASE_URL", "postgresql+asyncpg://cwd:cwd@localhost:5433/cwd_test"
)


def _alembic(url: URL) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url.render_as_string(hide_password=False))
    return cfg


def _admin_engine(url: URL) -> Engine:
    return create_engine(
        url.set(drivername="postgresql+psycopg", database="postgres"),
        isolation_level="AUTOCOMMIT",
    )


def _recreate(url: URL) -> None:
    admin = _admin_engine(url)
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def test_database_url() -> Iterator[str]:
    url = make_url(TEST_URL)
    _recreate(url)
    command.upgrade(_alembic(url), "head")
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


class ScratchDb:
    """CSDL riêng để test upgrade/downgrade từng revision."""

    def __init__(self, url: URL) -> None:
        self.url = url
        self.cfg = _alembic(url)
        self.engine = create_engine(url.set(drivername="postgresql+psycopg"))

    def upgrade(self, revision: str) -> None:
        command.upgrade(self.cfg, revision)

    def downgrade(self, revision: str) -> None:
        command.downgrade(self.cfg, revision)

    def tables(self) -> set[str]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            return {r[0] for r in rows}

    def indexes(self) -> set[str]:
        with self.engine.connect() as conn:
            rows = conn.execute(text("SELECT indexname FROM pg_indexes WHERE schemaname='public'"))
            return {r[0] for r in rows}


@pytest.fixture
def scratch_db() -> Iterator[ScratchDb]:
    base = make_url(TEST_URL)
    url = base.set(database=f"cwd_scratch_{uuid.uuid4().hex[:8]}")
    _recreate(url)
    db = ScratchDb(url)
    yield db
    db.engine.dispose()
    admin = _admin_engine(url)
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    """Client gọi thẳng ứng dụng; dùng chung `session` (rollback sau test)."""
    from app.core.db import get_session
    from app.main import create_app

    app = create_app()

    async def _session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = _session
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="https://test") as c:
        yield c
