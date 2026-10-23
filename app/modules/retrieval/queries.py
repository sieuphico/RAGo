"""Truy vấn SQL cho hai nhánh truy xuất (AD-03): vector (pgvector) và từ khóa (tsvector)."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession

# Lọc chung: chỉ tài liệu READY chưa xóa; phạm vi rỗng = tất cả
_FILTER = """
    d.status = 'READY' AND d.deleted_at IS NULL
    AND (cardinality(:scope) = 0 OR c.doc_id = ANY(:scope))
"""

_COLUMNS = "c.chunk_id, c.doc_id, d.name AS doc_name, c.page, c.text"

_VECTOR_SQL = f"""
    SELECT {_COLUMNS}, 1 - (c.embedding <=> CAST(:qvec AS vector)) AS similarity
    FROM chunk c JOIN document d ON d.doc_id = c.doc_id
    WHERE {_FILTER}
    ORDER BY c.embedding <=> CAST(:qvec AS vector)
    LIMIT :n
"""

_KEYWORD_SQL = f"""
    SELECT {_COLUMNS}, ts_rank_cd(c.tsv, q.query) AS rank
    FROM chunk c JOIN document d ON d.doc_id = c.doc_id,
         plainto_tsquery('simple', cwd_unaccent(:q)) AS q(query)
    WHERE {_FILTER} AND c.tsv @@ q.query
    ORDER BY rank DESC, c.chunk_id
    LIMIT :n
"""

_SCOPE = bindparam("scope", type_=ARRAY(PG_UUID(as_uuid=True)))


@dataclass(frozen=True)
class Hit:
    chunk_id: UUID
    doc_id: UUID
    doc_name: str
    page: int
    text: str
    similarity: float | None = None


def vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(repr(float(x)) for x in vector) + "]"


async def vector_hits(
    session: AsyncSession, qvec: list[float], scope: set[UUID], n: int
) -> list[Hit]:
    stmt = text(_VECTOR_SQL).bindparams(_SCOPE)
    rows = await session.execute(
        stmt, {"qvec": vector_literal(qvec), "scope": list(scope), "n": n}
    )
    return [
        Hit(r.chunk_id, r.doc_id, r.doc_name, r.page, r.text, float(r.similarity))
        for r in rows
    ]


async def keyword_hits(session: AsyncSession, query: str, scope: set[UUID], n: int) -> list[Hit]:
    stmt = text(_KEYWORD_SQL).bindparams(_SCOPE)
    rows = await session.execute(stmt, {"q": query, "scope": list(scope), "n": n})
    return [Hit(r.chunk_id, r.doc_id, r.doc_name, r.page, r.text) for r in rows]
