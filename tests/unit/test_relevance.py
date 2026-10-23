from uuid import uuid4

from app.domain import ScoredChunk
from app.modules.answer.relevance import decide, filter_evidence


def _chunk(similarity: float | None, keyword_hit: bool = False) -> ScoredChunk:
    return ScoredChunk(
        chunk_id=uuid4(), doc_id=uuid4(), doc_name="a.pdf", page=1, text="t",
        score=0.1, similarity=similarity, keyword_hit=keyword_hit,
    )  # fmt: skip


def test_below_threshold_not_enough() -> None:
    chunks = [_chunk(0.3), _chunk(0.4)]
    assert decide(chunks, 3, 0.5) == "NO_EVIDENCE"
    assert filter_evidence(chunks, 0.5) == []


def test_keyword_hit_passes() -> None:
    assert decide([_chunk(None, keyword_hit=True)], 3, 0.9) == "ANSWER"


def test_no_ready_docs() -> None:
    assert decide([_chunk(0.9)], 0, 0.5) == "NO_READY_DOCS"


def test_threshold_configurable() -> None:
    chunks = [_chunk(0.6)]
    assert decide(chunks, 3, 0.5) == "ANSWER"
    assert decide(chunks, 3, 0.7) == "NO_EVIDENCE"


def test_empty_list() -> None:
    assert decide([], 3, 0.5) == "NO_EVIDENCE"


def test_default_threshold_zero_passes_everything() -> None:
    assert decide([_chunk(0.01)], 1, 0.0) == "ANSWER"


def test_filter_keeps_order() -> None:
    a, b, c = _chunk(0.9), _chunk(0.1), _chunk(0.8)
    assert filter_evidence([a, b, c], 0.5) == [a, c]
