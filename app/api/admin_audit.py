from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import SessionDep, require_roles
from app.core.config import get_settings
from app.core.schemas import ApiModel, UtcDatetime
from app.domain import Role
from app.modules.audit import repository as audit

router = APIRouter(prefix="/api/v1/admin", dependencies=[Depends(require_roles(Role.ADMIN))])


class AuditOut(ApiModel):
    actor: str
    action: Literal["UPLOAD", "DELETE", "PURGE"]
    doc_id: UUID | None
    doc_name: str | None
    at: UtcDatetime


class AuditListOut(ApiModel):
    items: list[AuditOut]


@router.get("/audit-log", response_model=AuditListOut)
async def audit_log(
    session: SessionDep,
    since: datetime | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> AuditListOut:
    start = since or datetime.now(UTC) - timedelta(days=get_settings().audit_days)
    rows = await audit.list_since(session, start, limit)
    return AuditListOut(items=[AuditOut.model_validate(r) for r in rows])
