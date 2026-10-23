"""Dịch vụ trả lời: truy xuất → quyết định → prompt → AI dạng luồng → trích dẫn (US-020, US-022, US-023).

Phần dừng, đứt kết nối, lỗi và hết giờ do T-316 bổ sung.
"""

import time
from collections.abc import AsyncGenerator, AsyncIterator, Awaitable, Callable
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.ai_gateway import AiGateway
from app.core.config import Settings
from app.domain import (
    AnswerEvent,
    CitationEvent,
    CitationOut,
    CurrentUser,
    DoneEvent,
    MessageStatus,
    StatusEvent,
    TokenEvent,
)
from app.modules.answer.citations import CitationResolver
from app.modules.answer.lang import detect_lang
from app.modules.answer.prompt import build_prompt
from app.modules.answer.relevance import decide, filter_evidence
from app.modules.chat import repository as chat
from app.modules.documents import repository as documents
from app.modules.retrieval.service import retrieve
from app.modules.telemetry.service import emit as telemetry_emit

EmitFn = Callable[[CurrentUser, str, str, dict[str, Any]], Awaitable[None]]
NOT_FOUND_PREFIX = "Không tìm thấy thông tin này"


class AnswerService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        gateway: AiGateway,
        settings: Settings,
        emit: EmitFn | None = None,
    ) -> None:
        self.factory = session_factory
        self.gateway = gateway
        self.settings = settings
        self._emit_fn = emit

    async def _emit(self, user: CurrentUser, sid: str, event: str, **props: Any) -> None:
        if self._emit_fn is not None:
            await self._emit_fn(user, sid, event, props)
            return
        async with self.factory() as session:
            await telemetry_emit(session, user, sid, event, **props)
            await session.commit()

    async def _finish(
        self,
        message_id: UUID,
        text: str,
        citations: list[CitationOut],
        *,
        is_not_found: bool,
        started: float,
    ) -> int:
        latency_ms = int((time.monotonic() - started) * 1000)
        async with self.factory() as session:
            await chat.update_message(
                session,
                message_id,
                text=text,
                status=MessageStatus.NOT_FOUND if is_not_found else MessageStatus.COMPLETED,
                is_not_found=is_not_found,
                latency_ms=latency_ms,
            )
            await chat.add_citations(session, message_id, citations)
            await session.commit()
        return latency_ms

    async def ask(
        self, user: CurrentUser, sid: str, session_id: UUID, text: str, scope: set[UUID]
    ) -> AsyncGenerator[AnswerEvent]:
        started = time.monotonic()
        threshold = self.settings.relevance_threshold
        async with self.factory() as session:
            await chat.add_message(session, session_id, "user", text, MessageStatus.COMPLETED)
            assistant = await chat.add_message(
                session, session_id, "assistant", "", MessageStatus.SEARCHING
            )
            await chat.set_title_if_empty(session, session_id, text)
            message_id = assistant.message_id
            await session.commit()
            ready = await documents.ready_doc_ids(session, scope or None)

        # Trạng thái đến người dùng trước mọi lời gọi AI (NFR-001: ≤ 1 giây)
        yield StatusEvent(message_id=message_id, doc_count=len(ready))
        await self._emit(
            user, sid, "question_submitted",
            question_id=str(message_id), length_chars=len(text), language=detect_lang(text),
            is_followup=False, scope_doc_count=len(scope),
        )  # fmt: skip

        if not ready:
            async for event in self._not_found(
                user, sid, message_id, "NO_READY_DOCS", started
            ):
                yield event
            return

        async with self.factory() as session:
            chunks = await retrieve(
                session, self.gateway.embed, text, scope, k=self.settings.retrieval_k
            )
        if decide(chunks, len(ready), threshold) == "NO_EVIDENCE":
            async for event in self._not_found(user, sid, message_id, "NO_EVIDENCE", started):
                yield event
            return

        prompt = build_prompt(text, filter_evidence(chunks, threshold))
        resolver = CitationResolver(prompt.label_map)
        parts: list[str] = []
        first_token = True
        async for delta in self.gateway.generate(prompt.system, prompt.user):
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
                        question_id=str(message_id),
                        latency_ms=int((time.monotonic() - started) * 1000),
                    )  # fmt: skip
                parts.append(visible)
                yield TokenEvent(text=visible)
        tail, fresh = resolver.finish()
        parts.append(tail)

        full_text = "".join(parts)
        citations = resolver.citations
        is_not_found = full_text.strip().startswith(NOT_FOUND_PREFIX) and not citations
        latency_ms = await self._finish(
            message_id, full_text, citations, is_not_found=is_not_found, started=started
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
        self,
        user: CurrentUser,
        sid: str,
        message_id: UUID,
        reason: str,
        started: float,
    ) -> AsyncIterator[AnswerEvent]:
        latency_ms = await self._finish(message_id, "", [], is_not_found=True, started=started)
        yield DoneEvent(
            message_id=message_id,
            citation_count=0,
            is_not_found=True,
            not_found_reason=reason,  # type: ignore[arg-type]
        )
        await self._emit(
            user, sid, "answer_completed",
            question_id=str(message_id), latency_ms=latency_ms, citation_count=0,
            distinct_doc_count=0, is_not_found=True,
        )  # fmt: skip
