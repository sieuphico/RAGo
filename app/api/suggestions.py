"""API-17: gợi ý câu hỏi mẫu, tối đa 3 câu chọn ngẫu nhiên từ các tài liệu READY (US-031)."""

import random
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import SessionDep, require_roles
from app.core.features import require_feature
from app.core.schemas import ApiModel
from app.domain import DocumentStatus, Role
from app.models.document import Document, Suggestion

router = APIRouter(
    prefix="/api/v1",
    dependencies=[
        Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
        Depends(require_feature("suggestions")),
    ],
)


class SuggestionOut(ApiModel):
    doc_id: UUID
    text: str


class SuggestionListOut(ApiModel):
    items: list[SuggestionOut]


@router.get("/suggestions", response_model=SuggestionListOut)
async def suggestions_api(session: SessionDep) -> SuggestionListOut:
    rows = await session.execute(
        select(Suggestion.doc_id, Suggestion.questions)
        .join(Document, Document.doc_id == Suggestion.doc_id)
        .where(Document.status == DocumentStatus.READY, Document.deleted_at.is_(None))
    )
    pool = [SuggestionOut(doc_id=doc_id, text=q) for doc_id, questions in rows for q in questions]
    return SuggestionListOut(items=random.sample(pool, k=min(3, len(pool))))
