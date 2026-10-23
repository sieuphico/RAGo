from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ChunkDraft, DocumentStatus, InvalidTransition
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document

NOW = datetime(2026, 11, 2, tzinfo=UTC)


async def test_list_excludes_deleted(session: AsyncSession) -> None:
    docs = [await make_document(session, name=f"{i}.pdf") for i in range(3)]
    await repo.soft_delete(session, docs[0].doc_id, NOW)
    assert len(await repo.list_documents(session, None, "uploadedAt_desc")) == 2


async def test_search_unaccent(session: AsyncSession) -> None:
    await make_document(session, name="Hợp đồng ABC.pdf")
    await make_document(session, name="Báo cáo.pdf")
    found = await repo.list_documents(session, "hop dong", "uploadedAt_desc")
    assert [d.name for d in found] == ["Hợp đồng ABC.pdf"]


async def test_search_escapes_wildcards(session: AsyncSession) -> None:
    await make_document(session, name="a.pdf")
    await make_document(session, name="b.pdf")
    assert await repo.list_documents(session, "%", "uploadedAt_desc") == []
    assert await repo.list_documents(session, "_", "uploadedAt_desc") == []


async def test_sort_name_asc(session: AsyncSession) -> None:
    await make_document(session, name="b.pdf")
    await make_document(session, name="a.pdf")
    docs = await repo.list_documents(session, None, "name_asc")
    assert [d.name for d in docs] == ["a.pdf", "b.pdf"]


async def test_invalid_status_transition(session: AsyncSession) -> None:
    doc = await make_document(session, status=DocumentStatus.READY, page_count=3)
    with pytest.raises(InvalidTransition):
        await repo.set_status(session, doc.doc_id, DocumentStatus.PROCESSING)
    again = await repo.get(session, doc.doc_id)
    assert again is not None and again.status == DocumentStatus.READY
    assert again.processed_at is not None and again.page_count == 3


async def test_soft_delete_twice(session: AsyncSession) -> None:
    doc = await make_document(session)
    assert await repo.soft_delete(session, doc.doc_id, NOW) is True
    assert await repo.soft_delete(session, doc.doc_id, NOW) is False
    assert await repo.get(session, doc.doc_id) is None
    assert await repo.get(session, doc.doc_id, include_deleted=True) is not None


async def test_add_chunks(session: AsyncSession) -> None:
    doc = await make_document(session)
    drafts = [ChunkDraft(page=1, text="a"), ChunkDraft(page=2, text="b", lang="vi")]
    vectors = [[0.1] * 384, [0.2] * 384]
    assert await repo.add_chunks(session, doc.doc_id, drafts, vectors) == 2
    rows = await session.execute(
        text("SELECT page FROM chunk WHERE doc_id = :d ORDER BY page"), {"d": doc.doc_id}
    )
    assert [r[0] for r in rows] == [1, 2]
    assert await repo.delete_chunks(session, doc.doc_id) == 2


async def test_ready_doc_ids(session: AsyncSession) -> None:
    ready = await make_document(session, status=DocumentStatus.READY)
    await make_document(session)  # PROCESSING
    deleted = await make_document(session, status=DocumentStatus.READY)
    await repo.soft_delete(session, deleted.doc_id, NOW)
    assert await repo.ready_doc_ids(session) == {ready.doc_id}
    assert await repo.ready_doc_ids(session, {deleted.doc_id}) == set()
