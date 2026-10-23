import asyncio
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import (
    AnswerEvent,
    DoneEvent,
    ErrorEvent,
    MessageStatus,
    StatusEvent,
    TokenEvent,
)
from app.modules.answer.service import AnswerService
from app.modules.chat import repository as chat
from app.ports.ai import ProviderError
from tests.integration.test_answer_service import USER, Provider, _ready_doc, _service


class SlowProvider(Provider):
    def __init__(self, token_delay: float = 0.0, first_delay: float = 0.0, fail: bool = False) -> None:
        super().__init__("Theo tài liệu [c1].")
        self.token_delay, self.first_delay, self.fail = token_delay, first_delay, fail

    async def generate(self, system: str, user: str) -> AsyncIterator[str]:
        self.generate_calls += 1
        if self.fail:
            raise ProviderError("down")
        await asyncio.sleep(self.first_delay)
        for word in self.answer.split(" "):
            await asyncio.sleep(self.token_delay)
            yield word + " "


async def _start(
    service: AnswerService, session: AsyncSession
) -> tuple[Any, Any]:
    chat_session = await chat.create_session(session, USER.email)
    await session.commit()
    stream = service.ask(USER, "sid", chat_session.session_id, "Thời hạn bao lâu?", set())
    status = await anext(stream)
    assert isinstance(status, StatusEvent)
    return stream, status.message_id


async def _stored(session: AsyncSession, message_id: Any) -> Any:
    session.expire_all()
    message = await chat.get_message_for_user(session, USER.email, message_id)
    assert message is not None
    return message


async def _collect(stream: Any, timeout: float = 5) -> list[AnswerEvent]:
    async with asyncio.timeout(timeout):
        return [e async for e in stream]


async def test_stop_keeps_partial(session: AsyncSession) -> None:
    await _ready_doc(session)
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, SlowProvider(token_delay=0.3), emitted=emitted)
    stream, mid = await _start(service, session)
    seen: list[AnswerEvent] = []
    started = time.monotonic()
    async with asyncio.timeout(5):
        async for event in stream:
            seen.append(event)
            if sum(isinstance(e, TokenEvent) for e in seen) == 2 and service.running.stop(mid):
                stopped_at = time.monotonic()
    done = seen[-1]
    assert isinstance(done, DoneEvent) and done.stopped is True
    assert time.monotonic() - stopped_at <= 1 and time.monotonic() - started < 5
    message = await _stored(session, mid)
    assert message.status == MessageStatus.STOPPED and message.text == "Theo tài "
    assert "answer_stopped" in [name for name, _ in emitted]
    assert mid not in service.running


async def test_stop_while_ai_silent(session: AsyncSession) -> None:
    await _ready_doc(session)
    service = _service(session, SlowProvider(first_delay=5))
    stream, mid = await _start(service, session)
    asyncio.get_running_loop().call_later(0.2, service.running.stop, mid)
    started = time.monotonic()
    events = await _collect(stream)
    assert time.monotonic() - started <= 1
    assert isinstance(events[-1], DoneEvent) and events[-1].stopped
    assert (await _stored(session, mid)).status == MessageStatus.STOPPED
    assert mid not in service.running


async def test_disconnect_marks_interrupted(session: AsyncSession) -> None:
    await _ready_doc(session)
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, SlowProvider(token_delay=0.05), emitted=emitted)
    stream, mid = await _start(service, session)
    while not isinstance(await anext(stream), TokenEvent):
        pass
    await stream.aclose()
    message = await _stored(session, mid)
    assert message.status == MessageStatus.INTERRUPTED and message.text == "Theo "
    failed = [props for name, props in emitted if name == "question_failed"]
    assert failed == [{"question_id": str(mid), "reason": "network"}]
    assert mid not in service.running


async def test_ai_error_event(session: AsyncSession) -> None:
    await _ready_doc(session)
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, SlowProvider(fail=True), emitted=emitted)
    stream, mid = await _start(service, session)
    events = await _collect(stream)
    assert events[-1] == ErrorEvent(code="AI_UNAVAILABLE", retryable=True)
    message = await _stored(session, mid)
    assert message.status == MessageStatus.FAILED and message.error_code == "AI_UNAVAILABLE"
    assert [p["reason"] for n, p in emitted if n == "question_failed"] == ["provider_error"]
    assert mid not in service.running


async def test_timeout_event(session: AsyncSession) -> None:
    await _ready_doc(session)
    emitted: list[tuple[str, dict[str, Any]]] = []
    settings = get_settings().model_copy(update={"ai_timeout_s": 1})
    service = _service(session, SlowProvider(first_delay=2), settings, emitted)
    stream, mid = await _start(service, session)
    events = await _collect(stream)
    assert events[-1] == ErrorEvent(code="TIMEOUT", retryable=True)
    assert [p["reason"] for n, p in emitted if n == "question_failed"] == ["timeout"]
    assert (await _stored(session, mid)).error_code == "TIMEOUT"
    assert mid not in service.running


async def test_budget_event(session: AsyncSession) -> None:
    await _ready_doc(session)
    month = datetime.now(UTC).date().replace(day=1)
    await session.execute(
        text("INSERT INTO ai_usage (month, cost_usd) VALUES (:m, 999)"), {"m": month}
    )
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, SlowProvider(), emitted=emitted)
    stream, mid = await _start(service, session)
    events = await _collect(stream)
    assert events[-1] == ErrorEvent(code="BUDGET_EXCEEDED", retryable=False)
    assert [p["reason"] for n, p in emitted if n == "question_failed"] == ["budget"]
    assert mid not in service.running


async def test_unexpected_error_is_internal(session: AsyncSession, caplog: Any) -> None:
    await _ready_doc(session)

    class Broken(SlowProvider):
        async def embed(self, texts: list[str]) -> list[list[float]]:
            raise RuntimeError("chi tiết nhạy cảm")

    service = _service(session, Broken())
    stream, mid = await _start(service, session)
    events = await _collect(stream)
    assert events[-1] == ErrorEvent(code="INTERNAL", retryable=False)
    assert "nhạy cảm" not in caplog.text
    assert (await _stored(session, mid)).status == MessageStatus.FAILED
