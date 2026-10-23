from uuid import uuid4

from app.domain import ChunkRef
from app.modules.answer.citations import CitationResolver, resolve


def _ref(name: str, page: int, snippet: str = "đoạn trích") -> ChunkRef:
    return ChunkRef(chunk_id=uuid4(), doc_id=uuid4(), doc_name=name, page=page, snippet=snippet)


def _map() -> dict[str, ChunkRef]:
    return {"c1": _ref("A.pdf", 3), "c2": _ref("B.pdf", 7)}


def test_valid_labels_resolved() -> None:
    label_map = _map()
    text, citations = resolve("A [c2]. B [c1].", label_map)
    assert text == "A [[1]]. B [[2]]."
    assert citations[0].doc_name == "B.pdf" and citations[0].index == 1
    assert citations[1].doc_name == "A.pdf" and citations[1].page == 3


def test_unknown_label_dropped() -> None:
    text, citations = resolve("A [c9].", {"c1": _ref("A.pdf", 1)})
    assert text == "A ." and citations == []


def test_partial_label_buffered() -> None:
    resolver = CitationResolver(_map())
    first = resolver.feed("Thời hạn [c")
    assert first == ("Thời hạn ", [])
    second_text, second_new = resolver.feed("1] tháng")
    assert second_text == "[[1]] tháng" and len(second_new) == 1


def test_group_label() -> None:
    text, citations = resolve("X [c1, c2].", _map())
    assert text == "X [[1]][[2]]." and len(citations) == 2


def test_repeat_label_same_index() -> None:
    text, citations = resolve("[c1] và [c1]", _map())
    assert text == "[[1]] và [[1]]" and len(citations) == 1


def test_snippet_limit() -> None:
    _, citations = resolve("[c1]", {"c1": _ref("A.pdf", 1, snippet="x" * 200)})
    assert len(citations[0].snippet) <= 200


def test_dangling_label_at_end() -> None:
    resolver = CitationResolver(_map())
    assert resolver.feed("kết thúc [c") == ("kết thúc ", [])
    assert resolver.finish() == ("", [])


def test_token_by_token_equals_whole() -> None:
    whole, _ = resolve("Có [c1, c2] và [c2]. Hết [c7].", _map())
    resolver = CitationResolver(_map())
    pieces = [resolver.feed(ch)[0] for ch in "Có [c1, c2] và [c2]. Hết [c7]."]
    pieces.append(resolver.finish()[0])
    assert "".join(pieces) == whole == "Có [[1]][[2]] và [[2]]. Hết ."


def test_new_citation_reported_exactly_once() -> None:
    resolver = CitationResolver(_map())
    _, first = resolver.feed("a [c1] ")
    _, second = resolver.feed("b [c1] c [c2]")
    assert len(first) == 1 and [c.index for c in second] == [2]
    assert [c.index for c in resolver.citations] == [1, 2]


def test_plain_brackets_untouched() -> None:
    text, citations = resolve("Điều [1] và [abc] giữ nguyên", _map())
    assert text == "Điều [1] và [abc] giữ nguyên" and citations == []
