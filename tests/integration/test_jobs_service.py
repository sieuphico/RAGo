import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.domain import Job
from app.modules.jobs import repository as repo
from app.modules.jobs import service as jobs

T = datetime(2026, 11, 2, 8, tzinfo=UTC)


async def test_exclusive_claim(test_database_url: str) -> None:
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as s:
            await jobs.enqueue(s, "ingest", {"docId": "d"}, run_after=T)
            await s.commit()

        async def worker(name: str) -> Job | None:
            async with factory() as s:
                got = await jobs.claim(s, name, T + timedelta(seconds=1))
                await asyncio.sleep(0.2)  # giữ giao dịch mở để bên kia thấy dòng đã khóa
                await s.commit()
                return got

        results = await asyncio.gather(worker("w1"), worker("w2"))
        assert sum(r is not None for r in results) == 1
    finally:
        async with factory() as s:
            await s.execute(text("DELETE FROM job"))
            await s.commit()
        await engine.dispose()


async def test_retry_then_failed(session: AsyncSession) -> None:
    job_id = await jobs.enqueue(session, "ingest", {"docId": "d"}, run_after=T)
    now = T
    for attempt, delay in ((1, 30), (2, 120)):
        claimed = await jobs.claim(session, "w", now)
        assert claimed is not None and claimed.attempts == attempt
        await jobs.fail(session, job_id, ValueError("noi dung bi mat"), now)
        row = await repo.get(session, job_id)
        assert row.status == "QUEUED" and row.run_after == now + timedelta(seconds=delay)
        now = row.run_after
    assert await jobs.claim(session, "w", now) is not None
    await jobs.fail(session, job_id, ValueError("noi dung bi mat"), now)
    row = await repo.get(session, job_id)
    assert row.status == "FAILED"
    assert row.last_error == "ValueError"


async def test_stale_release(session: AsyncSession) -> None:
    stale = await jobs.enqueue(session, "ingest", {}, run_after=T)
    fresh = await jobs.enqueue(session, "ingest", {}, run_after=T)
    for job_id, age in ((stale, 1801), (fresh, 100)):
        await session.execute(
            text("UPDATE job SET status='RUNNING', locked_at=:t WHERE job_id=:j"),
            {"t": T - timedelta(seconds=age), "j": job_id},
        )
    assert await jobs.release_stale(session, T) == 1
    session.expire_all()
    assert (await repo.get(session, stale)).status == "QUEUED"
    assert (await repo.get(session, fresh)).status == "RUNNING"


async def test_future_not_claimed(session: AsyncSession) -> None:
    await jobs.enqueue(session, "ingest", {}, run_after=T + timedelta(seconds=60))
    assert await jobs.claim(session, "w", T) is None


async def test_complete(session: AsyncSession) -> None:
    job_id = await jobs.enqueue(session, "ingest", {"docId": "d"}, run_after=T)
    claimed = await jobs.claim(session, "w", T)
    assert claimed is not None and claimed.payload == {"docId": "d"}
    await jobs.complete(session, job_id)
    assert (await repo.get(session, job_id)).status == "DONE"
