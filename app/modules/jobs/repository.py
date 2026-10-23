from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobRow


async def add(
    session: AsyncSession, type_: str, payload: dict[str, Any], run_after: datetime | None
) -> JobRow:
    row = JobRow(type=type_, payload=payload, status="QUEUED", attempts=0)
    if run_after is not None:
        row.run_after = run_after
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return row


async def claim_next(session: AsyncSession, worker_id: str, now: datetime) -> JobRow | None:
    query = (
        select(JobRow)
        .where(JobRow.status == "QUEUED", JobRow.run_after <= now)
        .order_by(JobRow.run_after)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    row = (await session.execute(query)).scalar_one_or_none()
    if row is None:
        return None
    row.status = "RUNNING"
    row.locked_at = now
    row.locked_by = worker_id
    row.attempts += 1
    await session.flush()
    return row


async def get(session: AsyncSession, job_id: UUID) -> JobRow:
    return (await session.execute(select(JobRow).where(JobRow.job_id == job_id))).scalar_one()


async def release_stale(session: AsyncSession, cutoff: datetime) -> int:
    result = await session.execute(
        update(JobRow)
        .where(JobRow.status == "RUNNING", JobRow.locked_at < cutoff)
        .values(status="QUEUED", locked_at=None, locked_by=None)
    )
    await session.flush()
    return int(result.rowcount)  # type: ignore[attr-defined]
