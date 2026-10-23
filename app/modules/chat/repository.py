"""Hội thoại: phiên, tin nhắn, trích dẫn. Chỉ `flush`; nơi gọi quyết định `commit`."""

from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import CitationOut, MessageStatus
from app.models.chat import ChatSession, Citation, Message, Rating

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


async def set_scope(session: AsyncSession, session_id: UUID, scope: set[UUID]) -> None:
    await session.execute(
        update(ChatSession)
        .where(ChatSession.session_id == session_id)
        .values(scope_doc_ids=sorted(scope, key=str))
    )
    await session.flush()


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
    # created_at đặt ở ứng dụng: `now()` của CSDL trùng nhau trong cùng giao dịch (hỏi và đáp) nên mất thứ tự
    message = Message(
        session_id=session_id, role=role, text=text, status=status, created_at=datetime.now(UTC)
    )
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


RUNNING_MAX_AGE = timedelta(minutes=10)


async def has_running_message(
    session: AsyncSession, user_email: str, max_age: timedelta = RUNNING_MAX_AGE
) -> bool:
    """Tin nhắn SEARCHING/STREAMING quá `max_age` coi là treo (tiến trình sập), không chặn người dùng."""
    query = (
        select(func.count())
        .select_from(Message)
        .join(ChatSession, ChatSession.session_id == Message.session_id)
        .where(
            ChatSession.user_email == user_email.lower(),
            Message.role == "assistant",
            Message.status.in_(_RUNNING),
            Message.created_at >= datetime.now(UTC) - max_age,
        )
    )
    return int((await session.execute(query)).scalar_one()) > 0


async def upsert_rating(
    session: AsyncSession, message_id: UUID, value: str, reason_code: str | None
) -> None:
    """Gửi lại thì ghi đè (API-11)."""
    stmt = insert(Rating).values(message_id=message_id, value=value, reason_code=reason_code)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Rating.message_id],
        set_={"value": stmt.excluded.value, "reason_code": stmt.excluded.reason_code},
    )
    await session.execute(stmt)
    await session.flush()


async def delete_sessions_before(session: AsyncSession, cutoff: datetime) -> int:
    """Xóa phiên quá hạn; tin nhắn, trích dẫn, đánh giá xóa dây chuyền."""
    result = await session.execute(delete(ChatSession).where(ChatSession.last_message_at < cutoff))
    await session.flush()
    return int(result.rowcount)  # type: ignore[attr-defined]
