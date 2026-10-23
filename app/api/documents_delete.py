from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_roles
from app.core.schemas import ApiModel
from app.domain import CurrentUser, Role
from app.modules.documents.delete import delete_document

router = APIRouter(prefix="/api/v1")


class DeleteOut(ApiModel):
    doc_id: UUID
    already_deleted: bool


@router.delete("/documents/{doc_id}", response_model=DeleteOut)
async def delete_document_api(
    doc_id: UUID,
    session: SessionDep,
    actor: CurrentUser = Depends(require_roles(Role.TEAM_LEAD, Role.ADMIN)),  # noqa: B008
) -> DeleteOut:
    already = await delete_document(session, doc_id, actor, datetime.now(UTC))
    await session.commit()
    return DeleteOut(doc_id=doc_id, already_deleted=already)
