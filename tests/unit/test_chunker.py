from app.domain import PageText
from app.worker.chunker import split


def _page(n: int, text: str) -> PageText:
    return PageText(page=n, text=text, has_text_layer=True)


def _sentences(count: int, size: int = 80) -> str:
    return " ".join(f"{'x' * (size - 3)}{i:02d}." for i in range(count))


def test_chunk_keeps_page() -> None:
    chunks = split([_page(1, "a" * 100), _page(2, "b" * 100)])
    assert [(c.page, c.text[0]) for c in chunks] == [(1, "a"), (2, "b")]


def test_chunk_size_bounds() -> None:
    chunks = split([_page(1, _sentences(62))])  # ~5.000 ký tự
    assert len(chunks) >= 4
    assert all(len(c.text) <= 1400 for c in chunks)
    assert {c.page for c in chunks} == {1}


def test_long_sentence_hard_cut() -> None:
    words = " ".join(["tu"] * 1500)  # 4.499 ký tự, không có dấu câu
    chunks = split([_page(1, words)])
    assert len(chunks) >= 3
    assert all(len(c.text) <= 1400 for c in chunks)
    assert all(not c.text.startswith("u") for c in chunks)  # không cắt giữa từ


def test_long_token_without_spaces_is_cut() -> None:
    chunks = split([_page(1, "z" * 3000)])
    assert all(len(c.text) <= 1400 for c in chunks)
    assert sum(len(c.text) for c in chunks) >= 3000


def test_overlap() -> None:
    text = " ".join(f"tu{i:03d}" for i in range(500))  # 3.499 ký tự
    first, second = split([_page(3, text)])[:2]
    sizes = [
        n
        for n in range(1, 400)
        if first.text.endswith(second.text[:n]) and second.text[n : n + 1] == " "
    ]
    assert any(100 <= n <= 150 for n in sizes), sizes


def test_empty_page_skipped() -> None:
    chunks = split([PageText(1, "   ", False), _page(2, "abc def")])
    assert [(c.page, c.text) for c in chunks] == [(2, "abc def")]


def test_no_chunk_spans_two_pages() -> None:
    chunks = split([_page(1, "mot trang"), _page(2, "hai trang")])
    assert all(("mot" in c.text) != ("hai" in c.text) for c in chunks)
