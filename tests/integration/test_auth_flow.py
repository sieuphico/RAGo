from urllib.parse import urlsplit

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import Role
from app.modules.auth.cookies import SESSION_COOKIE, issue_cookie, read_cookie
from app.modules.users import repository as users


async def _login(client: httpx.AsyncClient, email: str, next_url: str = "/") -> httpx.Response:
    start = await client.get("/auth/login", params={"next": next_url, "login_hint": email})
    assert start.status_code == 302
    target = urlsplit(start.headers["location"])
    return await client.get(f"{target.path}?{target.query}")


async def test_login_allowed_user(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await users.add(session, "lan@congty.vn", Role.BD_USER, "root")
    assert (await _login(client, "lan@congty.vn")).status_code == 302
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 200
    assert resp.json() == {"email": "lan@congty.vn", "role": "BD_USER", "allowed": True}


async def test_login_not_in_allowlist(client: httpx.AsyncClient) -> None:
    await _login(client, "x@congty.vn")
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 200
    assert resp.json() == {"email": "x@congty.vn", "role": None, "allowed": False}


async def test_me_without_cookie_401(client: httpx.AsyncClient) -> None:
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 401
    assert resp.json() == {"code": "AUTH_EXPIRED", "retryable": False}


async def test_cookie_flags(client: httpx.AsyncClient) -> None:
    resp = await _login(client, "lan@congty.vn")
    cookie = next(h for h in resp.headers.get_list("set-cookie") if h.startswith(SESSION_COOKIE))
    for flag in ("HttpOnly", "Secure", "SameSite=lax", "Path=/", "Max-Age=28800"):
        assert flag.lower() in cookie.lower(), flag


async def test_state_mismatch(client: httpx.AsyncClient) -> None:
    await client.get("/auth/login")
    resp = await client.get("/auth/callback", params={"state": "khac", "email": "a@x.vn"})
    assert resp.status_code == 400
    assert resp.json() == {"code": "VALIDATION_ERROR", "retryable": False}
    assert SESSION_COOKIE not in resp.headers.get("set-cookie", "")


async def test_open_redirect_blocked(client: httpx.AsyncClient) -> None:
    resp = await _login(client, "lan@congty.vn", next_url="//evil.com")
    assert resp.status_code == 302
    assert resp.headers["location"] == "/"


async def test_next_path_kept(client: httpx.AsyncClient) -> None:
    resp = await _login(client, "lan@congty.vn", next_url="/documents")
    assert resp.headers["location"] == "/documents"


async def test_tampered_cookie(client: httpx.AsyncClient) -> None:
    await _login(client, "lan@congty.vn")
    value = client.cookies[SESSION_COOKIE]
    flipped = ("A" if value[5] != "A" else "B").join([value[:5], value[6:]])
    client.cookies.set(SESSION_COOKIE, flipped)
    assert (await client.get("/api/v1/me")).status_code == 401


async def test_expired_cookie_rejected() -> None:
    from datetime import UTC, datetime, timedelta

    settings = get_settings()
    now = datetime(2026, 11, 2, tzinfo=UTC)
    value = issue_cookie("a@x.vn", settings, now)
    assert read_cookie(value, settings, now + timedelta(seconds=settings.session_ttl_s - 1))
    assert read_cookie(value, settings, now + timedelta(seconds=settings.session_ttl_s + 1)) is None


async def test_first_login_flag(client: httpx.AsyncClient, session: AsyncSession) -> None:
    from app.adapters.idp_fake import IdpFake
    from app.modules.auth.service import complete_login

    await users.add(session, "lan@congty.vn", Role.BD_USER, "root")
    idp = IdpFake("x@x.vn")
    _, first = await complete_login(session, idp, {"email": "lan@congty.vn"})
    _, second = await complete_login(session, idp, {"email": "lan@congty.vn"})
    assert (first, second) == (True, False)
    _, outside = await complete_login(session, idp, {"email": "nobody@x.vn"})
    assert outside is False


async def test_logout_clears_cookie(client: httpx.AsyncClient) -> None:
    await _login(client, "lan@congty.vn")
    resp = await client.post("/auth/logout")
    assert resp.status_code == 204
    assert SESSION_COOKIE in resp.headers["set-cookie"]
