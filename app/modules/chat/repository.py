"""Hội thoại: phiên, tin nhắn, trích dẫn. Chỉ `flush`; nơi gọi quyết định `commit`."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import CitationOut, MessageStatus
from app.models.chat import ChatSession, Citation, Message

TITLE_CHARS = 60
_RUNNING = (MessageStatus.SEARCHING, MessageStatus.STREAMING)


async def create_session(
    session: AsyncSession, user_email: str, scope: list[UUID] | None = None
) -> ChatSession:
    chat = ChatSession(user_email=user_email.lower(), title=None, scope_doc_ids=scope or [])
    session.add(chat)
    await session.flush()
    await session.refresh(chat)
    return chat


async def set_title_if_empty(session: AsyncSession, session_id: UUID, question: str) -> None:
    await session.execute(
        update(ChatSession)
        .where(ChatSession.session_id == session_id, ChatSession.title.is_(None))
        .values(title=question.strip()[:TITLE_CHARS])
    )
    await session.flush()


async def get_session(
    session: AsyncSession, user_email: str, session_id: UUID
) -> ChatSession | None:
    """Chỉ trả phiên của chính người dùng (không tiết lộ phiên người khác)."""
    query = select(ChatSession).where(
        ChatSession.session_id == session_id, ChatSession.user_email == user_email.lower()
    )
    result = await session.execute(query.execution_options(populate_existing=True))
    return result.scalar_one_or_none()


async def list_sessions(
    session: AsyncSession, user_email: str, since: datetime
) -> list[ChatSession]:
    query = (
        select(ChatSession)
        .where(ChatSession.user_email == user_email.lower(), ChatSession.last_message_at >= since)
        .order_by(ChatSession.last_message_at.desc())
    )
    return list((await session.execute(query)).scalars())


async def add_message(
    session: AsyncSession,
    session_id: UUID,
    role: Literal["user", "assistant"],
    text: str,
    status: MessageStatus,
) -> Message:
    message = Message(session_id=session_id, role=role, text=text, status=status)
    session.add(message)
    await session.flush()
    await session.execute(
        update(ChatSession)
        .where(ChatSession.session_id == session_id)
        .values(last_message_at=func.now())
    )
    await session.refresh(message)
    return message


async def update_message(
    session: AsyncSession,
    message_id: UUID,
    *,
    text: str | None = None,
    status: MessageStatus | None = None,
    is_not_found: bool | None = None,
    latency_ms: int | None = None,
    error_code: str | None = None,
) -> None:
    values: dict[str, object] = {
        key: value
        for key, value in {
            "text": text,
            "status": status,
            "is_not_found": is_not_found,
            "latency_ms": latency_ms,
            "error_code": error_code,
        }.items()
        if value is not None
    }
    if values:
        await session.execute(
            update(Message).where(Message.message_id == message_id).values(**values)
        )
        await session.flush()


async def add_citations(
    session: AsyncSession, message_id: UUID, citations: list[CitationOut]
) -> None:
    for c in citations:
        session.add(
            Citation(
                message_id=message_id, idx=c.index, doc_id=c.doc_id, page=c.page, snippet=c.snippet
            )
        )
    await session.flush()


async def get_message_for_user(
    session: AsyncSession, user_email: str, message_id: UUID
) -> Message | None:
    query = (
        select(Message)
        .join(ChatSession, ChatSession.session_id == Message.session_id)
        .where(Message.message_id == message_id, ChatSession.user_email == user_email.lower())
        .execution_options(populate_existing=True)
    )
    return (await session.execute(query)).scalar_one_or_none()


async def has_running_message(session: AsyncSession, user_email: str) -> bool:
    query = (
        select(func.count())
        .select_from(Message)
        .join(ChatSession, ChatSession.session_id == Message.session_id)
        .where(
            ChatSession.user_email == user_email.lower(),
            Message.role == "assistant",
            Message.status.in_(_RUNNING),
        )
    )
    return int((await session.execute(query)).scalar_one()) > 0
