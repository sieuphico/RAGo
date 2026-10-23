import random
import time
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ChunkDraft, DocumentStatus
from app.modules.documents import repository as repo
from app.modules.retrieval.service import RRF_K, retrieve
from tests.fixtures.documents import make_document

DIM = 384


def unit(i: int) -> list[float]:
    """Vector trực giao e_i."""
    v = [0.0] * DIM
    v[i] = 1.0
    return v


def noise(seed: int) -> list[float]:
    rng = random.Random(seed)
    v = [rng.uniform(-1, 1) for _ in range(DIM)]
    norm = sum(x * x for x in v) ** 0.5
    return [x / norm for x in v]


def embed_returning(vector: list[float]):  # type: ignore[no-untyped-def]
    async def embed(texts: list[str]) -> list[list[float]]:
        return [vector for _ in texts]

    return embed


async def _doc_with_chunks(
    session: AsyncSession, texts: list[str], vectors: list[list[float]], **kw: object
) -> UUID:
    doc = await make_document(session, status=DocumentStatus.READY, **kw)
    drafts = [ChunkDraft(page=i + 1, text=t) for i, t in enumerate(texts)]
    await repo.add_chunks(session, doc.doc_id, drafts, vectors)
    return doc.doc_id


async def test_keyword_finds_contract_number(session: AsyncSession) -> None:
    texts = ["Hợp đồng số HD-2026-012 có thời hạn 24 tháng"] + [f"nội dung khác số {i}" for i in range(20)]
    await _doc_with_chunks(session, texts, [noise(i) for i in range(21)])
    results = await retrieve(session, embed_returning(noise(999)), "hợp đồng HD-2026-012", set())
    assert "HD-2026-012" in results[0].text and results[0].keyword_hit is True


async def test_vector_finds_paraphrase(session: AsyncSession) -> None:
    texts = ["thời hạn là hai năm"] + [f"đoạn {i} không liên quan" for i in range(5)]
    vectors = [unit(0)] + [unit(i + 1) for i in range(5)]
    await _doc_with_chunks(session, texts, vectors)
    results = await retrieve(session, embed_returning(unit(0)), "xyzzy plugh", set())
    assert results[0].text == "thời hạn là hai năm"
    assert results[0].similarity == pytest.approx(1.0, abs=1e-5)
    assert results[0].keyword_hit is False


async def test_scope_filter(session: AsyncSession) -> None:
    a = await _doc_with_chunks(session, ["alpha hop dong"], [unit(0)], name="A.pdf")
    b = await _doc_with_chunks(session, ["alpha hop dong"], [unit(1)], name="B.pdf")
    only_a = await retrieve(session, embed_returning(unit(0)), "alpha", {a})
    assert {r.doc_id for r in only_a} == {a}
    both = await retrieve(session, embed_returning(unit(0)), "alpha", set())
    assert {r.doc_id for r in both} == {a, b}
    assert {r.doc_name for r in only_a} == {"A.pdf"}


async def test_excludes_deleted_and_not_ready(session: AsyncSession) -> None:
    ready = await _doc_with_chunks(session, ["hop dong khop tu khoa"], [unit(0)])
    processing = await make_document(session)  # PROCESSING
    await repo.add_chunks(session, processing.doc_id, [ChunkDraft(1, "hop dong khop tu khoa")], [unit(1)])
    deleted = await _doc_with_chunks(session, ["hop dong khop tu khoa"], [unit(2)])
    await repo.soft_delete(session, deleted, datetime.now(UTC))
    results = await retrieve(session, embed_returning(unit(5)), "hop dong khop", set())
    assert {r.doc_id for r in results} == {ready}


async def test_rrf_merge(session: AsyncSession) -> None:
    # B: hạng 2 ở nhánh vector (gần e0 nhất sau A), hạng 1 ở nhánh từ khóa (duy nhất chứa cụm từ)
    close = [0.1] + [0.0] * (DIM - 1)
    close[1] = 1.0
    norm = sum(x * x for x in close) ** 0.5
    close = [x / norm for x in close]
    texts = ["doan mot", "bao hanh dac biet", "doan ba", "doan bon"]
    vectors = [unit(0), close, unit(2), unit(3)]
    await _doc_with_chunks(session, texts, vectors)
    results = await retrieve(session, embed_returning(unit(0)), "bao hanh dac biet", set())
    b = next(r for r in results if r.text == "bao hanh dac biet")
    assert b.score == pytest.approx(1 / (RRF_K + 2) + 1 / (RRF_K + 1))
    assert b.keyword_hit is True and b.similarity is not None
    assert results[0].text == "bao hanh dac biet"  # điểm cộng dồn vượt chunk chỉ có ở một nhánh


async def test_empty_corpus_returns_empty(session: AsyncSession) -> None:
    assert await retrieve(session, embed_returning(unit(0)), "bat ky", set()) == []


async def test_k_limit_and_order(session: AsyncSession) -> None:
    texts = [f"muc {i} thoi han" for i in range(12)]
    await _doc_with_chunks(session, texts, [unit(i) for i in range(12)])
    results = await retrieve(session, embed_returning(unit(3)), "thoi han", set(), k=5)
    assert len(results) == 5
    assert results == sorted(results, key=lambda r: -r.score)


@pytest.mark.perf
async def test_retrieval_perf(session: AsyncSession) -> None:
    doc = await make_document(session, status=DocumentStatus.READY)
    await session.execute(
        text(
            "INSERT INTO chunk (doc_id, page, text, embedding) "
            "SELECT :d, (g % 300) + 1, 'chunk ' || g || ' hop dong dieu khoan ' || (g % 97), "
            "CAST(ARRAY(SELECT random() + g * 0 FROM generate_series(1, :dim)) AS vector) "
            "FROM generate_series(1, 25000) AS g"
        ),
        {"d": doc.doc_id, "dim": DIM},
    )
    await session.execute(text("ANALYZE chunk"))
    started = time.perf_counter()
    results = await retrieve(session, embed_returning(noise(7)), "dieu khoan 42", set())
    elapsed = time.perf_counter() - started
    print(f"\nretrieval 25.000 chunk: {elapsed * 1000:.0f} ms")
    assert len(results) == 8
    assert elapsed <= 0.5, elapsed
