"""Sinh 3 câu hỏi mẫu cho mỗi tài liệu khi `READY` (US-031, BR-020)."""

import json
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db
from app.core.config import Settings, get_settings
from app.core.wiring import build_gateway
from app.domain import DocumentStatus, Job
from app.models.document import Chunk, Document, Suggestion
from app.ports.ai import AiPort

logger = logging.getLogger("app.worker.suggest")
MAX_CHARS = 150
SYSTEM = (
    "Đề xuất đúng 3 câu hỏi ngắn (mỗi câu ≤ 150 ký tự) mà người đọc có thể hỏi về tài liệu, "
    "chỉ dựa trên các đoạn trích. Trả về một mảng JSON gồm 3 chuỗi, không thêm gì khác."
)
_FENCE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$")


@dataclass
class SuggestDeps:
    factory: Callable[[], Any]
    gateway: AiPort
    settings: Settings


def default_deps() -> SuggestDeps:
    settings = get_settings()
    return SuggestDeps(db.get_session_factory(), build_gateway(settings), settings)


def pick_positions(count: int) -> list[int]:
    """Tối đa 4 vị trí 0, n//4, n//2, 3n//4 (bỏ trùng, giữ thứ tự)."""
    return sorted({0, count // 4, count // 2, 3 * count // 4} & set(range(count)))


def parse_questions(raw: str) -> list[str]:
    cleaned = _FENCE.sub("", raw.strip()).strip()
    data = json.loads(cleaned)  # ValueError nếu không phải JSON
    if (
        not isinstance(data, list)
        or len(data) != 3
        or not all(isinstance(q, str) and 0 < len(q.strip()) <= MAX_CHARS for q in data)
    ):
        raise ValueError("gợi ý phải là mảng đúng 3 chuỗi không rỗng ≤ 150 ký tự")
    return [q.strip() for q in data]


async def _chunk_texts(session: AsyncSession, doc_id: UUID) -> list[str]:
    rows = await session.execute(
        select(Chunk.text).where(Chunk.doc_id == doc_id).order_by(Chunk.page, Chunk.chunk_id)
    )
    texts = list(rows.scalars())
    return [texts[i] for i in pick_positions(len(texts))]


async def generate_suggestions(job: Job, deps: SuggestDeps | None = None) -> None:
    deps = deps or default_deps()
    if "suggestions" not in deps.settings.features:
        return  # cờ tắt: hoàn tất ngay, không gọi AI
    doc_id = UUID(job.payload["docId"])
    async with deps.factory() as session:
        existing = await session.get(Suggestion, doc_id)
        doc = await session.get(Document, doc_id)
        if existing is not None or doc is None:
            return  # đã có gợi ý: không gọi AI lại
        if doc.deleted_at is not None or doc.status != DocumentStatus.READY:
            return
        excerpts = await _chunk_texts(session, doc_id)
        if not excerpts:
            return
    # Không gồm tên tệp (BR-028); không giữ phiên CSDL trong lúc chờ AI
    user = "\n\n".join(f"[Đoạn {i + 1}]\n{text}" for i, text in enumerate(excerpts))
    raw = "".join([token async for token in deps.gateway.generate(SYSTEM, user)])
    questions = parse_questions(raw)
    async with deps.factory() as session:
        stmt = insert(Suggestion).values(doc_id=doc_id, questions=questions)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Suggestion.doc_id], set_={"questions": stmt.excluded.questions}
        )
        await session.execute(stmt)
        await session.commit()
