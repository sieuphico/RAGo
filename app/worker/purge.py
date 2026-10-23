"""Xóa vật lý dữ liệu đã xử lý của tài liệu bị xóa trong ≤ 24 giờ (BR-029, AD-08)."""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.core.config import Settings, get_settings
from app.core.wiring import build_storage
from app.domain import DocumentStatus, Job
from app.models.document import Chunk, Document, Suggestion
from app.modules.audit import service as audit
from app.modules.documents import repository as documents
from app.modules.documents.events import publish_status
from app.modules.jobs import service as jobs
from app.ports.storage import StoragePort

logger = logging.getLogger("app.worker.purge")


@dataclass
class PurgeDeps:
    factory: Callable[[], Any]
    storage: StoragePort
    settings: Settings


def default_deps() -> PurgeDeps:
    settings = get_settings()
    return PurgeDeps(db.get_session_factory(), build_storage(settings), settings)


async def purge_document(job: Job, deps: PurgeDeps | None = None) -> None:
    deps = deps or default_deps()
    doc_id = UUID(job.payload["docId"])
    async with deps.factory() as session:
        doc = await documents.get(session, doc_id, include_deleted=True)
        if doc is None or doc.deleted_at is None:
            logger.warning("purge skipped: document %s is not deleted", doc_id)
            return
        if doc.status == DocumentStatus.DELETED:
            return  # đã xóa vật lý trước đó
        name, file_key = doc.name, doc.file_key
        await session.execute(delete(Chunk).where(Chunk.doc_id == doc_id))
        await session.execute(delete(Suggestion).where(Suggestion.doc_id == doc_id))
        # Giữ hàng `document` (tên, DELETED) để trích dẫn cũ hiện "Tài liệu đã bị xóa" (EC-14)
        await documents.set_status(session, doc_id, DocumentStatus.DELETED)
        await publish_status(session, doc_id, DocumentStatus.DELETED)
        await audit.record(session, "system", "PURGE", doc_id, name)
        await session.commit()
    await asyncio.to_thread(deps.storage.delete, file_key)


async def _has_open_purge(session: AsyncSession, doc_id: UUID) -> bool:
    row = await session.execute(
        text(
            "SELECT 1 FROM job WHERE type = 'purge' AND status IN ('QUEUED','RUNNING') "
            "AND payload->>'docId' = :d LIMIT 1"
        ),
        {"d": str(doc_id)},
    )
    return row.first() is not None


async def purge_sweep(now: datetime, deps: PurgeDeps | None = None) -> int:
    """Đưa vào hàng đợi các tài liệu đã xóa gần hết hạn mà chưa có tác vụ purge (kể cả bị lỡ)."""
    deps = deps or default_deps()
    cutoff = now - timedelta(hours=deps.settings.purge_hours - 1)
    queued = 0
    async with deps.factory() as session:
        stale = await session.execute(
            select(Document.doc_id).where(
                Document.deleted_at.is_not(None),
                Document.deleted_at <= cutoff,
                Document.status != DocumentStatus.DELETED,
            )
        )
        for doc_id in stale.scalars().all():
            if not await _has_open_purge(session, doc_id):
                await jobs.enqueue(session, "purge", {"docId": str(doc_id)})
                queued += 1
        await session.commit()
    return queued
