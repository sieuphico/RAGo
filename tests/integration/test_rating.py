from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import MessageStatus, Role
from app.modules.chat import repository as chat
from tests.integration.helpers import CSRF, login


@pytest.fixture
def only_features(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    def use(value: str) -> None:
        monkeypatch.setenv("CWD_FEATURES", value)
        get_settings.cache_clear()

    yield use
    monkeypatch.delenv("CWD_FEATURES", raising=False)
    get_settings.cache_clear()


async def _answer(
    session: AsyncSession, email: str, status: MessageStatus = MessageStatus.COMPLETED,
    role: str = "assistant",
) -> UUID:  # fmt: skip
    chat_session = await chat.create_session(session, email)
    message = await chat.add_message(session, chat_session.session_id, role, "Đáp", status)  # type: ignore[arg-type]
    return message.message_id


async def _rows(session: AsyncSession) -> list[Any]:
    return list((await session.execute(text("SELECT value, reason_code FROM rating"))).all())


def _url(message_id: UUID) -> str:
    return f"/api/v1/chat/messages/{message_id}/rating"


async def test_rate_up(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn")
    resp = await client.post(_url(mid), json={"value": "UP", "reasonCode": None}, headers=CSRF)
    assert resp.status_code == 204
    assert [tuple(r) for r in await _rows(session)] == [("UP", None)]
    props = (
        await session.execute(
            text("SELECT props FROM telemetry_event WHERE event = 'answer_rated'")
        )
    ).scalar_one()
    assert props == {"question_id": str(mid), "rating": "up", "reason_code": None}


async def test_rate_down_with_reason(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn")
    body = {"value": "DOWN", "reasonCode": "WRONG_CITATION"}
    assert (await client.post(_url(mid), json=body, headers=CSRF)).status_code == 204
    assert [tuple(r) for r in await _rows(session)] == [("DOWN", "WRONG_CITATION")]


async def test_rate_overwrite(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn")
    await client.post(_url(mid), json={"value": "UP"}, headers=CSRF)
    await client.post(_url(mid), json={"value": "DOWN", "reasonCode": "OTHER"}, headers=CSRF)
    assert [tuple(r) for r in await _rows(session)] == [("DOWN", "OTHER")]


async def test_rate_other_user_forbidden(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    mid = await _answer(session, "lan@congty.vn")
    resp = await client.post(_url(mid), json={"value": "UP"}, headers=CSRF)
    assert resp.status_code == 404 and resp.json()["code"] == "NOT_FOUND"
    assert (await client.post(_url(uuid4()), json={"value": "UP"}, headers=CSRF)).status_code == 404


async def test_rate_streaming_rejected(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    for status, role in ((MessageStatus.STREAMING, "assistant"), (MessageStatus.COMPLETED, "user")):
        mid = await _answer(session, "lan@congty.vn", status, role)
        resp = await client.post(_url(mid), json={"value": "UP"}, headers=CSRF)
        assert resp.status_code == 409 and resp.json()["code"] == "MESSAGE_NOT_RATEABLE"


async def test_not_found_answer_is_rateable(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn", MessageStatus.NOT_FOUND)
    assert (await client.post(_url(mid), json={"value": "DOWN"}, headers=CSRF)).status_code == 204


async def test_bad_reason(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn")
    bad = await client.post(_url(mid), json={"value": "DOWN", "reasonCode": "ABC"}, headers=CSRF)
    up_with_reason = await client.post(
        _url(mid), json={"value": "UP", "reasonCode": "OTHER"}, headers=CSRF
    )
    assert bad.status_code == 422 and up_with_reason.status_code == 422
    assert bad.json()["code"] == "VALIDATION_ERROR" and await _rows(session) == []


async def test_flag_off(client: httpx.AsyncClient, session: AsyncSession, only_features) -> None:  # type: ignore[no-untyped-def]
    only_features("history")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    mid = await _answer(session, "lan@congty.vn")
    assert (await client.post(_url(mid), json={"value": "UP"}, headers=CSRF)).status_code == 404
