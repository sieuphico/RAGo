"""Chia văn bản từng trang thành chunk; mỗi chunk thuộc đúng một trang (để trích dẫn đúng số trang)."""

import re

from app.domain import ChunkDraft, PageText

_SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")


def _hard_cut(text: str, limit: int) -> list[str]:
    """Cắt tại khoảng trắng gần nhất trước `limit`; không có khoảng trắng thì cắt cứng."""
    parts: list[str] = []
    rest = text.strip()
    while len(rest) > limit:
        cut = rest.rfind(" ", 0, limit + 1)
        if cut <= 0:
            cut = limit
        parts.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        parts.append(rest)
    return parts


def _units(page_text: str, target: int) -> list[str]:
    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", page_text):
        paragraph = " ".join(paragraph.split())
        if not paragraph:
            continue
        pieces = [paragraph] if len(paragraph) <= target else _SENTENCE_END.split(paragraph)
        for piece in pieces:
            units.extend(_hard_cut(piece, target) if len(piece) > target else [piece])
    return units


def _tail(chunk: str, overlap: int) -> str:
    """Phần cuối chunk (≤ overlap ký tự), bắt đầu tại ranh giới từ."""
    if len(chunk) <= overlap:
        return ""
    tail = chunk[-overlap:]
    space = tail.find(" ")
    return tail[space + 1 :] if space != -1 else tail


def split(
    pages: list[PageText], target_chars: int = 1200, overlap: int = 150
) -> list[ChunkDraft]:
    chunks: list[ChunkDraft] = []
    for page in pages:
        if not page.text.strip():
            continue
        packed: list[str] = []
        current = ""
        for unit in _units(page.text, target_chars):
            if current and len(current) + 1 + len(unit) > target_chars:
                packed.append(current)
                current = unit
            else:
                current = f"{current} {unit}" if current else unit
        if current:
            packed.append(current)
        previous = ""
        for body in packed:
            prefix = _tail(previous, overlap)
            text = f"{prefix} {body}" if prefix else body
            chunks.append(ChunkDraft(page=page.page, text=text))
            previous = body
    return chunks
