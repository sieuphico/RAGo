from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict

from app.api.deps import CurrentUserDep, SessionDep, require_roles
from app.core.schemas import ApiModel, UtcDatetime
from app.domain import Role
from app.modules.users import repository as users
from app.modules.users.service import USER_LIMIT, add_user, remove_user

router = APIRouter(prefix="/api/v1/admin", dependencies=[Depends(require_roles(Role.ADMIN))])


class UserOut(ApiModel):
    email: str
    role: Role
    added_by: str
    added_at: UtcDatetime


class UserListOut(ApiModel):
    items: list[UserOut]
    count: int
    limit: int


class AddUserIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    role: Role


@router.get("/users", response_model=UserListOut)
async def list_users_api(session: SessionDep) -> UserListOut:
    entries = await users.list_all(session)
    return UserListOut(
        items=[UserOut.model_validate(e) for e in entries], count=len(entries), limit=USER_LIMIT
    )


@router.post("/users", status_code=201, response_model=UserOut)
async def add_user_api(body: AddUserIn, actor: CurrentUserDep, session: SessionDep) -> UserOut:
    entry = await add_user(session, body.email, body.role, actor)
    await session.commit()
    return UserOut.model_validate(entry)


@router.delete("/users/{email}", status_code=204)
async def remove_user_api(email: str, actor: CurrentUserDep, session: SessionDep) -> Response:
    await remove_user(session, email, actor)
    await session.commit()
    return Response(status_code=204)
