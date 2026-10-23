import re
import uuid

import httpx
from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserDep, require_roles
from app.domain import CurrentUser, Role
from app.modules.users import repository as users

CSRF = {"X-Requested-With": "cwd"}


def _add_test_routes(app: FastAPI) -> None:
    router = APIRouter(prefix="/api/v1/_t")

    @router.get("/bd")
    async def bd(user: CurrentUser = Depends(require_roles(Role.BD_USER))) -> dict[str, str]:  # noqa: B008
        return {"email": user.email}

    @router.get("/admin")
    async def admin(user: CurrentUser = Depends(require_roles(Role.ADMIN))) -> dict[str, str]:  # noqa: B008
        return {"email": user.email}

    @router.post("/write")
    async def write(user: CurrentUserDep) -> dict[str, str]:
        return {"email": user.email}

    app.include_router(router)


async def _login(client: httpx.AsyncClient, email: str) -> None:
    resp = await client.get("/auth/login", params={"login_hint": email})
    await client.get(resp.headers["location"].removeprefix("https://test"))


async def test_revoked_user_blocked_next_request(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    _add_test_routes(app)
    await users.add(session, "lan@congty.vn", Role.BD_USER, "root")
    await _login(client, "lan@congty.vn")
    assert (await client.get("/api/v1/_t/bd")).status_code == 200
    await users.remove(session, "lan@congty.vn")
    resp = await client.get("/api/v1/_t/bd")
    assert resp.status_code == 403
    assert resp.json() == {"code": "AUTH_FORBIDDEN", "retryable": False}


async def test_unauthenticated_all_endpoints(app: FastAPI, client: httpx.AsyncClient) -> None:
    _add_test_routes(app)
    checked = 0
    for path, methods in app.openapi()["paths"].items():
        if not path.startswith("/api/v1") or path == "/api/v1/me":
            continue
        url = re.sub(r"\{[^}]+\}", str(uuid.uuid4()), path)
        for method in methods:
            resp = await client.request(method.upper(), url, headers=CSRF)
            assert resp.status_code == 401, (method, path)
            assert resp.json()["code"] == "AUTH_EXPIRED"
            checked += 1
    assert checked >= 3


async def test_csrf_header_required(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    _add_test_routes(app)
    await users.add(session, "lan@congty.vn", Role.BD_USER, "root")
    await _login(client, "lan@congty.vn")
    resp = await client.post("/api/v1/_t/write")
    assert resp.status_code == 403
    assert resp.json() == {"code": "CSRF_REJECTED", "retryable": False}
    assert (await client.post("/api/v1/_t/write", headers=CSRF)).status_code == 200
    assert (await client.get("/api/v1/_t/bd")).status_code == 200  # GET không cần tiêu đề


async def test_csrf_not_applied_to_auth(client: httpx.AsyncClient) -> None:
    assert (await client.post("/auth/logout")).status_code == 204


async def test_wrong_role(app: FastAPI, client: httpx.AsyncClient, session: AsyncSession) -> None:
    _add_test_routes(app)
    await users.add(session, "ntt@congty.vn", Role.SPONSOR, "root")
    await _login(client, "ntt@congty.vn")
    resp = await client.get("/api/v1/_t/admin")
    assert resp.status_code == 403
    assert resp.json()["code"] == "AUTH_FORBIDDEN"
