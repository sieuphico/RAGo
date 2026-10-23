"""Handler tác vụ `ingest`: trích văn bản → (OCR) → chia chunk → nhúng → READY (SAD mục 5.2)."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.core.config import Settings, get_settings
from app.core.metrics import DOC_SECONDS, ERRORS
from app.core.wiring import build_gateway, build_ocr, build_renderer, build_storage
from app.domain import CurrentUser, DocumentStatus, FailureReason, Job, Role
from app.models.document import Document
from app.modules.documents import repository as documents
from app.modules.documents.events import publish_status
from app.modules.jobs import service as jobs
from app.modules.telemetry.mapping import failure_reason
from app.modules.telemetry.service import emit
from app.ports.ocr import OcrPort
from app.ports.storage import StoragePort
from app.worker.chunker import split
from app.worker.extract import ExtractError, extract_pages
from app.worker.indexer import EmbedFn, index_document
from app.worker.ocr_step import Render, ocr_pages

logger = logging.getLogger("app.worker.ingest")
WORKER_SID = "worker"
SessionMaker = Callable[[], Any]  # async_sessionmaker hoặc đối tượng tương đương trong test


@dataclass
class IngestDeps:
    factory: SessionMaker
    storage: StoragePort
    embed: EmbedFn
    ocr: OcrPort
    render: Render
    settings: Settings


def default_deps() -> IngestDeps:
    settings = get_settings()
    return IngestDeps(
        factory=db.get_session_factory(),
        storage=build_storage(settings),
        embed=build_gateway(settings).embed,
        ocr=build_ocr(settings),
        render=build_renderer(settings),
        settings=settings,
    )


async def _is_deleted(session: AsyncSession, doc_id: UUID) -> bool:
    deleted_at = (
        await session.execute(
            select(Document.deleted_at)
            .where(Document.doc_id == doc_id)
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    return deleted_at is not None


async def _transition(
    session: AsyncSession,
    doc_id: UUID,
    status: DocumentStatus,
    *,
    reason: FailureReason | None = None,
    page_count: int | None = None,
    used_ocr: bool | None = None,
) -> Document:
    doc = await documents.set_status(
        session, doc_id, status, reason=reason, page_count=page_count, used_ocr=used_ocr
    )
    await publish_status(session, doc_id, status, reason, page_count)
    return doc


async def handle_ingest(job: Job, deps: IngestDeps | None = None) -> None:
    deps = deps or default_deps()
    settings = deps.settings
    doc_id = UUID(job.payload["docId"])
    async with deps.factory() as session:
        doc = await documents.get(session, doc_id)
        if doc is None or doc.status not in (
            DocumentStatus.PROCESSING,
            DocumentStatus.OCR_PROCESSING,
        ):
            return  # đã xóa hoặc đã xử lý xong (chạy lại an toàn)
        # Sự kiện của worker dùng anon_user_id của người tải lên (session_id = "worker")
        uploader = CurrentUser(doc.uploaded_by, Role.TEAM_LEAD)
        uploaded_at = doc.uploaded_at
        ocr_attempted = False
        try:
            data = await asyncio.to_thread(deps.storage.read, doc.file_key)
            pages = await asyncio.to_thread(extract_pages, data, max_pages=settings.max_pages)
            used_ocr = False
            if any(not p.has_text_layer for p in pages):
                if doc.status == DocumentStatus.PROCESSING:
                    await _transition(session, doc_id, DocumentStatus.OCR_PROCESSING)
                    await session.commit()
                ocr_attempted = True
                pages, _ = await ocr_pages(
                    deps.ocr, data, pages, settings.ocr_min_confidence, render=deps.render
                )
                used_ocr = True
            chunks = split(pages, settings.chunk_target_chars, settings.chunk_overlap_chars)
            if await _is_deleted(session, doc_id):  # xóa giữa chừng (Q-C5)
                await session.rollback()
                return
            await index_document(
                session,
                deps.embed,
                doc_id,
                chunks,
                batch_size=settings.embed_batch_size,
                dim=settings.embedding_dim,
            )
            done = await _transition(
                session, doc_id, DocumentStatus.READY, page_count=len(pages), used_ocr=used_ocr
            )
            seconds = (done.processed_at - uploaded_at).total_seconds() if done.processed_at else 0.0
            DOC_SECONDS.labels(ocr=str(used_ocr).lower()).observe(max(seconds, 0.0))
            await emit(
                session, uploader, WORKER_SID, "document_processing_completed",
                doc_id=str(doc_id), page_count=len(pages), processing_seconds=max(seconds, 0.0),
            )  # fmt: skip
            if "suggestions" in settings.features:
                await jobs.enqueue(session, "suggest", {"docId": str(doc_id)})
            await session.commit()
        except ExtractError as exc:  # lỗi do tệp: thử lại vô ích
            await session.rollback()
            await _transition(session, doc_id, DocumentStatus.FAILED, reason=exc.reason)
            ERRORS.labels(code=exc.reason.value).inc()
            await emit(
                session, uploader, WORKER_SID, "document_processing_failed",
                doc_id=str(doc_id), reason=failure_reason(exc.reason), used_ocr=ocr_attempted,
            )  # fmt: skip
            await session.commit()
        except Exception:
            await session.rollback()
            if job.attempts >= settings.job_max_attempts:
                await _transition(
                    session, doc_id, DocumentStatus.FAILED, reason=FailureReason.PROCESSING_ERROR
                )
                ERRORS.labels(code=FailureReason.PROCESSING_ERROR.value).inc()
                await emit(
                    session, uploader, WORKER_SID, "document_processing_failed",
                    doc_id=str(doc_id), reason="other", used_ocr=ocr_attempted,
                )  # fmt: skip
                await session.commit()
            raise


def make_handler(deps: IngestDeps | None = None) -> Callable[[Job], Awaitable[None]]:
    async def handler(job: Job) -> None:
        await handle_ingest(job, deps)

    return handler


__all__ = ["IngestDeps", "handle_ingest", "make_handler"]
