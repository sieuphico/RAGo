"""Dependency dùng chung cho router."""

from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.errors import AppError, ErrorCode
from app.core.wiring import build_idp
from app.domain import CurrentUser, Role
from app.modules.auth.cookies import SESSION_COOKIE, SessionData, read_cookie
from app.modules.users import repository as users
from app.ports.idp import IdpPort


@lru_cache
def get_idp() -> IdpPort:
    return build_idp(get_settings())


def session_data(request: Request) -> SessionData:
    data = read_cookie(request.cookies.get(SESSION_COOKIE, ""), get_settings())
    if data is None:
        raise AppError(ErrorCode.AUTH_EXPIRED)
    return data


SessionDep = Annotated[AsyncSession, Depends(get_session)]
IdpDep = Annotated[IdpPort, Depends(get_idp)]
SessionDataDep = Annotated[SessionData, Depends(session_data)]


async def current_user(data: SessionDataDep, session: SessionDep) -> CurrentUser:
    """Tra allow-list mỗi yêu cầu, không bộ nhớ đệm: thu hồi quyền có hiệu lực ngay (EC-17)."""
    entry = await users.get_by_email(session, data.email)
    if entry is None:
        raise AppError(ErrorCode.AUTH_FORBIDDEN)
    return CurrentUser(email=entry.email, role=entry.role)


CurrentUserDep = Annotated[CurrentUser, Depends(current_user)]


def require_roles(*roles: Role) -> Callable[..., Awaitable[CurrentUser]]:
    async def dependency(user: CurrentUserDep) -> CurrentUser:
        if user.role not in roles:
            raise AppError(ErrorCode.AUTH_FORBIDDEN)
        return user

    return dependency
