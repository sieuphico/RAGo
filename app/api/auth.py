import secrets

from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from app.api.deps import IdpDep, SessionDep
from app.core.config import get_settings
from app.core.errors import AppError, ErrorCode
from app.modules.auth.cookies import (
    SESSION_COOKIE,
    STATE_COOKIE,
    STATE_TTL_S,
    issue_state_cookie,
    read_state_cookie,
    safe_next,
)
from app.modules.auth.service import complete_login, record_login

router = APIRouter(prefix="/auth")


def _set_cookie(response: Response, key: str, value: str, max_age: int) -> None:
    response.set_cookie(
        key, value, max_age=max_age, httponly=True, secure=True, samesite="lax", path="/"
    )


@router.get("/login")
async def login(
    request: Request,
    idp: IdpDep,
    next: str | None = None,
    login_hint: str | None = None,
) -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    redirect_uri = str(request.url_for("callback"))
    response = RedirectResponse(idp.login_url(redirect_uri, state, login_hint), status_code=302)
    cookie = issue_state_cookie(state, safe_next(next), get_settings())
    _set_cookie(response, STATE_COOKIE, cookie, STATE_TTL_S)
    return response


@router.get("/callback", name="callback")
async def callback(
    request: Request,
    session: SessionDep,
    idp: IdpDep,
) -> RedirectResponse:
    saved = read_state_cookie(request.cookies.get(STATE_COOKIE, ""), get_settings())
    params = dict(request.query_params)
    if saved is None or not secrets.compare_digest(saved[0], params.get("state", "")):
        raise AppError(ErrorCode.VALIDATION_ERROR, http_status=400)
    try:
        cookie, first = await complete_login(session, idp, params)
        await record_login(session, cookie, first)
    except Exception as exc:  # lỗi từ IdP: không lộ chi tiết (DD-06)
        raise AppError(ErrorCode.VALIDATION_ERROR, http_status=400) from exc
    await session.commit()
    response = RedirectResponse(saved[1], status_code=302)
    _set_cookie(response, SESSION_COOKIE, cookie, get_settings().session_ttl_s)
    response.delete_cookie(STATE_COOKIE, path="/")
    return response


@router.post("/logout", status_code=204)
async def logout() -> Response:
    response = Response(status_code=204)
    response.delete_cookie(SESSION_COOKIE, path="/")
    return response
