from uuid import uuid4

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import CurrentUser, Role
from app.modules.telemetry.service import emit
from tests.integration.helpers import CSRF, login


async def _count(session: AsyncSession, event: str | None = None) -> int:
    """Đăng nhập cũng phát `auth_*` nên test lọc theo tên sự kiện khi cần."""
    sql = "SELECT count(*) FROM telemetry_event"
    params: dict[str, str] = {}
    if event:
        sql += " WHERE event = :e"
        params = {"e": event}
    return int((await session.execute(text(sql), params)).scalar_one())


async def test_unknown_field_rejected_by_api(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    body = {"event": "citation_clicked", "props": {
        "question_id": str(uuid4()), "doc_id": str(uuid4()), "page": 3, "text": "abc"}}  # fmt: skip
    resp = await client.post("/api/v1/telemetry/events", json=body, headers=CSRF)
    assert resp.status_code == 422 and resp.json()["code"] == "VALIDATION_ERROR"
    assert await _count(session, "citation_clicked") == 0


async def test_server_event_from_client_rejected(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    body = {"event": "answer_completed", "props": {
        "question_id": str(uuid4()), "latency_ms": 1, "citation_count": 0,
        "distinct_doc_count": 0, "is_not_found": True}}  # fmt: skip
    resp = await client.post("/api/v1/telemetry/events", json=body, headers=CSRF)
    assert resp.status_code == 422


async def test_valid_client_event_stored_without_email(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    body = {"event": "suggestion_clicked", "props": {"suggestion_index": 1}}
    resp = await client.post("/api/v1/telemetry/events", json=body, headers=CSRF)
    assert resp.status_code == 204
    row = (
        await session.execute(
            text(
                "SELECT event, anon_user_id, session_id, props FROM telemetry_event "
                "WHERE event = 'suggestion_clicked'"
            )
        )
    ).one()
    assert row[0] == "suggestion_clicked" and row[3] == {"suggestion_index": 1}
    assert "lan" not in row[1] and len(row[1]) == 64 and row[2]


async def test_requires_auth(client: httpx.AsyncClient) -> None:
    body = {"event": "answer_copied", "props": {"question_id": str(uuid4())}}
    resp = await client.post("/api/v1/telemetry/events", json=body, headers=CSRF)
    assert resp.status_code == 401


async def test_emit_writes_row(session: AsyncSession) -> None:
    user = CurrentUser("minh@congty.vn", Role.TEAM_LEAD)
    await emit(session, user, "sid-1", "auth_login_succeeded", is_first_login=True)
    assert await _count(session) == 1


async def test_emit_invalid_props_not_stored(session: AsyncSession) -> None:
    user = CurrentUser("minh@congty.vn", Role.TEAM_LEAD)
    await emit(session, user, "sid-1", "auth_login_succeeded", email="minh@congty.vn")
    await emit(session, user, "sid-1", "khong_co_su_kien")
    assert await _count(session) == 0
