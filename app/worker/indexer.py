"""Nhúng chunk theo lô và ghi chunk cùng vector vào CSDL."""

from collections.abc import Awaitable, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ChunkDraft
from app.modules.documents import repository as documents

EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]


async def index_document(
    session: AsyncSession,
    embed: EmbedFn,
    doc_id: UUID,
    chunks: list[ChunkDraft],
    *,
    batch_size: int,
    dim: int,
) -> int:
    """Chạy lại an toàn: xóa chunk cũ rồi ghi mới. Nhúng hết trước khi ghi nên lỗi giữa chừng
    không để lại dòng nào. Không tự thử lại (cổng AI làm, T-301)."""
    vectors: list[list[float]] = []
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        batch_vectors = await embed([c.text for c in batch])
        if len(batch_vectors) != len(batch) or any(len(v) != dim for v in batch_vectors):
            raise ValueError("embedding dim")
        vectors.extend(batch_vectors)
    await documents.delete_chunks(session, doc_id)
    return await documents.add_chunks(session, doc_id, chunks, vectors)
