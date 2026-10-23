"""Hàng đợi tác vụ trong PostgreSQL (AD-14). Chỉ `flush`; nơi gọi quyết định `commit`."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import Job
from app.modules.jobs import repository as repo

RETRY_DELAYS_S = (30, 120)


async def enqueue(
    session: AsyncSession, type: str, payload: dict[str, Any], run_after: datetime | None = None
) -> UUID:
    return (await repo.add(session, type, payload, run_after)).job_id


async def claim(session: AsyncSession, worker_id: str, now: datetime) -> Job | None:
    row = await repo.claim_next(session, worker_id, now)
    if row is None:
        return None
    return Job(job_id=row.job_id, type=row.type, payload=row.payload, attempts=row.attempts)


async def complete(session: AsyncSession, job_id: UUID) -> None:
    row = await repo.get(session, job_id)
    row.status = "DONE"
    await session.flush()


async def fail(session: AsyncSession, job_id: UUID, error: BaseException, now: datetime) -> None:
    """Thử lại sau 30 giây, rồi 120 giây; hết `job_max_attempts` thì FAILED."""
    row = await repo.get(session, job_id)
    row.last_error = type(error).__name__[:200]  # chỉ tên lớp lỗi, không có nội dung
    row.locked_at = None
    row.locked_by = None
    if row.attempts < get_settings().job_max_attempts:
        delay = RETRY_DELAYS_S[min(row.attempts, len(RETRY_DELAYS_S)) - 1]
        row.status = "QUEUED"
        row.run_after = now + timedelta(seconds=delay)
    else:
        row.status = "FAILED"
    await session.flush()


async def release_stale(session: AsyncSession, now: datetime) -> int:
    cutoff = now - timedelta(seconds=get_settings().job_stale_after_s)
    return await repo.release_stale(session, cutoff)
