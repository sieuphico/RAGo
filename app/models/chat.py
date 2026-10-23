"""Mô hình khớp migration 002."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain import MessageStatus
from app.models.base import Base


class ChatSession(Base):
    __tablename__ = "chat_session"

    session_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_email: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    scope_doc_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), default=list, server_default="{}"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", order_by="Message.created_at", lazy="selectin"
    )


class Message(Base):
    __tablename__ = "message"

    message_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_session.session_id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text, default="", server_default="")
    status: Mapped[MessageStatus] = mapped_column(
        SAEnum(
            MessageStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            length=16,
        )
    )
    is_not_found: Mapped[bool] = mapped_column(default=False, server_default="false")
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped[ChatSession] = relationship(back_populates="messages")
    citations: Mapped[list["Citation"]] = relationship(
        order_by="Citation.idx", lazy="selectin"
    )
    rating: Mapped["Rating | None"] = relationship(lazy="selectin", uselist=False)


class Citation(Base):
    __tablename__ = "citation"

    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("message.message_id", ondelete="CASCADE"), primary_key=True
    )
    idx: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document.doc_id"))
    page: Mapped[int] = mapped_column(Integer)
    snippet: Mapped[str] = mapped_column(Text)


class Rating(Base):
    __tablename__ = "rating"

    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("message.message_id", ondelete="CASCADE"), primary_key=True
    )
    value: Mapped[str] = mapped_column(Text)
    reason_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
