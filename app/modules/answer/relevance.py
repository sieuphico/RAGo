"""Quyết định có đủ bằng chứng để gọi AI hay trả "không tìm thấy" ngay (US-023).

Ngưỡng mặc định 0,0 (mọi chunk tìm được đều đạt) để không chặn luồng; giá trị thật chỉnh bằng
bộ câu hỏi chuẩn ở T-607 (RA-06, CONTRACTS Q-C13).
"""

from typing import Literal

from app.domain import ScoredChunk

Decision = Literal["ANSWER", "NO_READY_DOCS", "NO_EVIDENCE"]


def _passes(chunk: ScoredChunk, threshold: float) -> bool:
    return chunk.keyword_hit or (chunk.similarity is not None and chunk.similarity >= threshold)


def filter_evidence(chunks: list[ScoredChunk], threshold: float) -> list[ScoredChunk]:
    """Chỉ các chunk đạt được đưa vào prompt; giữ thứ tự."""
    return [c for c in chunks if _passes(c, threshold)]


def decide(chunks: list[ScoredChunk], ready_doc_count: int, threshold: float) -> Decision:
    if ready_doc_count == 0:
        return "NO_READY_DOCS"
    if not filter_evidence(chunks, threshold):
        return "NO_EVIDENCE"
    return "ANSWER"
