import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.adapters.ai_gateway import AiGateway
from app.api.chat import to_sse_frame
from app.api.deps import get_answer_service
from app.core.config import get_settings
from app.core.db import get_session
from app.domain import (
    ChunkDraft,
    CitationEvent,
    CitationOut,
    DocumentStatus,
    DoneEvent,
    ErrorEvent,
    Role,
    StatusEvent,
    TokenEvent,
)
from app.main import create_app
from app.modules.answer.running import RunningAnswers
from app.modules.answer.service import AnswerService
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document
from tests.integration.helpers import CSRF, login
from tests.integration.test_answer_interrupts import SlowProvider
from tests.integration.test_answer_service import unit

Maker = async_sessionmaker[AsyncSession]


@pytest.fixture
async def maker(test_database_url: str) -> AsyncIterator[Maker]:
    """Dữ liệu được commit thật (nhiều yêu cầu đồng thời) nên dọn lại sau mỗi test."""
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    async with factory() as s:
        await s.execute(
            text(
                "TRUNCATE document, chat_session, allow_list_entry, job, audit_log, "
                "telemetry_event, ai_usage CASCADE"
            )
        )
        await s.commit()
    await engine.dispose()


def _build(maker: Maker, provider: SlowProvider) -> tuple[FastAPI, RunningAnswers]:
    app = create_app()
    settings = get_settings()
    running = RunningAnswers()
    service = AnswerService(maker, AiGateway(provider, settings, maker), settings, running=running)

    async def _session() -> AsyncIterator[AsyncSession]:
        async with maker() as session:
            yield session

    app.dependency_overrides[get_session] = _session
    app.dependency_overrides[get_answer_service] = lambda: service
    return app, running


async def _seed(maker: Maker) -> None:
    async with maker() as s:
        doc = await make_document(s, name="HD_ABC_2026.pdf", status=DocumentStatus.READY)
        await repo.add_chunks(s, doc.doc_id, [ChunkDraft(page=12, text="thời hạn 24 tháng")], [unit(0)])
        await s.commit()


async def _client(app: FastAPI, maker: Maker, email: str, role: Role) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    client = httpx.AsyncClient(transport=transport, base_url="https://test")
    async with maker() as s:
        await login(client, s, email, role)
        await s.commit()
    return client


def _frames(body: str) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for block in body.strip().split("\n\n"):
        lines = block.split("\n")
        if lines[0].startswith(":"):
            continue
        assert lines[0].startswith("event: ") and lines[1].startswith("data: ") and len(lines) == 2
        out.append((lines[0][7:], json.loads(lines[1][6:])))
    return out


async def _new_session(client: httpx.AsyncClient) -> str:
    resp = await client.post("/api/v1/chat/sessions", json={}, headers=CSRF)
    assert resp.status_code == 201
    return str(resp.json()["sessionId"])


async def test_create_session(maker: Maker) -> None:
    app, _ = _build(maker, SlowProvider())
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    resp = await client.post("/api/v1/chat/sessions", json={}, headers=CSRF)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] is None and body["createdAt"].endswith("Z") and body["sessionId"]


