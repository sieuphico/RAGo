from datetime import UTC, datetime, timedelta
from uuid import UUID

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import CitationOut, DocumentStatus, MessageStatus, Role
from app.modules.chat import repository as chat
from app.modules.documents import repository as repo
from app.worker.expire_history import expire_history
from tests.fixtures.documents import make_document
from tests.integration.helpers import login

NOW = datetime(2026, 12, 1, 3, tzinfo=UTC)


@pytest.fixture
def only_features(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    def use(value: str) -> None:
        monkeypatch.setenv("CWD_FEATURES", value)
        get_settings.cache_clear()

    yield use
    monkeypatch.delenv("CWD_FEATURES", raising=False)
    get_settings.cache_clear()


async def test_history_own_sessions_only(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await chat.create_session(session, "lan@congty.vn")
    await chat.create_session(session, "lan@congty.vn")
    await chat.create_session(session, "minh@congty.vn")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    items = (await client.get("/api/v1/chat/sessions")).json()["items"]
    assert len(items) == 2
    assert set(items[0]) == {"sessionId", "title", "createdAt", "lastMessageAt"}


async def test_history_window_90_days(client: httpx.AsyncClient, session: AsyncSession) -> None:
    old = await chat.create_session(session, "lan@congty.vn")
    await session.execute(
        text("UPDATE chat_session SET last_message_at = :t WHERE session_id = :s"),
        {"t": datetime.now(UTC) - timedelta(days=100), "s": old.session_id},
    )
    await chat.create_session(session, "lan@congty.vn")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert len((await client.get("/api/v1/chat/sessions")).json()["items"]) == 1


async def test_open_other_user_session(client: httpx.AsyncClient, session: AsyncSession) -> None:
    other = await chat.create_session(session, "lan@congty.vn")
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.get(f"/api/v1/chat/sessions/{other.session_id}")
    assert resp.status_code == 404 and resp.json()["code"] == "SESSION_NOT_FOUND"


async def _conversation(session: AsyncSession) -> tuple[UUID, UUID, UUID]:
    doc_a = await make_document(session, name="A.pdf", status=DocumentStatus.READY)
    doc_b = await make_document(session, name="B.pdf", status=DocumentStatus.READY)
    chat_session = await chat.create_session(session, "lan@congty.vn")
    sid = chat_session.session_id
    await chat.add_message(session, sid, "user", "Thời hạn?", MessageStatus.COMPLETED)
    answer = await chat.add_message(session, sid, "assistant", "24 tháng [[1]][[2]]", MessageStatus.COMPLETED)
    await chat.add_citations(
        session,
        answer.message_id,
        [CitationOut(1, doc_a.doc_id, "A.pdf", 3, "đoạn a"), CitationOut(2, doc_b.doc_id, "B.pdf", 5, "đoạn b")],
    )
    await chat.upsert_rating(session, answer.message_id, "UP", None)
    return sid, doc_a.doc_id, doc_b.doc_id


async def test_session_detail_shape(client: httpx.AsyncClient, session: AsyncSession) -> None:
    sid, doc_a, _ = await _conversation(session)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    body = (await client.get(f"/api/v1/chat/sessions/{sid}")).json()
    assert set(body) == {"sessionId", "title", "createdAt", "scopeDocIds", "messages"}
    user_msg, answer = body["messages"]
    assert user_msg["role"] == "user" and user_msg["citations"] == [] and user_msg["rating"] is None
    assert answer["rating"] == "UP" and answer["status"] == "COMPLETED"
    assert [c["index"] for c in answer["citations"]] == [1, 2]
    assert answer["citations"][0] == {
        "index": 1, "docId": str(doc_a), "docName": "A.pdf", "page": 3,
        "snippet": "đoạn a", "deleted": False,
    }  # fmt: skip
    opened = (
        await session.execute(
            text("SELECT props FROM telemetry_event WHERE event = 'history_session_opened'")
        )
    ).scalar_one()
    assert opened == {"session_age_days": 0}


async def test_deleted_doc_flag(client: httpx.AsyncClient, session: AsyncSession) -> None:
    sid, _, doc_b = await _conversation(session)
    await repo.soft_delete(session, doc_b, datetime.now(UTC))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    answer = (await client.get(f"/api/v1/chat/sessions/{sid}")).json()["messages"][1]
    assert [c["deleted"] for c in answer["citations"]] == [False, True]


async def test_expired_sessions_removed(session: AsyncSession) -> None:
    for name, age in (("old", 91), ("new", 89)):
        chat_session = await chat.create_session(session, f"{name}@congty.vn")
        await chat.add_message(
            session, chat_session.session_id, "user", name, MessageStatus.COMPLETED
        )
        await session.execute(
            text("UPDATE chat_session SET last_message_at = :t WHERE session_id = :s"),
            {"t": NOW - timedelta(days=age), "s": chat_session.session_id},
        )
    assert await expire_history(session, NOW) == 1
    owners = (await session.execute(text("SELECT user_email FROM chat_session"))).scalars().all()
    assert list(owners) == ["new@congty.vn"]
    texts = (await session.execute(text("SELECT text FROM message"))).scalars().all()
    assert list(texts) == ["new"]  # tin nhắn của phiên quá hạn bị xóa dây chuyền


async def test_flag_off(client: httpx.AsyncClient, session: AsyncSession, only_features) -> None:  # type: ignore[no-untyped-def]
    only_features("summary")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert (await client.get("/api/v1/chat/sessions")).status_code == 404
