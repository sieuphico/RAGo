"""Bộ đếm chi phí AI theo tháng."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import AiUsage


async def add_cost(session: AsyncSession, month: date, usd: float) -> None:
    """Cộng dồn nguyên tử, an toàn khi nhiều giao dịch cùng ghi."""
    stmt = insert(AiUsage).values(month=month, cost_usd=usd)
    stmt = stmt.on_conflict_do_update(
        index_elements=[AiUsage.month],
        set_={"cost_usd": AiUsage.cost_usd + stmt.excluded.cost_usd, "updated_at": func.now()},
    )
    await session.execute(stmt)
    await session.flush()


async def get_cost(session: AsyncSession, month: date) -> float:
    value = (
        await session.execute(select(AiUsage.cost_usd).where(AiUsage.month == month))
    ).scalar_one_or_none()
    return float(value) if value is not None else 0.0
