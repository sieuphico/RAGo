"""API-07/08/09: phiên hội thoại, gửi câu hỏi (SSE), dừng câu trả lời."""

import asyncio
import json
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import Field

from app.api.deps import (
    AnswerServiceDep,
    CurrentUserDep,
    SessionDataDep,
    SessionDep,
    SettingsDep,
    require_roles,
)
from app.core.errors import AppError, ErrorCode
from app.core.schemas import ApiModel, UtcDatetime
from app.domain import (
    AnswerEvent,
    CitationEvent,
    DoneEvent,
    ErrorEvent,
    MessageStatus,
    Role,
    StatusEvent,
    TokenEvent,
)
from app.modules.chat import repository as chat

router = APIRouter(
    prefix="/api/v1/chat",
    dependencies=[Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN))],
)

PING_S = 10.0
_RUNNING = {MessageStatus.SEARCHING, MessageStatus.STREAMING}


class SessionCreatedOut(ApiModel):
    session_id: UUID
    title: str | None
    created_at: UtcDatetime


class AskIn(ApiModel):
    text: str
    scope_doc_ids: Annotated[list[UUID], Field(max_length=50)] = Field(default_factory=list)


class StopOut(ApiModel):
    message_id: UUID
    status: MessageStatus


def to_sse_frame(event: AnswerEvent) -> bytes:
    """Khung SSE đúng CONTRACTS mục 5.2 (khóa camelCase, JSON một dòng)."""
    name: str
    data: dict[str, Any]
    match event:
        case StatusEvent():
            name = "status"
            data = {
                "stage": event.stage,
                "docCount": event.doc_count,
                "messageId": str(event.message_id),
                "scopeRemoved": [str(d) for d in event.scope_removed],
            }
        case CitationEvent():
            c = event.citation
            name = "citation"
            data = {
                "index": c.index,
                "docId": str(c.doc_id),
                "docName": c.doc_name,
                "page": c.page,
                "snippet": c.snippet,
            }
        case TokenEvent():
            name, data = "token", {"text": event.text}
        case DoneEvent():
            name = "done"
            data = {
                "messageId": str(event.message_id),
                "citationCount": event.citation_count,
                "isNotFound": event.is_not_found,
                "notFoundReason": event.not_found_reason,
                "notice": event.notice,
                "stopped": event.stopped,
            }
        case ErrorEvent():
            name, data = "error", {"code": event.code, "retryable": event.retryable}
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {name}\ndata: {body}\n\n".encode()


async def _frames(events: AsyncGenerator[AnswerEvent], ping_s: float) -> AsyncIterator[bytes]:
    """Đổi sự kiện thành khung SSE; chèn `: ping` khi im lặng quá `ping_s` mà không hủy trình sinh."""
    pending: asyncio.Future[AnswerEvent] | None = None
    try:
        while True:
            if pending is None:
                pending = asyncio.ensure_future(anext(events))
            done, _ = await asyncio.wait({pending}, timeout=ping_s)
            if not done:
                yield b": ping\n\n"
                continue
            try:
                event = pending.result()
            except StopAsyncIteration:
                return
            pending = None
            yield to_sse_frame(event)
    finally:
        if pending is not None and not pending.done():
            pending.cancel()
        await events.aclose()


@router.post("/sessions", status_code=201, response_model=SessionCreatedOut)
async def create_session_api(user: CurrentUserDep, session: SessionDep) -> SessionCreatedOut:
    chat_session = await chat.create_session(session, user.email)
    await session.commit()
    return SessionCreatedOut(
        session_id=chat_session.session_id,
        title=chat_session.title,
        created_at=chat_session.created_at,
    )


@router.post("/sessions/{session_id}/messages")
async def ask_api(
    session_id: UUID,
    body: AskIn,
    request: Request,
    user: CurrentUserDep,
    data: SessionDataDep,
    session: SessionDep,
    settings: SettingsDep,
    service: AnswerServiceDep,
) -> StreamingResponse:
    # Mọi lỗi dưới đây trả JSON trước khi mở luồng
    question = body.text.strip()
    if not question:
        raise AppError(ErrorCode.QUESTION_EMPTY)
    if len(question) > settings.max_question_chars:
        raise AppError(ErrorCode.QUESTION_TOO_LONG)
    if await chat.get_session(session, user.email, session_id) is None:
        raise AppError(ErrorCode.SESSION_NOT_FOUND)
    message_id = await service.begin(user, session_id, question)  # 409 nếu đang có câu chạy
    events = service.ask(
        user, data.sid, session_id, question, set(body.scope_doc_ids), message_id=message_id
    )
    return StreamingResponse(
        _frames(events, PING_S),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/messages/{message_id}/stop", response_model=StopOut)
async def stop_api(
    message_id: UUID, user: CurrentUserDep, session: SessionDep, service: AnswerServiceDep
) -> StopOut:
    message = await chat.get_message_for_user(session, user.email, message_id)
    if message is None:
        raise AppError(ErrorCode.NOT_FOUND)
    if service.running.stop(message_id):
        for _ in range(20):  # chờ tối đa ~1 giây để trạng thái chuyển sang STOPPED
            await asyncio.sleep(0.05)
            await session.rollback()  # đọc lại dữ liệu mới
            message = await chat.get_message_for_user(session, user.email, message_id)
            if message is None or message.status not in _RUNNING:
                break
    assert message is not None
    return StopOut(message_id=message_id, status=message.status)