async def test_sse_event_order(maker: Maker) -> None:
    await _seed(maker)
    app, _ = _build(maker, SlowProvider())
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    resp = await client.post(
        f"/api/v1/chat/sessions/{sid}/messages", json={"text": "Thời hạn bao lâu?"}, headers=CSRF
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    assert resp.headers["x-accel-buffering"] == "no" and resp.headers["cache-control"] == "no-cache"
    frames = _frames(resp.text)
    names = [name for name, _ in frames]
    assert names[0] == "status" and names[-1] == "done"
    assert set(names) == {"status", "citation", "token", "done"}
    assert names.index("citation") < min(i for i, (n, d) in enumerate(frames) if n == "token" and "[[1]]" in d["text"])
    status, done = frames[0][1], frames[-1][1]
    assert status["stage"] == "searching" and status["docCount"] == 1 and status["scopeRemoved"] == []
    assert done["citationCount"] == 1 and done["isNotFound"] is False and done["stopped"] is False
    assert frames[names.index("citation")][1]["docName"] == "HD_ABC_2026.pdf"


async def test_question_validation(maker: Maker) -> None:
    provider = SlowProvider()
    app, _ = _build(maker, provider)
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    url = f"/api/v1/chat/sessions/{sid}/messages"
    empty = await client.post(url, json={"text": "   "}, headers=CSRF)
    assert empty.status_code == 400 and empty.json()["code"] == "QUESTION_EMPTY"
    long = await client.post(url, json={"text": "a" * 2001}, headers=CSRF)
    assert long.status_code == 400 and long.json()["code"] == "QUESTION_TOO_LONG"
    assert provider.embed_calls == 0 and provider.generate_calls == 0
    exact = await client.post(url, json={"text": " " + "a" * 2000 + " "}, headers=CSRF)
    assert exact.status_code == 200  # 2.000 ký tự sau khi bỏ khoảng trắng đầu cuối là hợp lệ


async def test_request_schema_validation(maker: Maker) -> None:
    app, _ = _build(maker, SlowProvider())
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    url = f"/api/v1/chat/sessions/{sid}/messages"
    assert (await client.post(url, json={"x": 1}, headers=CSRF)).json()["code"] == "VALIDATION_ERROR"
    too_many = {"text": "hỏi", "scopeDocIds": [str(uuid4()) for _ in range(51)]}
    assert (await client.post(url, json=too_many, headers=CSRF)).status_code == 422


async def test_session_ownership(maker: Maker) -> None:
    app, _ = _build(maker, SlowProvider())
    lan = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    minh = await _client(app, maker, "minh@congty.vn", Role.TEAM_LEAD)
    sid = await _new_session(lan)
    resp = await minh.post(f"/api/v1/chat/sessions/{sid}/messages", json={"text": "hỏi"}, headers=CSRF)
    assert resp.status_code == 404 and resp.json()["code"] == "SESSION_NOT_FOUND"


async def _running_message_id(maker: Maker) -> str:
    for _ in range(40):
        async with maker() as s:
            row = (
                await s.execute(
                    text("SELECT message_id FROM message WHERE role = 'assistant' ORDER BY created_at")
                )
            ).first()
        if row:
            return str(row[0])
        await asyncio.sleep(0.05)
    raise AssertionError("không thấy tin nhắn đang chạy")


async def test_question_in_progress(maker: Maker) -> None:
    await _seed(maker)
    app, _ = _build(maker, SlowProvider(first_delay=2))
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    url = f"/api/v1/chat/sessions/{sid}/messages"
    first = asyncio.create_task(client.post(url, json={"text": "câu 1"}, headers=CSRF))
    await _running_message_id(maker)
    second = await client.post(url, json={"text": "câu 2"}, headers=CSRF)
    assert second.status_code == 409
    assert second.json() == {"code": "QUESTION_IN_PROGRESS", "retryable": True}
    assert (await first).status_code == 200


async def test_stop_endpoint(maker: Maker) -> None:
    await _seed(maker)
    app, _ = _build(maker, SlowProvider(first_delay=5))
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    stream = asyncio.create_task(
        client.post(f"/api/v1/chat/sessions/{sid}/messages", json={"text": "câu hỏi"}, headers=CSRF)
    )
    mid = await _running_message_id(maker)
    await asyncio.sleep(0.2)
    resp = await client.post(f"/api/v1/chat/messages/{mid}/stop", json={}, headers=CSRF)
    assert resp.status_code == 200 and resp.json() == {"messageId": mid, "status": "STOPPED"}
    frames = _frames((await asyncio.wait_for(stream, 2)).text)
    assert frames[-1][0] == "done" and frames[-1][1]["stopped"] is True
    again = await client.post(f"/api/v1/chat/messages/{mid}/stop", json={}, headers=CSRF)
    assert again.status_code == 200 and again.json()["status"] == "STOPPED"  # đã xong: không lỗi


async def test_stop_other_user_404(maker: Maker) -> None:
    await _seed(maker)
    app, _ = _build(maker, SlowProvider())
    lan = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    minh = await _client(app, maker, "minh@congty.vn", Role.TEAM_LEAD)
    sid = await _new_session(lan)
    await lan.post(f"/api/v1/chat/sessions/{sid}/messages", json={"text": "hỏi"}, headers=CSRF)
    mid = await _running_message_id(maker)
    resp = await minh.post(f"/api/v1/chat/messages/{mid}/stop", json={}, headers=CSRF)
    assert resp.status_code == 404 and resp.json()["code"] == "NOT_FOUND"


async def test_csrf_on_stream(maker: Maker) -> None:
    app, _ = _build(maker, SlowProvider())
    client = await _client(app, maker, "lan@congty.vn", Role.BD_USER)
    sid = await _new_session(client)
    resp = await client.post(f"/api/v1/chat/sessions/{sid}/messages", json={"text": "hỏi"})
    assert resp.status_code == 403 and resp.json()["code"] == "CSRF_REJECTED"


async def test_sponsor_cannot_chat(maker: Maker) -> None:
    app, _ = _build(maker, SlowProvider())
    client = await _client(app, maker, "ntt@congty.vn", Role.SPONSOR)
    resp = await client.post("/api/v1/chat/sessions", json={}, headers=CSRF)
    assert resp.status_code == 403


def test_to_sse_frame_shapes() -> None:
    mid, did = uuid4(), uuid4()
    status = to_sse_frame(StatusEvent(message_id=mid, doc_count=3)).decode()
    assert status.startswith("event: status\ndata: ") and status.endswith("\n\n")
    assert '"docCount":3' in status and f'"messageId":"{mid}"' in status and '"scopeRemoved":[]' in status
    cite = to_sse_frame(CitationEvent(CitationOut(1, did, "Tên.pdf", 4, "…"))).decode()
    assert '"docName":"Tên.pdf"' in cite and "\\u" not in cite  # ensure_ascii=False
    token = to_sse_frame(TokenEvent("Xin chào")).decode()
    assert token == 'event: token\ndata: {"text":"Xin chào"}\n\n'
    done = to_sse_frame(DoneEvent(mid, 2, True, "NO_EVIDENCE", None, False)).decode()
    assert '"notFoundReason":"NO_EVIDENCE"' in done and '"notice":null' in done
    error = to_sse_frame(ErrorEvent("TIMEOUT", True)).decode()
    assert error == 'event: error\ndata: {"code":"TIMEOUT","retryable":true}\n\n'
