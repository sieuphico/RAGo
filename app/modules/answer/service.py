"""Dịch vụ trả lời: truy xuất → quyết định → prompt → AI dạng luồng → trích dẫn (US-020, US-022, US-023, US-027).

Xử lý cả dừng theo yêu cầu, client đứt kết nối, lỗi AI và hết giờ (T-316).
"""

import asyncio
import contextlib
import logging
import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.domain import (
    AnswerEvent,
    CitationEvent,
    CitationOut,
    CurrentUser,
    DoneEvent,
    ErrorEvent,
    MessageStatus,
    StatusEvent,
    TokenEvent,
)
from app.modules.answer.citations import CitationResolver
from app.modules.answer.lang import detect_lang
from app.modules.answer.prompt import build_prompt
from app.modules.answer.relevance import decide, filter_evidence
from app.modules.answer.running import RUNNING, RunningAnswers
from app.modules.chat import repository as chat
from app.modules.documents import repository as documents
from app.modules.retrieval.service import retrieve
from app.modules.telemetry.service import emit as telemetry_emit
from app.ports.ai import AiPort

logger = logging.getLogger("app.answer")
EmitFn = Callable[[CurrentUser, str, str, dict[str, Any]], Awaitable[None]]
NOT_FOUND_PREFIX = "Không tìm thấy thông tin này"
_FAIL_REASON = {
    ErrorCode.TIMEOUT: "timeout",
    ErrorCode.AI_UNAVAILABLE: "provider_error",
    ErrorCode.BUDGET_EXCEEDED: "budget",
}


@dataclass
class _Progress:
    """Trạng thái đang soạn, để lưu phần đã có khi bị dừng, đứt kết nối hay lỗi."""

    message_id: UUID
    started: float
    parts: list[str] = field(default_factory=list)
    resolver: CitationResolver | None = None
    stopped: bool = False

    @property
    def text(self) -> str:
        return "".join(self.parts)

    @property
    def citations(self) -> list[CitationOut]:
        return self.resolver.citations if self.resolver else []

    def elapsed_ms(self) -> int:
        return int((time.monotonic() - self.started) * 1000)


