"""Allow-list. Email luôn lưu và tra ở dạng chữ thường."""

from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Role
from app.models.admin import AllowListEntry


async def get_by_email(session: AsyncSession, email: str) -> AllowListEntry | None:
    return await session.get(AllowListEntry, email.lower())


async def list_all(session: AsyncSession) -> list[AllowListEntry]:
    result = await session.execute(select(AllowListEntry).order_by(AllowListEntry.added_at))
    return list(result.scalars())


async def add(session: AsyncSession, email: str, role: Role, added_by: str) -> AllowListEntry:
    entry = AllowListEntry(email=email.lower(), role=role, added_by=added_by)
    session.add(entry)
    await session.flush()
    await session.refresh(entry)
    return entry


async def remove(session: AsyncSession, email: str) -> bool:
    entry = await get_by_email(session, email)
    if entry is None:
        return False
    await session.delete(entry)
    await session.flush()
    return True


async def count(session: AsyncSession) -> int:
    return int((await session.execute(select(func.count()).select_from(AllowListEntry))).scalar_one())


async def count_by_role(session: AsyncSession, role: Role) -> int:
    query = select(func.count()).select_from(AllowListEntry).where(AllowListEntry.role == role)
    return int((await session.execute(query)).scalar_one())


async def mark_login(session: AsyncSession, email: str, at: datetime) -> bool:
    """True nếu đây là lần đăng nhập đầu tiên."""
    result = await session.execute(
        update(AllowListEntry)
        .where(AllowListEntry.email == email.lower(), AllowListEntry.first_login_at.is_(None))
        .values(first_login_at=at)
    )
    await session.flush()
    return bool(result.rowcount)  # type: ignore[attr-defined]
