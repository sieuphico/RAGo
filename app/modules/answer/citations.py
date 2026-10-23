"""Đổi nhãn chunk `[cN]` trong đầu ra của AI thành trích dẫn `[[n]]`; nhãn lạ bị xóa (AD-13, CONTRACTS 4.3)."""

import re

from app.domain import ChunkRef, CitationOut

_LABELS = re.compile(r"\[(c\d+(?:\s*,\s*c\d+)*)\]")
_PARTIAL = re.compile(r"\[(c\d*(\s*,\s*c?\d*)*)?$")


class CitationResolver:
    def __init__(self, label_map: dict[str, ChunkRef]) -> None:
        self.label_map = label_map
        self._index_by_label: dict[str, int] = {}
        self._citations: list[CitationOut] = []
        self._buffer = ""

    @property
    def citations(self) -> list[CitationOut]:
        return list(self._citations)

    def _cite(self, label: str, fresh: list[CitationOut]) -> str:
        ref = self.label_map.get(label)
        if ref is None:
            return ""
        index = self._index_by_label.get(label)
        if index is None:
            index = len(self._citations) + 1
            self._index_by_label[label] = index
            citation = CitationOut(
                index=index,
                doc_id=ref.doc_id,
                doc_name=ref.doc_name,
                page=ref.page,
                snippet=ref.snippet[:200],
            )
            self._citations.append(citation)
            fresh.append(citation)
        return f"[[{index}]]"

    def _replace(self, text: str, fresh: list[CitationOut]) -> str:
        def sub(match: re.Match[str]) -> str:
            labels = [part.strip() for part in match.group(1).split(",")]
            return "".join(self._cite(label, fresh) for label in labels)

        return _LABELS.sub(sub, text)

    def feed(self, delta: str) -> tuple[str, list[CitationOut]]:
        """Trả (văn bản an toàn, trích dẫn mới). Gửi trích dẫn mới trước văn bản."""
        self._buffer += delta
        partial = _PARTIAL.search(self._buffer)
        cut = partial.start() if partial else len(self._buffer)
        ready, self._buffer = self._buffer[:cut], self._buffer[cut:]
        fresh: list[CitationOut] = []
        return self._replace(ready, fresh), fresh

    def finish(self) -> tuple[str, list[CitationOut]]:
        """Nhãn dở ở cuối bị bỏ."""
        self._buffer = ""
        return "", []


def resolve(text: str, label_map: dict[str, ChunkRef]) -> tuple[str, list[CitationOut]]:
    resolver = CitationResolver(label_map)
    out, _ = resolver.feed(text)
    tail, _ = resolver.finish()
    return out + tail, resolver.citations
