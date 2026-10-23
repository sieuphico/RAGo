from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Role
from app.modules.audit import service as audit
from app.modules.users import repository as users

NOW = datetime(2026, 12, 1, 3, tzinfo=UTC)


async def _login(client: httpx.AsyncClient, email: str) -> None:
    resp = await client.get("/auth/login", params={"login_hint": email})
    await client.get(resp.headers["location"].removeprefix("https://test"))


async def test_four_records_after_ops(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await users.add(session, "admin@congty.vn", Role.ADMIN, "root")
    for i in range(3):
        await audit.record(session, "minh@congty.vn", "UPLOAD", None, f"HD_{i}.pdf")
    await audit.record(session, "minh@congty.vn", "DELETE", None, "HD_0.pdf")
    await _login(client, "admin@congty.vn")
    resp = await client.get("/api/v1/admin/audit-log")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 4
    assert all(set(i) == {"actor", "action", "docId", "docName", "at"} for i in items)
    assert items[0]["action"] == "DELETE"  # mới nhất trước
    assert items[0]["at"].endswith("Z")


async def test_audit_admin_only(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await users.add(session, "minh@congty.vn", Role.TEAM_LEAD, "root")
    await _login(client, "minh@congty.vn")
    resp = await client.get("/api/v1/admin/audit-log")
    assert resp.status_code == 403
    assert resp.json()["code"] == "AUTH_FORBIDDEN"


async def test_limit_bounds(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await users.add(session, "admin@congty.vn", Role.ADMIN, "root")
    await _login(client, "admin@congty.vn")
    for limit in (0, 501):
        resp = await client.get("/api/v1/admin/audit-log", params={"limit": limit})
        assert resp.status_code == 422
        assert resp.json()["code"] == "VALIDATION_ERROR"


async def test_expire_90_days(session: AsyncSession) -> None:
    for name, age in (("old.pdf", 91), ("new.pdf", 89)):
        await audit.record(session, "u@x.vn", "UPLOAD", None, name)
        await session.execute(
            text("UPDATE audit_log SET at = :t WHERE doc_name = :n"),
            {"t": NOW - timedelta(days=age), "n": name},
        )
    assert await audit.expire(session, NOW) == 1
    rows = await session.execute(text("SELECT doc_name FROM audit_log"))
    assert [r[0] for r in rows] == ["new.pdf"]


async def test_no_mutating_routes(client: httpx.AsyncClient, app: object) -> None:
    resp = await client.get("/openapi.json")
    methods = resp.json()["paths"]["/api/v1/admin/audit-log"]
    assert set(methods) == {"get"}
