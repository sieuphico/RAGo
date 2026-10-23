from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import CurrentUser, Role
from app.modules.auth.cookies import issue_cookie, read_cookie
from app.modules.telemetry.service import emit
from app.modules.users import repository as users
from app.ports.idp import IdpPort


async def complete_login(
    session: AsyncSession, idp: IdpPort, params: dict[str, str], now: datetime | None = None
) -> tuple[str, bool]:
    """Trả (giá trị cookie, là lần đăng nhập đầu). Ngoài allow-list vẫn nhận cookie (US-002)."""
    now = now or datetime.now(UTC)
    identity = await idp.complete(params)
    email = identity.email.lower()
    first = False
    if await users.get_by_email(session, email) is not None:
        first = await users.mark_login(session, email, now)
    return issue_cookie(email, get_settings(), now), first


async def record_login(session: AsyncSession, cookie: str, is_first_login: bool) -> None:
    """Phát `auth_login_succeeded` hoặc `auth_access_denied(not_in_allowlist)` (telemetry, T-314)."""
    data = read_cookie(cookie, get_settings())
    if data is None:
        return
    entry = await users.get_by_email(session, data.email)
    if entry is not None:
        await emit(
            session,
            CurrentUser(entry.email, entry.role),
            data.sid,
            "auth_login_succeeded",
            is_first_login=is_first_login,
        )
    else:
        await emit(
            session,
            CurrentUser(data.email, Role.BD_USER),  # vai trò không dùng: chỉ cần email để băm
            data.sid,
            "auth_access_denied",
            reason="not_in_allowlist",
        )
