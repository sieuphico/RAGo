"""Dependency dùng chung cho router."""

from collections.abc import Awaitable, Callable
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.core.errors import AppError, ErrorCode
from app.core.wiring import build_gateway, build_idp, build_storage
from app.domain import CurrentUser, Role
from app.modules.answer.service import AnswerService
from app.modules.auth.cookies import SESSION_COOKIE, SessionData, read_cookie
from app.modules.users import repository as users
from app.ports.idp import IdpPort
from app.ports.storage import StoragePort


@lru_cache
def get_idp() -> IdpPort:
    return build_idp(get_settings())


@lru_cache
def get_storage() -> StoragePort:
    return build_storage(get_settings())


def session_data(request: Request) -> SessionData:
    data = read_cookie(request.cookies.get(SESSION_COOKIE, ""), get_settings())
    if data is None:
        raise AppError(ErrorCode.AUTH_EXPIRED)
    return data


SessionDep = Annotated[AsyncSession, Depends(get_session)]
IdpDep = Annotated[IdpPort, Depends(get_idp)]
StorageDep = Annotated[StoragePort, Depends(get_storage)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
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


@lru_cache
def get_answer_service() -> AnswerService:
    settings = get_settings()
    return AnswerService(db.get_session_factory(), build_gateway(settings), settings)


AnswerServiceDep = Annotated[AnswerService, Depends(get_answer_service)]
