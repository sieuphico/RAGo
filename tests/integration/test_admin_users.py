import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.cli import main
from app.domain import Role
from app.modules.users import repository as users
from tests.integration.helpers import CSRF, login

BASE = "/api/v1/admin/users"


async def test_admin_only(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(BASE)
    assert resp.status_code == 403 and resp.json()["code"] == "AUTH_FORBIDDEN"


async def test_list_users(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    body = (await client.get(BASE)).json()
    assert body["count"] == 1 and body["limit"] == 20
    assert set(body["items"][0]) == {"email", "role", "addedBy", "addedAt"}


async def test_add_user_201(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    resp = await client.post(BASE, json={"email": "Lan@CongTy.vn", "role": "BD_USER"}, headers=CSRF)
    assert resp.status_code == 201
    assert resp.json()["email"] == "lan@congty.vn" and resp.json()["addedBy"] == "quantri@congty.vn"
    await login(client, session, "lan@congty.vn", None)  # đã có trong allow-list
    me = (await client.get("/api/v1/me")).json()
    assert me == {"email": "lan@congty.vn", "role": "BD_USER", "allowed": True}


async def test_add_duplicate_rejected(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    body = {"email": "lan@congty.vn", "role": "BD_USER"}
    await client.post(BASE, json=body, headers=CSRF)
    resp = await client.post(BASE, json={**body, "email": "LAN@congty.vn"}, headers=CSRF)
    assert resp.status_code == 409 and resp.json()["code"] == "USER_EXISTS"


async def test_email_invalid(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    for bad in ("lan@", "khong-co-a-cong", "a b@x.vn", ""):
        resp = await client.post(BASE, json={"email": bad, "role": "BD_USER"}, headers=CSRF)
        assert resp.status_code == 400 and resp.json()["code"] == "EMAIL_INVALID", bad


async def test_limit_20(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    for i in range(19):
        await users.add(session, f"u{i}@congty.vn", Role.BD_USER, "root")
    resp = await client.post(BASE, json={"email": "thu21@congty.vn", "role": "BD_USER"}, headers=CSRF)
    assert resp.status_code == 409 and resp.json()["code"] == "USER_LIMIT_REACHED"


async def test_remove_user_and_blocked_next_request(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    admin = httpx.AsyncClient(transport=client._transport, base_url="https://test")
    await login(admin, session, "quantri@congty.vn", Role.ADMIN)
    assert (await admin.delete(f"{BASE}/lan@congty.vn", headers=CSRF)).status_code == 204
    assert (await client.get("/api/v1/documents")).status_code == 403  # bị chặn ngay (EC-17)
    assert (await admin.delete(f"{BASE}/lan@congty.vn", headers=CSRF)).json()["code"] == "NOT_FOUND"


async def test_last_admin(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    resp = await client.delete(f"{BASE}/quantri@congty.vn", headers=CSRF)
    assert resp.status_code == 409 and resp.json()["code"] == "LAST_ADMIN"
    await users.add(session, "hai@congty.vn", Role.ADMIN, "root")
    assert (await client.delete(f"{BASE}/quantri@congty.vn", headers=CSRF)).status_code == 204


def test_cli_add_admin(test_database_url: str, capsys: object) -> None:
    sync = create_engine(make_url(test_database_url).set(drivername="postgresql+psycopg"))
    try:
        with sync.begin() as conn:
            conn.execute(text("DELETE FROM allow_list_entry"))
        assert main(["add-admin", "QuanTri@congty.vn"]) == 0
        assert main(["add-admin", "quantri@congty.vn"]) == 0  # chạy lại không lỗi
        with sync.connect() as conn:
            rows = conn.execute(text("SELECT email, role FROM allow_list_entry")).all()
        assert [tuple(r) for r in rows] == [("quantri@congty.vn", "ADMIN")]
        assert main(["add-admin", "khong-hop-le"]) == 1
    finally:
        with sync.begin() as conn:
            conn.execute(text("DELETE FROM allow_list_entry"))
        sync.dispose()
