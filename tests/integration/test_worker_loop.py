import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.domain import Job
from app.modules.jobs import service as jobs
from app.worker import registry
from app.worker.main import run_worker
from app.worker.scheduler import Scheduler

T = datetime(2026, 11, 2, 8, tzinfo=UTC)


@pytest.fixture
async def factory(test_database_url: str) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    """Dữ liệu được commit thật nên dọn lại sau mỗi test."""
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    registry.clear()
    yield maker
    registry.clear()
    async with maker() as s:
        await s.execute(text("DELETE FROM job"))
        await s.commit()
    await engine.dispose()


async def _enqueue(maker: async_sessionmaker[AsyncSession], type_: str) -> object:
    async with maker() as s:
        job_id = await jobs.enqueue(s, type_, {"docId": "d"}, run_after=T)
        await s.commit()
        return job_id


async def _row(maker: async_sessionmaker[AsyncSession], job_id: object) -> tuple[str, str | None]:
    async with maker() as s:
        row = (
            await s.execute(text("SELECT status, last_error FROM job WHERE job_id = :j"), {"j": job_id})
        ).one()
        return row[0], row[1]


async def _run_until_done(
    maker: async_sessionmaker[AsyncSession], job_id: object, *, timeout: float = 5
) -> None:
    stop = asyncio.Event()
    worker = asyncio.create_task(
        run_worker("w1", stop, factory=maker, clock=lambda: T + timedelta(seconds=1), idle_s=0.05)
    )
    for _ in range(int(timeout / 0.05)):
        status, error = await _row(maker, job_id)
        if status in ("DONE", "FAILED") or error:
            break
        await asyncio.sleep(0.05)
    stop.set()
    await worker


async def test_dispatch_by_type(factory: async_sessionmaker[AsyncSession]) -> None:
    seen: list[Job] = []

    async def handler(job: Job) -> None:
        seen.append(job)

    registry.register("t1", handler)
    job_id = await _enqueue(factory, "t1")
    await _run_until_done(factory, job_id)
    assert [j.type for j in seen] == ["t1"] and seen[0].payload == {"docId": "d"}
    assert (await _row(factory, job_id))[0] == "DONE"


async def test_unknown_type_fails(factory: async_sessionmaker[AsyncSession]) -> None:
    job_id = await _enqueue(factory, "khong_co")
    await _run_until_done(factory, job_id)
    status, error = await _row(factory, job_id)
    assert error == "UnknownJobType" and status == "QUEUED"  # chờ thử lại sau 30 giây


async def test_handler_error_is_recorded_not_fatal(
    factory: async_sessionmaker[AsyncSession],
) -> None:
    async def boom(job: Job) -> None:
        raise ValueError("noi dung nhay cam")

    registry.register("t1", boom)
    job_id = await _enqueue(factory, "t1")
    await _run_until_done(factory, job_id)
    assert (await _row(factory, job_id))[1] == "ValueError"


async def test_graceful_stop(factory: async_sessionmaker[AsyncSession]) -> None:
    async def slow(job: Job) -> None:
        await asyncio.sleep(2)

    registry.register("t1", slow)
    job_id = await _enqueue(factory, "t1")
    stop = asyncio.Event()
    started = asyncio.get_running_loop().time()
    worker = asyncio.create_task(
        run_worker("w1", stop, factory=factory, clock=lambda: T + timedelta(seconds=1), idle_s=0.05)
    )
    await asyncio.sleep(0.5)
    stop.set()
    await worker
    assert asyncio.get_running_loop().time() - started <= 3
    assert (await _row(factory, job_id))[0] == "DONE"


async def test_scheduler_every() -> None:
    registry.clear()
    calls: list[int] = []

    async def fn() -> None:
        calls.append(1)

    registry.every("t", 60, fn)
    scheduler = Scheduler()
    for second in range(181):
        await scheduler.tick(T + timedelta(seconds=second))
    await scheduler.drain()
    assert len(calls) == 3
    registry.clear()


async def test_scheduler_daily() -> None:
    registry.clear()
    calls: list[int] = []

    async def fn() -> None:
        calls.append(1)

    registry.daily("t", "02:00", fn)
    scheduler = Scheduler()
    now = datetime(2026, 11, 1, 1, 59, tzinfo=UTC)
    end = datetime(2026, 11, 2, 2, 1, tzinfo=UTC)
    while now <= end:
        await scheduler.tick(now)
        now += timedelta(minutes=1)
    await scheduler.drain()
    assert len(calls) == 2
    registry.clear()


async def test_scheduler_failure_does_not_block_others() -> None:
    registry.clear()
    calls: list[str] = []

    async def bad() -> None:
        raise RuntimeError("x")

    async def good() -> None:
        calls.append("good")

    registry.every("bad", 1, bad)
    registry.every("good", 1, good)
    scheduler = Scheduler()
    await scheduler.tick(T)
    await scheduler.tick(T + timedelta(seconds=1))
    await scheduler.drain()
    assert calls == ["good"]
    registry.clear()
