from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import DocumentStatus
from app.models.document import Document
from app.modules.documents import repository as repo


async def make_document(session: AsyncSession, **kw: Any) -> Document:
    """Tạo tài liệu thử; `status` mặc định PROCESSING, đặt READY/FAILED... nếu truyền vào."""
    status = kw.pop("status", DocumentStatus.PROCESSING)
    doc = await repo.add(
        session,
        name=kw.pop("name", "a.pdf"),
        uploaded_by=kw.pop("uploaded_by", "minh@congty.vn"),
        size_bytes=kw.pop("size_bytes", 1000),
        file_key=kw.pop("file_key", f"docs/{uuid4()}.pdf"),
    )
    if status != DocumentStatus.PROCESSING:
        doc = await repo.set_status(session, doc.doc_id, status, **kw)
    return doc
