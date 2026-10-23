import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_fake import AiFake
from app.domain import ChunkDraft
from app.worker.indexer import index_document
from tests.fixtures.documents import make_document

DIM = 384


def _chunks(n: int) -> list[ChunkDraft]:
    return [ChunkDraft(page=i % 3 + 1, text=f"doan van {i}") for i in range(n)]


async def _count(session: AsyncSession) -> int:
    return int((await session.execute(text("SELECT count(*) FROM chunk"))).scalar_one())


async def test_index_writes_chunks(session: AsyncSession) -> None:
    doc = await make_document(session)
    ai, calls = AiFake(dim=DIM), []

    async def embed(texts: list[str]) -> list[list[float]]:
        calls.append(len(texts))
        return await ai.embed(texts)

    written = await index_document(session, embed, doc.doc_id, _chunks(70), batch_size=32, dim=DIM)
    assert written == 70
    assert calls == [32, 32, 6]
    assert await _count(session) == 70


async def test_reindex_idempotent(session: AsyncSession) -> None:
    doc = await make_document(session)
    ai = AiFake(dim=DIM)
    for _ in range(2):
        await index_document(session, ai.embed, doc.doc_id, _chunks(5), batch_size=32, dim=DIM)
    assert await _count(session) == 5


async def test_dim_mismatch_raises(session: AsyncSession) -> None:
    doc = await make_document(session)

    async def bad(texts: list[str]) -> list[list[float]]:
        return [[0.1] * 10 for _ in texts]

    with pytest.raises(ValueError, match="embedding dim"):
        await index_document(session, bad, doc.doc_id, _chunks(3), batch_size=32, dim=DIM)
    assert await _count(session) == 0


async def test_partial_failure_leaves_nothing(session: AsyncSession) -> None:
    doc = await make_document(session)
    ai, state = AiFake(dim=DIM), {"n": 0}

    async def flaky(texts: list[str]) -> list[list[float]]:
        state["n"] += 1
        if state["n"] == 2:
            raise RuntimeError("provider down")
        return await ai.embed(texts)

    with pytest.raises(RuntimeError):
        await index_document(session, flaky, doc.doc_id, _chunks(70), batch_size=32, dim=DIM)
    assert await _count(session) == 0
