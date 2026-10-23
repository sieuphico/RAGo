"""API-10: lịch sử hội thoại trong `history_days` ngày (US-041, BR-021)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDataDep, SessionDep, SettingsDep, require_roles
from app.core.errors import AppError, ErrorCode
from app.core.features import require_feature
from app.core.schemas import ApiModel, UtcDatetime
from app.domain import MessageStatus, Role
from app.models.document import Document
from app.modules.chat import repository as chat
from app.modules.telemetry.service import emit

router = APIRouter(
    prefix="/api/v1/chat",
    dependencies=[
        Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
        Depends(require_feature("history")),
    ],
)


class SessionSummaryOut(ApiModel):
    session_id: UUID
    title: str | None
    created_at: UtcDatetime
    last_message_at: UtcDatetime


class SessionListOut(ApiModel):
    items: list[SessionSummaryOut]


class CitationOut(ApiModel):
    index: int
    doc_id: UUID
    doc_name: str
    page: int
    snippet: str
    deleted: bool


class MessageOut(ApiModel):
    message_id: UUID
    role: str
    text: str
    status: MessageStatus
    created_at: UtcDatetime
    is_not_found: bool
    citations: list[CitationOut]
    rating: str | None


class SessionDetailOut(ApiModel):
    session_id: UUID
    title: str | None
    created_at: UtcDatetime
    scope_doc_ids: list[UUID]
    messages: list[MessageOut]


@router.get("/sessions", response_model=SessionListOut)
async def list_sessions_api(
    user: CurrentUserDep, session: SessionDep, settings: SettingsDep
) -> SessionListOut:
    since = datetime.now(UTC) - timedelta(days=settings.history_days)
    rows = await chat.list_sessions(session, user.email, since)
    return SessionListOut(items=[SessionSummaryOut.model_validate(r) for r in rows])


@router.get("/sessions/{session_id}", response_model=SessionDetailOut)
async def session_detail_api(
    session_id: UUID,
    user: CurrentUserDep,
    data: SessionDataDep,
    session: SessionDep,
) -> SessionDetailOut:
    chat_session = await chat.get_session(session, user.email, session_id)
    if chat_session is None:
        raise AppError(ErrorCode.SESSION_NOT_FOUND)
    doc_ids = {c.doc_id for m in chat_session.messages for c in m.citations}
    docs = {}
    if doc_ids:
        rows = await session.execute(select(Document).where(Document.doc_id.in_(doc_ids)))
        docs = {d.doc_id: d for d in rows.scalars()}
    messages = [
        MessageOut(
            message_id=m.message_id,
            role=m.role,
            text=m.text,
            status=m.status,
            created_at=m.created_at,
            is_not_found=m.is_not_found,
            citations=[
                CitationOut(
                    index=c.idx,
                    doc_id=c.doc_id,
                    doc_name=docs[c.doc_id].name if c.doc_id in docs else "",
                    page=c.page,
                    snippet=c.snippet,
                    deleted=c.doc_id not in docs or docs[c.doc_id].deleted_at is not None,
                )
                for c in m.citations
            ],
            rating=m.rating.value if m.rating else None,
        )
        for m in chat_session.messages
    ]
    age_days = max((datetime.now(UTC) - chat_session.created_at).days, 0)
    await emit(session, user, data.sid, "history_session_opened", session_age_days=age_days)
    await session.commit()
    return SessionDetailOut(
        session_id=chat_session.session_id,
        title=chat_session.title,
        created_at=chat_session.created_at,
        scope_doc_ids=list(chat_session.scope_doc_ids),
        messages=messages,
    )
