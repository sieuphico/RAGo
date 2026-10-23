from fastapi import APIRouter

from app.api.deps import SessionDataDep, SessionDep
from app.core.schemas import ApiModel
from app.domain import Role
from app.modules.users import repository as users

router = APIRouter(prefix="/api/v1")


class MeOut(ApiModel):
    email: str
    role: Role | None
    allowed: bool


@router.get("/me", response_model=MeOut)
async def me(data: SessionDataDep, session: SessionDep) -> MeOut:
    entry = await users.get_by_email(session, data.email)
    if entry is None:
        return MeOut(email=data.email, role=None, allowed=False)
    return MeOut(email=entry.email, role=entry.role, allowed=True)
