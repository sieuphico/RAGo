from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.auth.cookies import issue_cookie
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
