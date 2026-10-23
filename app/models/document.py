"""Mô hình khớp migration 001.

`chunk.embedding` (vector) và `chunk.tsv` (cột sinh) không ánh xạ ở đây: vector được ghi
bằng SQL trực tiếp trong repository, tránh thêm thư viện ngoài danh sách đã duyệt.
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain import DocumentStatus, FailureReason
from app.models.base import Base


def _enum[E: (DocumentStatus, FailureReason)](cls: type[E]) -> SAEnum:
    return SAEnum(cls, native_enum=False, create_constraint=False, validate_strings=True,
                  length=32)  # fmt: skip


class Document(Base):
    __tablename__ = "document"

    doc_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text)
    uploaded_by: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(_enum(DocumentStatus))
    failure_reason: Mapped[FailureReason | None] = mapped_column(
        _enum(FailureReason), nullable=True
    )
    used_ocr: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    file_key: Mapped[str] = mapped_column(Text, unique=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Chunk(Base):
    __tablename__ = "chunk"

    chunk_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    doc_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document.doc_id", ondelete="CASCADE"))
    page: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    lang: Mapped[str | None] = mapped_column(String, nullable=True)


class Suggestion(Base):
    __tablename__ = "suggestion"

    doc_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document.doc_id", ondelete="CASCADE"), primary_key=True
    )
    questions: Mapped[list[str]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
