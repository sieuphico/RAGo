"""Xóa phiên hội thoại quá `history_days` ngày (OQ-013); chạy hằng ngày 02:30."""

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.chat import repository as chat


async def expire_history(session: AsyncSession, now: datetime) -> int:
    cutoff = now - timedelta(days=get_settings().history_days)
    return await chat.delete_sessions_before(session, cutoff)
