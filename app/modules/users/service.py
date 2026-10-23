"""Quản lý allow-list (AD-09): kiểm tra email, giới hạn 20 người, không gỡ quản trị viên cuối."""

import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ErrorCode
from app.domain import CurrentUser, Role
from app.models.admin import AllowListEntry
from app.modules.users import repository as users

logger = logging.getLogger("app.users")
USER_LIMIT = 20  # ASM-002
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    cleaned = email.strip().lower()
    if not _EMAIL.fullmatch(cleaned):
        raise AppError(ErrorCode.EMAIL_INVALID)
    return cleaned


async def add_user(
    session: AsyncSession, email: str, role: Role, actor: CurrentUser
) -> AllowListEntry:
    cleaned = normalize_email(email)
    if await users.get_by_email(session, cleaned) is not None:
        raise AppError(ErrorCode.USER_EXISTS)
    if await users.count(session) >= USER_LIMIT:
        raise AppError(ErrorCode.USER_LIMIT_REACHED)
    entry = await users.add(session, cleaned, role, actor.email)
    logger.info("user_added role=%s", role.value)  # không ghi email
    return entry


async def remove_user(session: AsyncSession, email: str, actor: CurrentUser) -> None:
    entry = await users.get_by_email(session, email)
    if entry is None:
        raise AppError(ErrorCode.NOT_FOUND)
    if entry.role == Role.ADMIN and await users.count_by_role(session, Role.ADMIN) <= 1:
        raise AppError(ErrorCode.LAST_ADMIN)
    await users.remove(session, entry.email)
    logger.info("user_removed role=%s", entry.role.value)


async def ensure_admin(session: AsyncSession, email: str) -> bool:
    """Tạo quản trị viên đầu tiên (CLI). Trả True nếu vừa tạo; chạy lại không lỗi."""
    cleaned = normalize_email(email)
    if await users.get_by_email(session, cleaned) is not None:
        return False
    await users.add(session, cleaned, Role.ADMIN, "cli")
    return True
