from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, SessionDep, require_roles
from app.core.schemas import ApiModel, UtcDatetime
from app.domain import DocumentStatus, FailureReason, Role
from app.modules.documents import repository as documents
from app.modules.documents.repository import DocumentSort

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN))],
)


class DocumentOut(ApiModel):
    doc_id: UUID
    name: str
    page_count: int | None
    uploaded_by: str
    uploaded_at: UtcDatetime
    size_bytes: int
    status: DocumentStatus
    failure_reason: FailureReason | None
    used_ocr: bool
    can_delete: bool


class DocumentListOut(ApiModel):
    items: list[DocumentOut]
    total: int


@router.get("/documents", response_model=DocumentListOut)
async def list_documents_api(
    user: CurrentUserDep,
    session: SessionDep,
    search: str | None = None,
    sort: DocumentSort = "uploadedAt_desc",
) -> DocumentListOut:
    rows = await documents.list_documents(session, search, sort)
    items = [
        DocumentOut(
            doc_id=d.doc_id,
            name=d.name,
            page_count=d.page_count,
            uploaded_by=d.uploaded_by,
            uploaded_at=d.uploaded_at,
            size_bytes=d.size_bytes,
            status=d.status,
            failure_reason=d.failure_reason,
            used_ocr=d.used_ocr,
            can_delete=user.role == Role.ADMIN
            or (user.role == Role.TEAM_LEAD and d.uploaded_by == user.email),
        )
        for d in rows
    ]
    return DocumentListOut(items=items, total=len(items))

