from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.audit import repository as audit


async def record(
    session: AsyncSession,
    actor: str,
    action: Literal["UPLOAD", "DELETE", "PURGE"],
    doc_id: UUID | None,
    doc_name: str | None,
) -> None:
    await audit.append(session, actor, action, doc_id, doc_name)


async def expire(session: AsyncSession, now: datetime) -> int:
    """Xóa bản ghi cũ hơn `audit_days` (tác vụ hằng ngày, T-205)."""
    return await audit.delete_before(session, now - timedelta(days=get_settings().audit_days))
