import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import ScratchDb

TABLES = {"document", "chunk", "suggestion"}
INDEXES = {
    "ix_chunk_embedding_hnsw",
    "ix_chunk_tsv_gin",
    "ix_chunk_doc_page",
    "ix_document_status_uploaded",
}


def test_upgrade_downgrade(scratch_db: ScratchDb) -> None:
    scratch_db.upgrade("001")
    assert TABLES <= scratch_db.tables()
    scratch_db.downgrade("000")
    assert not TABLES & scratch_db.tables()


def test_indexes_exist(scratch_db: ScratchDb) -> None:
    scratch_db.upgrade("001")
    assert INDEXES <= scratch_db.indexes()


async def _doc(session: AsyncSession, status: str = "PROCESSING") -> uuid.UUID:
    doc_id = uuid.uuid4()
    await session.execute(
        text(
            "INSERT INTO document (doc_id, name, uploaded_by, size_bytes, status, file_key) "
            "VALUES (:id, 'a.pdf', 'u@x.vn', 10, :status, :key)"
        ),
        {"id": doc_id, "status": status, "key": f"k-{doc_id}"},
    )
    return doc_id


def _vec(dim: int = 384) -> str:
    return "[" + ",".join(["0.1"] * dim) + "]"


async def _chunk(session: AsyncSession, doc_id: uuid.UUID, page: int, body: str) -> None:
    await session.execute(
        text(
            "INSERT INTO chunk (doc_id, page, text, embedding) "
            "VALUES (:d, :p, :t, CAST(:e AS vector))"
        ),
        {"d": doc_id, "p": page, "t": body, "e": _vec()},
    )


async def _count(session: AsyncSession, table: str) -> int:
    return int((await session.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one())


async def test_cascade_delete(session: AsyncSession) -> None:
    doc_id = await _doc(session)
    await _chunk(session, doc_id, 1, "a")
    await _chunk(session, doc_id, 2, "b")
    await session.execute(
        text("INSERT INTO suggestion (doc_id, questions) VALUES (:d, CAST(:q AS jsonb))"),
        {"d": doc_id, "q": '["a","b","c"]'},
    )
    await session.execute(text("DELETE FROM document WHERE doc_id = :d"), {"d": doc_id})
    assert await _count(session, "chunk") == 0
    assert await _count(session, "suggestion") == 0


async def test_status_check(session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await _doc(session, "UPLOADING")


async def test_tsv_unaccent(session: AsyncSession) -> None:
    doc_id = await _doc(session)
    await _chunk(session, doc_id, 1, "Hợp đồng số 12/2026")
    await _chunk(session, doc_id, 2, "Báo cáo tài chính")
    rows = await session.execute(
        text(
            "SELECT page FROM chunk "
            "WHERE tsv @@ plainto_tsquery('simple', cwd_unaccent('hop dong'))"
        )
    )
    assert [r[0] for r in rows] == [1]
