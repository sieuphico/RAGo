"""Các lượt hỏi–đáp gần nhất của chính phiên, cho câu hỏi nối tiếp (US-025)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import MessageStatus, Turn
from app.models.chat import Message


async def recent_turns(session: AsyncSession, session_id: UUID, n: int = 3) -> list[Turn]:
    """Tối đa `n` cặp đã COMPLETED, cũ trước mới sau. Câu đang hỏi chưa có đáp COMPLETED nên không lọt vào."""
    rows = (
        await session.execute(
            select(Message.role, Message.text, Message.status)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at, Message.message_id)
            .execution_options(populate_existing=True)
        )
    ).all()
    turns: list[Turn] = []
    question: str | None = None
    for role, text, status in rows:
        if role == "user":
            question = text
        elif role == "assistant" and status == MessageStatus.COMPLETED and question is not None:
            turns.append(Turn(question=question, answer=text))
            question = None
    return turns[-n:]
