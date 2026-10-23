"""Engine và session bất đồng bộ.

`engine` và `SessionLocal` tạo lười (lần truy cập đầu) để nhập module này
không đòi đủ biến môi trường, ví dụ khi chạy test đơn vị.
"""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


@lru_cache
def _engine() -> AsyncEngine:
    return create_async_engine(get_settings().database_url)


@lru_cache
def _session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(_engine(), expire_on_commit=False)


def __getattr__(name: str) -> Any:
    if name == "engine":
        return _engine()
    if name == "SessionLocal":
        return _session_factory()
    raise AttributeError(name)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with _session_factory()() as session:
        yield session