class AnswerService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        gateway: AiPort,
        settings: Settings,
        emit: EmitFn | None = None,
        running: RunningAnswers | None = None,
    ) -> None:
        self.factory = session_factory
        self.gateway = gateway
        self.settings = settings
        self._emit_fn = emit
        self.running = running if running is not None else RUNNING

    # ---- tiện ích
    async def _emit(self, user: CurrentUser, sid: str, event: str, **props: Any) -> None:
        if self._emit_fn is not None:
            await self._emit_fn(user, sid, event, props)
            return
        async with self.factory() as session:
            await telemetry_emit(session, user, sid, event, **props)
            await session.commit()

    async def _save(
        self,
        progress: _Progress,
        status: MessageStatus,
        *,
        is_not_found: bool = False,
        error_code: str | None = None,
        text: str | None = None,
    ) -> int:
        latency_ms = progress.elapsed_ms()
        async with self.factory() as session:
            await chat.update_message(
                session,
                progress.message_id,
                text=progress.text if text is None else text,
                status=status,
                is_not_found=is_not_found,
                latency_ms=latency_ms,
                error_code=error_code,
            )
            await chat.add_citations(session, progress.message_id, progress.citations)
            await session.commit()
        return latency_ms

    async def _save_interrupted(self, user: CurrentUser, sid: str, progress: _Progress) -> None:
        await self._save(progress, MessageStatus.INTERRUPTED)
        await self._emit(
            user, sid, "question_failed",
            question_id=str(progress.message_id), reason="network",
        )  # fmt: skip

    # ---- luồng chính
    async def ask(
        self, user: CurrentUser, sid: str, session_id: UUID, text: str, scope: set[UUID]
    ) -> AsyncGenerator[AnswerEvent]:
        started = time.monotonic()
        async with self.factory() as session:
            await chat.add_message(session, session_id, "user", text, MessageStatus.COMPLETED)
            assistant = await chat.add_message(
                session, session_id, "assistant", "", MessageStatus.SEARCHING
            )
            await chat.set_title_if_empty(session, session_id, text)
            await session.commit()
            message_id = assistant.message_id
            ready = await documents.ready_doc_ids(session, scope or None)

        progress = _Progress(message_id, started)
        stop = self.running.start(message_id)
        inner = self._answer(user, sid, text, scope, ready, progress, stop)
        try:
            # Trạng thái đến người dùng trước mọi lời gọi AI (NFR-001: ≤ 1 giây)
            yield StatusEvent(message_id=message_id, doc_count=len(ready))
            async for event in inner:
                yield event
        except (GeneratorExit, asyncio.CancelledError):
            # Client đóng kết nối: lưu phần đã có, không để việc ghi bị hủy theo
            await asyncio.shield(self._save_interrupted(user, sid, progress))
            raise
        except AppError as exc:
            reason = _FAIL_REASON.get(exc.code, "provider_error")
            await self._save(progress, MessageStatus.FAILED, error_code=exc.code.value)
            yield ErrorEvent(code=exc.code.value, retryable=exc.retryable)
            await self._emit(
                user, sid, "question_failed", question_id=str(message_id), reason=reason
            )
        except Exception as exc:  # noqa: BLE001 - mọi lỗi lạ đều phải kết thúc luồng gọn gàng
            request_id = uuid.uuid4().hex
            logger.error("answer failed %s request_id=%s", type(exc).__name__, request_id)
            await self._save(progress, MessageStatus.FAILED, error_code=ErrorCode.INTERNAL.value)
            yield ErrorEvent(code=ErrorCode.INTERNAL.value, retryable=False)
            await self._emit(
                user, sid, "question_failed", question_id=str(message_id), reason="provider_error"
            )
        finally:
            await inner.aclose()
            self.running.finish(message_id)

    async def _answer(
        self,
        user: CurrentUser,
        sid: str,
        text: str,
        scope: set[UUID],
        ready: set[UUID],
        progress: _Progress,
        stop: asyncio.Event,
    ) -> AsyncGenerator[AnswerEvent]:
        message_id = progress.message_id
        threshold = self.settings.relevance_threshold
        await self._emit(
            user, sid, "question_submitted",
            question_id=str(message_id), length_chars=len(text), language=detect_lang(text),
            is_followup=False, scope_doc_count=len(scope),
        )  # fmt: skip

        if not ready:
            async for event in self._not_found(user, sid, progress, "NO_READY_DOCS"):
                yield event
            return

        async with self.factory() as session:
            chunks = await retrieve(
                session, self.gateway.embed, text, scope, k=self.settings.retrieval_k
            )
        if decide(chunks, len(ready), threshold) == "NO_EVIDENCE":
            async for event in self._not_found(user, sid, progress, "NO_EVIDENCE"):
                yield event
            return

        prompt = build_prompt(text, filter_evidence(chunks, threshold))
        progress.resolver = resolver = CitationResolver(prompt.label_map)
        stream = self.gateway.generate(prompt.system, prompt.user).__aiter__()
        first_token = True
        try:
            while True:
                next_token = asyncio.ensure_future(anext(stream))
                stopper = asyncio.ensure_future(stop.wait())
                await asyncio.wait({next_token, stopper}, return_when=asyncio.FIRST_COMPLETED)
                if stop.is_set():  # Dừng kể cả khi AI đang im lặng (≤ 1 giây)
                    next_token.cancel()
                    with contextlib.suppress(asyncio.CancelledError, StopAsyncIteration):
                        await next_token
                    progress.stopped = True
                    break
                stopper.cancel()
                try:
                    delta = next_token.result()
                except StopAsyncIteration:
                    break
                visible, fresh = resolver.feed(delta)
                for citation in fresh:  # trích dẫn đến trước văn bản chứa [[n]] (CONTRACTS 4.3)
                    yield CitationEvent(citation=citation)
                if visible:
                    if first_token:
                        first_token = False
                        async with self.factory() as session:
                            await chat.update_message(
                                session, message_id, status=MessageStatus.STREAMING
                            )
                            await session.commit()
                        await self._emit(
                            user, sid, "answer_first_token",
                            question_id=str(message_id), latency_ms=progress.elapsed_ms(),
                        )  # fmt: skip
                    progress.parts.append(visible)
                    yield TokenEvent(text=visible)
        finally:
            await stream.aclose()  # type: ignore[attr-defined]

        if progress.stopped:
            await self._save(progress, MessageStatus.STOPPED)
            yield DoneEvent(
                message_id=message_id,
                citation_count=len(progress.citations),
                is_not_found=False,
                stopped=True,
            )
            await self._emit(
                user, sid, "answer_stopped",
                question_id=str(message_id), elapsed_ms=progress.elapsed_ms(),
            )  # fmt: skip
            return

        tail, _ = resolver.finish()
        progress.parts.append(tail)
        citations = resolver.citations
        is_not_found = progress.text.strip().startswith(NOT_FOUND_PREFIX) and not citations
        latency_ms = await self._save(
            progress,
            MessageStatus.NOT_FOUND if is_not_found else MessageStatus.COMPLETED,
            is_not_found=is_not_found,
        )
        yield DoneEvent(
            message_id=message_id,
            citation_count=len(citations),
            is_not_found=is_not_found,
            not_found_reason="NO_EVIDENCE" if is_not_found else None,
        )
        await self._emit(
            user, sid, "answer_completed",
            question_id=str(message_id), latency_ms=latency_ms, citation_count=len(citations),
            distinct_doc_count=len({c.doc_id for c in citations}), is_not_found=is_not_found,
        )  # fmt: skip

    async def _not_found(
        self, user: CurrentUser, sid: str, progress: _Progress, reason: str
    ) -> AsyncGenerator[AnswerEvent]:
        latency_ms = await self._save(progress, MessageStatus.NOT_FOUND, is_not_found=True, text="")
        yield DoneEvent(
            message_id=progress.message_id,
            citation_count=0,
            is_not_found=True,
            not_found_reason=reason,  # type: ignore[arg-type]
        )
        await self._emit(
            user, sid, "answer_completed",
            question_id=str(progress.message_id), latency_ms=latency_ms, citation_count=0,
            distinct_doc_count=0, is_not_found=True,
        )  # fmt: skip
