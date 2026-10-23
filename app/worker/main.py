"""Vòng lặp worker: nhận tác vụ, gọi handler theo loại, ghi kết quả."""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import db
from app.modules.audit import service as audit
from app.modules.jobs import service as jobs
from app.worker import registry
from app.worker.expire_history import expire_history
from app.worker.ingest import make_handler
from app.worker.purge import purge_document, purge_sweep
from app.worker.suggest import generate_suggestions

logger = logging.getLogger("app.worker")
SessionFactory = Callable[[], AsyncSession]


class UnknownJobType(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def run_worker(
    worker_id: str,
    stop: asyncio.Event,
    *,
    factory: async_sessionmaker[AsyncSession] | None = None,
    clock: Callable[[], datetime] = _utcnow,
    idle_s: float = 1.0,
) -> None:
    factory = factory or db.get_session_factory()
    while not stop.is_set():
        async with factory() as session:
            job = await jobs.claim(session, worker_id, clock())
            await session.commit()
        if job is None:
            try:
                await asyncio.wait_for(stop.wait(), timeout=idle_s)
            except TimeoutError:
                pass
            continue
        try:
            handler = registry.handler_for(job.type)
            if handler is None:
                raise UnknownJobType(job.type)
            await handler(job)
        except Exception as exc:  # noqa: BLE001 - mọi lỗi handler đều phải ghi nhận và thử lại
            logger.error("job %s (%s) failed: %s", job.job_id, job.type, type(exc).__name__)
            async with factory() as session:
                await jobs.fail(session, job.job_id, exc, clock())
                await session.commit()
        else:
            async with factory() as session:
                await jobs.complete(session, job.job_id)
                await session.commit()


def register_defaults() -> None:
    """Tác vụ định kỳ có sẵn (CONTRACTS mục 8). Task khác tự thêm dòng của mình ở registry."""

    async def release_stale() -> None:
        async with db.get_session_factory()() as session:
            await jobs.release_stale(session, _utcnow())
            await session.commit()

    async def history_expire() -> None:
        async with db.get_session_factory()() as session:
            await expire_history(session, _utcnow())
            await session.commit()

    async def audit_expire() -> None:
        async with db.get_session_factory()() as session:
            await audit.expire(session, _utcnow())
            await session.commit()

    async def sweep() -> None:
        await purge_sweep(_utcnow())

    registry.register("ingest", make_handler())
    registry.register("purge", purge_document)
    registry.register("suggest", generate_suggestions)
    registry.every("purge_sweep", 3600, sweep)
    registry.every("release_stale_jobs", 60, release_stale)
    registry.daily("audit_expire", "02:00", audit_expire)
    registry.daily("history_expire", "02:30", history_expire)
