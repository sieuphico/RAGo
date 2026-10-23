"""Hàm dùng chung cho test API."""

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Role
from app.modules.users import repository as users

CSRF = {"X-Requested-With": "cwd"}


async def login(
    client: httpx.AsyncClient, session: AsyncSession, email: str, role: Role | None
) -> None:
    """Đăng nhập bằng IdP giả; `role=None` nghĩa là không thêm vào allow-list."""
    if role is not None and await users.get_by_email(session, email) is None:
        await users.add(session, email, role, "root")
    client.cookies.clear()
    resp = await client.get("/auth/login", params={"login_hint": email})
    await client.get(resp.headers["location"].removeprefix("https://test"))


class SharedSession:
    """Factory trả về cùng một session của test (rollback sau test)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def __call__(self) -> "SharedSession":
        return self

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, *exc: object) -> None:
        return None
