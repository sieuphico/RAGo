"""Dependency dùng chung cho router."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_session
from app.core.errors import AppError, ErrorCode
from app.core.wiring import build_idp
from app.modules.auth.cookies import SESSION_COOKIE, SessionData, read_cookie
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
