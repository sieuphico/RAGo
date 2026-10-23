"""Trích văn bản theo trang từ PDF. PDF là đầu vào không tin cậy (SAD 4.1): chạy trong tiến trình
con có thời hạn, hết hạn thì giết tiến trình."""

import multiprocessing as mp
import re
import unicodedata
from io import BytesIO
from multiprocessing.connection import Connection

from app.domain import FailureReason, PageText

MIN_TEXT_CHARS = 20
TIMEOUT_S = 120


class ExtractError(Exception):
    def __init__(self, reason: FailureReason) -> None:
        super().__init__(reason.value)
        self.reason = reason


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    lines = (re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _extract(data: bytes, max_pages: int) -> list[tuple[int, str, bool]]:
    """Chạy trong tiến trình con; ném ExtractError."""
    from pypdf import PdfReader
    from pypdf.errors import PyPdfError

    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted and not reader.decrypt(""):
            raise ExtractError(FailureReason.FILE_ENCRYPTED)
        count = len(reader.pages)
        if count > max_pages:
            raise ExtractError(FailureReason.PROCESSING_ERROR)
        pages: list[tuple[int, str, bool]] = []
        for number, page in enumerate(reader.pages, start=1):
            text = _normalize(page.extract_text() or "")
            pages.append((number, text, len(text.strip()) >= MIN_TEXT_CHARS))
        return pages
    except ExtractError:
        raise
    except (PyPdfError, ValueError, KeyError, TypeError, AttributeError, OSError, RecursionError):
        raise ExtractError(FailureReason.FILE_CORRUPTED) from None


def _child(conn: Connection, data: bytes, max_pages: int) -> None:
    try:
        conn.send(("ok", _extract(data, max_pages)))
    except ExtractError as exc:
        conn.send(("err", exc.reason.value))
    except BaseException:  # noqa: BLE001 - tiến trình con không được chết im lặng
        conn.send(("err", FailureReason.PROCESSING_ERROR.value))
    finally:
        conn.close()


def extract_pages(data: bytes, *, max_pages: int, timeout_s: float = TIMEOUT_S) -> list[PageText]:
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_child, args=(child, data, max_pages), daemon=True)
    process.start()
    child.close()
    try:
        if not parent.poll(timeout_s):
            raise ExtractError(FailureReason.PROCESSING_ERROR)
        kind, payload = parent.recv()
    except (EOFError, OSError):  # tiến trình con bị giết hoặc sập
        raise ExtractError(FailureReason.PROCESSING_ERROR) from None
    finally:
        parent.close()
        if process.is_alive():
            process.terminate()
        process.join(5)
    if kind == "err":
        raise ExtractError(FailureReason(payload))
    result: list[tuple[int, str, bool]] = payload
    return [PageText(page=n, text=t, has_text_layer=h) for n, t, h in result]


__all__ = ["ExtractError", "extract_pages"]
