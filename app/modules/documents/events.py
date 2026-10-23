"""Thông báo trạng thái tài liệu: worker `NOTIFY doc_status`, tiến trình API `LISTEN` rồi đẩy tới SSE."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any
from uuid import UUID

import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import DocumentStatus, FailureReason

logger = logging.getLogger("app.documents.events")
CHANNEL = "doc_status"
QUEUE_SIZE = 100
PING_S = 15.0


async def publish_status(
    session: AsyncSession,
    doc_id: UUID,
    status: DocumentStatus,
    reason: FailureReason | None = None,
    page_count: int | None = None,
) -> None:
    """Gửi trong cùng giao dịch với việc đổi trạng thái: thông báo chỉ đi khi `commit`."""
    payload = json.dumps(
        {
            "docId": str(doc_id),
            "status": status.value,
            "failureReason": reason.value if reason else None,
            "pageCount": page_count,
        }
    )
    await session.execute(text("SELECT pg_notify(:channel, :payload)"),
                          {"channel": CHANNEL, "payload": payload})  # fmt: skip


class StatusHub:
    def __init__(self) -> None:
        self.subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._conn: asyncpg.Connection | None = None

    async def start(self, dsn: str) -> None:
        # asyncpg không nhận hậu tố "+asyncpg" của SQLAlchemy
        self._conn = await asyncpg.connect(dsn.replace("+asyncpg", ""))
        await self._conn.add_listener(CHANNEL, self._on_notify)

    async def stop(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    def _on_notify(self, _conn: object, _pid: int, _channel: str, payload: str) -> None:
        try:
            event = json.loads(payload)
        except ValueError:
            logger.error("bad doc_status payload")
            return
        self.deliver(event)

    def deliver(self, event: dict[str, Any]) -> None:
        for queue in list(self.subscribers):
            if queue.full():
                queue.get_nowait()  # bỏ thông báo cũ nhất
            queue.put_nowait(event)

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=QUEUE_SIZE)
        self.subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self.subscribers.discard(queue)


def frame(event: dict[str, Any]) -> str:
    return f"event: status\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"


async def event_stream(
    hub: StatusHub,
    is_disconnected: Callable[[], Awaitable[bool]],
    ping_s: float | None = None,
) -> AsyncGenerator[str]:
    """Khung SSE đúng CONTRACTS mục 5.1; gỡ hàng đợi khi client ngắt."""
    ping = PING_S if ping_s is None else ping_s
    queue = hub.subscribe()
    try:
        yield ": connected\n\n"
        waited = 0.0
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=min(ping, 0.5))
            except TimeoutError:
                if await is_disconnected():
                    return
                waited += min(ping, 0.5)
                if waited >= ping:
                    waited = 0.0
                    yield ": ping\n\n"
                continue
            waited = 0.0
            yield frame(event)
    finally:
        hub.unsubscribe(queue)
