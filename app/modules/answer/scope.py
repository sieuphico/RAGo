"""Phạm vi tài liệu của câu hỏi: tự loại tài liệu đã xóa hoặc chưa sẵn sàng (US-026, EC-15)."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents import repository as documents


@dataclass(frozen=True)
class ScopeResult:
    effective: set[UUID]  # rỗng = tất cả tài liệu sẵn sàng
    removed: set[UUID]


async def normalize_scope(session: AsyncSession, requested: set[UUID]) -> ScopeResult:
    if not requested:
        return ScopeResult(set(), set())
    effective = requested & await documents.ready_doc_ids(session)
    # Toàn bộ phạm vi đã mất: quay về "tất cả tài liệu" và báo các tài liệu bị loại
    return ScopeResult(effective, requested - effective)
