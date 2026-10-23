"""Truy cập dữ liệu tài liệu và chunk. Chỉ `flush`; nơi gọi quyết định `commit`."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import delete, func, literal, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ChunkDraft, DocumentStatus, FailureReason, assert_transition
from app.models.document import Chunk, Document

DocumentSort = Literal["uploadedAt_desc", "uploadedAt_asc", "name_asc", "name_desc"]

_ORDER = {
    "uploadedAt_desc": (Document.uploaded_at.desc(), Document.doc_id),
    "uploadedAt_asc": (Document.uploaded_at.asc(), Document.doc_id),
    "name_asc": (func.lower(Document.name).asc(), Document.doc_id),
    "name_desc": (func.lower(Document.name).desc(), Document.doc_id),
}


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def add(
    session: AsyncSession, *, name: str, uploaded_by: str, size_bytes: int, file_key: str
) -> Document:
    assert_transition(None, DocumentStatus.PROCESSING)
    doc = Document(
        name=name,
        uploaded_by=uploaded_by,
        size_bytes=size_bytes,
        file_key=file_key,
        status=DocumentStatus.PROCESSING,
    )
    session.add(doc)
    await session.flush()
    await session.refresh(doc)
    return doc


async def get(
    session: AsyncSession, doc_id: UUID, *, include_deleted: bool = False
) -> Document | None:
    query = select(Document).where(Document.doc_id == doc_id)
    if not include_deleted:
        query = query.where(Document.deleted_at.is_(None))
    # populate_existing: luôn đọc dữ liệu mới (tránh đối tượng cũ sau rollback)
    result = await session.execute(query.execution_options(populate_existing=True))
    return result.scalar_one_or_none()


async def list_documents(
    session: AsyncSession, search: str | None, sort: DocumentSort
) -> list[Document]:
    query = select(Document).where(Document.deleted_at.is_(None))
    if search:
        pattern = literal(f"%{_escape_like(search)}%")
        query = query.where(
            func.cwd_unaccent(func.lower(Document.name)).like(
                func.cwd_unaccent(func.lower(pattern)), escape="\\"
            )
        )
    result = await session.execute(query.order_by(*_ORDER[sort]))
    return list(result.scalars())


async def set_status(
    session: AsyncSession,
    doc_id: UUID,
    status: DocumentStatus,
    *,
    reason: FailureReason | None = None,
    page_count: int | None = None,
    used_ocr: bool | None = None,
) -> Document:
    result = await session.execute(
        select(Document).where(Document.doc_id == doc_id).with_for_update()
    )
    doc = result.scalar_one()
    assert_transition(doc.status, status)
    doc.status = status
    doc.failure_reason = reason
    if page_count is not None:
        doc.page_count = page_count
    if used_ocr is not None:
        doc.used_ocr = used_ocr
    if status in (DocumentStatus.READY, DocumentStatus.FAILED):
        doc.processed_at = func.now()
    await session.flush()
    await session.refresh(doc)
    return doc


async def soft_delete(session: AsyncSession, doc_id: UUID, at: datetime) -> bool:
    """False nếu đã xóa trước đó (EC-18)."""
    result = await session.execute(
        update(Document)
        .where(Document.doc_id == doc_id, Document.deleted_at.is_(None))
        .values(deleted_at=at)
    )
    await session.flush()
    return bool(result.rowcount)  # type: ignore[attr-defined]


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in vector) + "]"


async def add_chunks(
    session: AsyncSession,
    doc_id: UUID,
    chunks: list[ChunkDraft],
    embeddings: list[list[float]],
) -> int:
    if len(chunks) != len(embeddings):
        raise ValueError("chunks và embeddings phải cùng độ dài")
    if not chunks:
        return 0
    await session.execute(
        text(
            "INSERT INTO chunk (doc_id, page, text, embedding, lang) "
            "VALUES (:doc_id, :page, :text, CAST(:embedding AS vector), :lang)"
        ),
        [
            {
                "doc_id": doc_id,
                "page": c.page,
                "text": c.text,
                "embedding": _vector_literal(e),
                "lang": c.lang,
            }
            for c, e in zip(chunks, embeddings, strict=True)
        ],
    )
    await session.flush()
    return len(chunks)


async def delete_chunks(session: AsyncSession, doc_id: UUID) -> int:
    result = await session.execute(delete(Chunk).where(Chunk.doc_id == doc_id))
    await session.flush()
    return int(result.rowcount)  # type: ignore[attr-defined]


async def ready_doc_ids(session: AsyncSession, scope: set[UUID] | None = None) -> set[UUID]:
    query = select(Document.doc_id).where(
        Document.status == DocumentStatus.READY, Document.deleted_at.is_(None)
    )
    if scope is not None:
        query = query.where(Document.doc_id.in_(scope))
    return set((await session.execute(query)).scalars())
