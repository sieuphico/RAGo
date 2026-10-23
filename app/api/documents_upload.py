from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile

from app.api.deps import SessionDataDep, SessionDep, SettingsDep, StorageDep, require_roles
from app.core.errors import AppError, ErrorCode
from app.core.schemas import ApiModel
from app.domain import CurrentUser, DocumentStatus, Role
from app.modules.documents.upload import upload_documents

router = APIRouter(prefix="/api/v1")


class UploadResultOut(ApiModel):
    name: str
    doc_id: UUID | None
    status: DocumentStatus | None
    error: str | None


class UploadOut(ApiModel):
    results: list[UploadResultOut]


@router.post("/documents", status_code=202, response_model=UploadOut)
async def upload(
    session: SessionDep,
    storage: StorageDep,
    settings: SettingsDep,
    data: SessionDataDep,
    actor: CurrentUser = Depends(require_roles(Role.TEAM_LEAD)),  # noqa: B008
    files: list[UploadFile] | None = None,
) -> UploadOut:
    if not files:
        raise AppError(ErrorCode.FILE_TOO_MANY)
    results = await upload_documents(session, storage, files, actor, settings, data.sid)
    return UploadOut(results=[UploadResultOut.model_validate(r) for r in results])
