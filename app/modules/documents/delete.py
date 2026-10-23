"""Xóa logic tài liệu (API-05): ngừng dùng ngay, xóa vật lý do tác vụ `purge` (T-213)."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ErrorCode
from app.domain import CurrentUser, DocumentStatus, Role
from app.modules.audit import service as audit
from app.modules.documents import repository as documents
from app.modules.documents.events import publish_status
from app.modules.jobs import service as jobs
from app.modules.telemetry.service import emit

PURGE_DELAY = timedelta(minutes=5)


async def delete_document(
    session: AsyncSession, doc_id: UUID, actor: CurrentUser, now: datetime, sid: str = "unknown"
) -> bool:
    """Trả `already_deleted`. Ném DOC_NOT_FOUND (chưa từng có) hoặc AUTH_FORBIDDEN (không phải chủ)."""
    doc = await documents.get(session, doc_id, include_deleted=True)
    if doc is None:
        raise AppError(ErrorCode.DOC_NOT_FOUND)
    if actor.role == Role.TEAM_LEAD and doc.uploaded_by != actor.email:
        raise AppError(ErrorCode.AUTH_FORBIDDEN)
    if doc.deleted_at is not None:
        return True  # EC-18: đã xóa trước đó, không ghi gì thêm
    name = doc.name
    await documents.soft_delete(session, doc_id, now)
    await audit.record(session, actor.email, "DELETE", doc_id, name)
    await jobs.enqueue(session, "purge", {"docId": str(doc_id)}, run_after=now + PURGE_DELAY)
    await publish_status(session, doc_id, DocumentStatus.DELETED)
    await emit(
        session, actor, sid, "document_deleted", doc_id=str(doc_id), actor_role=actor.role.value
    )
    return False
