"""Nhật ký kiểm toán chỉ ghi thêm. Không có hàm sửa hay xóa lẻ."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AuditLog


async def append(
    session: AsyncSession,
    actor: str,
    action: Literal["UPLOAD", "DELETE", "PURGE"],
    doc_id: UUID | None,
    doc_name: str | None,
) -> None:
    session.add(AuditLog(actor=actor, action=action, doc_id=doc_id, doc_name=doc_name))
    await session.flush()


async def list_since(session: AsyncSession, since: datetime, limit: int) -> list[AuditLog]:
    query = (
        select(AuditLog)
        .where(AuditLog.at >= since)
        .order_by(AuditLog.at.desc(), AuditLog.id.desc())
        .limit(limit)
    )
    return list((await session.execute(query)).scalars())


async def delete_before(session: AsyncSession, cutoff: datetime) -> int:
    """Chỉ dùng cho tác vụ hết hạn nhật ký."""
    result = await session.execute(delete(AuditLog).where(AuditLog.at < cutoff))
    await session.flush()
    return int(result.rowcount)  # type: ignore[attr-defined]
