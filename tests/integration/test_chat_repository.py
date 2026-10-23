from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import CitationOut, MessageStatus
from app.modules.chat import repository as chat
from tests.fixtures.documents import make_document


async def test_get_session_other_user_none(session: AsyncSession) -> None:
    mine = await chat.create_session(session, "lan@congty.vn")
    assert await chat.get_session(session, "minh@congty.vn", mine.session_id) is None
    found = await chat.get_session(session, "LAN@congty.vn", mine.session_id)
    assert found is not None and found.title is None


async def test_list_respects_window(session: AsyncSession) -> None:
    now = datetime.now(UTC)
    recent = await chat.create_session(session, "lan@congty.vn")
    old = await chat.create_session(session, "lan@congty.vn")
    for chat_id, age in ((recent.session_id, 10), (old.session_id, 100)):
        await session.execute(
            text("UPDATE chat_session SET last_message_at = :t WHERE session_id = :s"),
            {"t": now - timedelta(days=age), "s": chat_id},
        )
    rows = await chat.list_sessions(session, "lan@congty.vn", now - timedelta(days=90))
    assert [r.session_id for r in rows] == [recent.session_id]
    assert await chat.list_sessions(session, "minh@congty.vn", now - timedelta(days=90)) == []


async def test_title_truncation(session: AsyncSession) -> None:
    session_id = (await chat.create_session(session, "lan@congty.vn")).session_id
    await chat.set_title_if_empty(session, session_id, "x" * 75)
    await chat.set_title_if_empty(session, session_id, "y")
    fresh = await chat.get_session(session, "lan@congty.vn", session_id)
    assert fresh is not None and fresh.title == "x" * 60


async def test_has_running_message(session: AsyncSession) -> None:
    chat_session = await chat.create_session(session, "lan@congty.vn")
    assert await chat.has_running_message(session, "lan@congty.vn") is False
    message = await chat.add_message(
        session, chat_session.session_id, "assistant", "", MessageStatus.STREAMING
    )
    assert await chat.has_running_message(session, "lan@congty.vn") is True
    assert await chat.has_running_message(session, "minh@congty.vn") is False
    await chat.update_message(session, message.message_id, status=MessageStatus.COMPLETED)
    assert await chat.has_running_message(session, "lan@congty.vn") is False


async def test_add_citations_roundtrip(session: AsyncSession) -> None:
    doc = await make_document(session, name="A.pdf")
    chat_session = await chat.create_session(session, "lan@congty.vn")
    await chat.add_message(session, chat_session.session_id, "user", "Hỏi?", MessageStatus.COMPLETED)
    answer = await chat.add_message(
        session, chat_session.session_id, "assistant", "Đáp [[1]]", MessageStatus.COMPLETED
    )
    await chat.add_citations(
        session, answer.message_id, [CitationOut(1, doc.doc_id, "A.pdf", 3, "…")]
    )
    loaded = await chat.get_session(session, "lan@congty.vn", chat_session.session_id)
    assert loaded is not None
    assistant = next(m for m in loaded.messages if m.role == "assistant")
    assert [(c.idx, c.page, c.doc_id) for c in assistant.citations] == [(1, 3, doc.doc_id)]


async def test_update_message_fields_and_other_user_access(session: AsyncSession) -> None:
    chat_session = await chat.create_session(session, "lan@congty.vn")
    message = await chat.add_message(
        session, chat_session.session_id, "assistant", "", MessageStatus.SEARCHING
    )
    await chat.update_message(
        session, message.message_id, text="xong", is_not_found=True, latency_ms=1200, error_code=None
    )
    mine = await chat.get_message_for_user(session, "lan@congty.vn", message.message_id)
    assert mine is not None and (mine.text, mine.is_not_found, mine.latency_ms) == ("xong", True, 1200)
    assert await chat.get_message_for_user(session, "minh@congty.vn", message.message_id) is None
    assert await chat.get_message_for_user(session, "lan@congty.vn", uuid4()) is None


async def test_add_message_touches_last_message_at(session: AsyncSession) -> None:
    chat_session = await chat.create_session(session, "lan@congty.vn")
    await session.execute(
        text("UPDATE chat_session SET last_message_at = :t"),
        {"t": datetime(2020, 1, 1, tzinfo=UTC)},
    )
    await chat.add_message(session, chat_session.session_id, "user", "hi", MessageStatus.COMPLETED)
    stamp = (await session.execute(text("SELECT last_message_at FROM chat_session"))).scalar_one()
    assert stamp.year >= 2026
