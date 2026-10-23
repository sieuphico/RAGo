from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, GatewayDep, SessionDataDep, SessionDep, require_roles
from app.core.features import require_feature
from app.domain import Role
from app.modules.summary.service import SummaryOut, summarize

router = APIRouter(
    prefix="/api/v1",
    dependencies=[
        Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
        Depends(require_feature("summary")),
    ],
)


@router.post("/documents/{doc_id}/summary", response_model=SummaryOut)
async def summary_api(
    doc_id: UUID,
    user: CurrentUserDep,
    data: SessionDataDep,
    session: SessionDep,
    gateway: GatewayDep,
) -> SummaryOut:
    return await summarize(session, gateway, doc_id, user, data.sid)
