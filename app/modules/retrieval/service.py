"""Truy xuất lai: vector + từ khóa, hợp nhất bằng RRF, lọc theo phạm vi tài liệu."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ScoredChunk
from app.modules.retrieval import queries
from app.worker.indexer import EmbedFn

RRF_K = 60


async def retrieve(
    session: AsyncSession, embed: EmbedFn, query: str, scope: set[UUID], k: int = 8
) -> list[ScoredChunk]:
    """Trả `k` chunk điểm RRF cao nhất. `scope` rỗng = mọi tài liệu READY."""
    qvec = (await embed([query]))[0]
    vector = await queries.vector_hits(session, qvec, scope, 2 * k)
    keyword = await queries.keyword_hits(session, query, scope, 2 * k)

    scores: dict[UUID, float] = {}
    similarity: dict[UUID, float] = {}
    keyword_ids: set[UUID] = set()
    rows: dict[UUID, queries.Hit] = {}
    for rank, hit in enumerate(vector, start=1):
        scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1 / (RRF_K + rank)
        assert hit.similarity is not None
        similarity[hit.chunk_id] = hit.similarity
        rows[hit.chunk_id] = hit
    for rank, hit in enumerate(keyword, start=1):
        scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1 / (RRF_K + rank)
        keyword_ids.add(hit.chunk_id)
        rows.setdefault(hit.chunk_id, hit)

    ordered = sorted(scores, key=lambda cid: (-scores[cid], str(cid)))[:k]
    return [
        ScoredChunk(
            chunk_id=cid,
            doc_id=rows[cid].doc_id,
            doc_name=rows[cid].doc_name,
            page=rows[cid].page,
            text=rows[cid].text,
            score=scores[cid],
            similarity=similarity.get(cid),
            keyword_hit=cid in keyword_ids,
        )
        for cid in ordered
    ]
