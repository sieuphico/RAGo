import asyncio
import json
import socket
from collections.abc import AsyncGenerator, AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
import uvicorn
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.domain import DocumentStatus, Role
from app.modules.auth.cookies import SESSION_COOKIE, issue_cookie
from app.modules.documents import events
from app.modules.documents.events import StatusHub, event_stream, publish_status
from app.modules.users import repository as users


@pytest.fixture
async def hub(test_database_url: str) -> AsyncIterator[StatusHub]:
    hub = StatusHub()
    await hub.start(test_database_url)
    yield hub
    await hub.stop()


@pytest.fixture
async def publisher(test_database_url: str) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(test_database_url, poolclass=NullPool)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def _never() -> bool:
    return False


async def _next_status(stream: AsyncGenerator[str], *, timeout: float = 2.0) -> str:
    async with asyncio.timeout(timeout):
        async for chunk in stream:
            if chunk.startswith("event: status"):
                return chunk
    raise AssertionError("luồng kết thúc")


async def test_status_event_delivered(
    hub: StatusHub, publisher: async_sessionmaker[AsyncSession]
) -> None:
    doc_id = uuid4()
    stream = event_stream(hub, _never)
    assert await anext(stream) == ": connected\n\n"
    async with publisher() as s:
        await publish_status(s, doc_id, DocumentStatus.READY, page_count=3)
        await s.commit()
    chunk = await _next_status(stream)
    data = json.loads(chunk.split("data: ", 1)[1])
    assert data == {"docId": str(doc_id), "status": "READY", "failureReason": None, "pageCount": 3}
    await stream.aclose()


async def test_no_notify_without_commit(
    hub: StatusHub, publisher: async_sessionmaker[AsyncSession]
) -> None:
    stream = event_stream(hub, _never)
    await anext(stream)
    async with publisher() as s:
        await publish_status(s, uuid4(), DocumentStatus.READY)
        await s.rollback()
    with pytest.raises(TimeoutError):
        await _next_status(stream, timeout=1.0)
    await stream.aclose()


async def test_disconnect_cleanup(hub: StatusHub) -> None:
    stream = event_stream(hub, _never)
    await anext(stream)
    assert len(hub.subscribers) == 1
    await stream.aclose()
    assert len(hub.subscribers) == 0


async def test_queue_drops_oldest_when_full() -> None:
    hub = StatusHub()
    queue = hub.subscribe()
    for i in range(events.QUEUE_SIZE + 5):
        hub.deliver({"n": i})
    assert queue.qsize() == events.QUEUE_SIZE
    assert (await queue.get())["n"] == 5


async def test_ping(hub: StatusHub) -> None:
    stream = event_stream(hub, _never, ping_s=0.1)
    await anext(stream)
    async with asyncio.timeout(2):
        assert await anext(stream) == ": ping\n\n"
    await stream.aclose()


async def test_events_require_auth(app: FastAPI, client: httpx.AsyncClient) -> None:
    app.state.hub = StatusHub()
    resp = await client.get("/api/v1/documents/events")
    assert resp.status_code == 401
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json()["code"] == "AUTH_EXPIRED"


async def test_sse_over_http(
    app: FastAPI,
    session: AsyncSession,
    hub: StatusHub,
    publisher: async_sessionmaker[AsyncSession],
) -> None:
    """Qua một máy chủ uvicorn thật: tiêu đề đúng và khung tới máy khách (httpx ASGI không stream)."""
    app.state.hub = hub
    await users.add(session, "lan@congty.vn", Role.BD_USER, "root")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, port=port, log_level="warning", lifespan="off"))
    task = asyncio.create_task(server.serve())
    try:
        async with asyncio.timeout(5):
            while not server.started:
                await asyncio.sleep(0.02)
        cookie = issue_cookie("lan@congty.vn", get_settings(), datetime.now(UTC))
        doc_id = uuid4()
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}") as client:
            client.cookies.set(SESSION_COOKIE, cookie)
            async with client.stream("GET", "/api/v1/documents/events") as resp:
                assert resp.status_code == 200
                assert resp.headers["content-type"].startswith("text/event-stream")
                assert resp.headers["cache-control"] == "no-cache"
                assert resp.headers["x-accel-buffering"] == "no"
                lines = resp.aiter_lines()
                async with asyncio.timeout(3):
                    assert await anext(lines) == ": connected"
                async with publisher() as s:
                    await publish_status(s, doc_id, DocumentStatus.FAILED, reason=None)
                    await s.commit()
                async with asyncio.timeout(3):
                    line = await anext(lines)
                    while line == "":  # bỏ dòng trống phân tách khung
                        line = await anext(lines)
                    assert line == "event: status"
                    data = json.loads((await anext(lines)).removeprefix("data: "))
                assert data["docId"] == str(doc_id) and data["status"] == "FAILED"
        for _ in range(20):
            if not hub.subscribers:
                break
            await asyncio.sleep(0.1)
        assert hub.subscribers == set()
    finally:
        server.should_exit = True
        await task
