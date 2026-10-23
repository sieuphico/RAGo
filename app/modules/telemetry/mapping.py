"""Ánh xạ mã lỗi nội bộ sang giá trị liệt kê của telemetry và chống phát trùng sự kiện từ chối."""

from collections import OrderedDict
from typing import Literal

from app.domain import FailureReason

_SEEN_MAX = 10_000
_seen: OrderedDict[tuple[str, str], None] = OrderedDict()


def upload_reason(
    code: str, *, extension_ok: bool
) -> Literal["not_pdf", "too_large", "too_many", "invalid_pdf"]:
    if code == "FILE_TOO_LARGE":
        return "too_large"
    if code == "FILE_TOO_MANY":
        return "too_many"
    # FILE_NOT_PDF: sai đuôi tệp → not_pdf; đúng đuôi nhưng sai nội dung `%PDF-` → invalid_pdf
    return "invalid_pdf" if extension_ok else "not_pdf"


def failure_reason(
    reason: FailureReason,
) -> Literal["ocr_unreadable", "corrupted", "encrypted", "other"]:
    return {
        FailureReason.OCR_UNREADABLE: "ocr_unreadable",
        FailureReason.FILE_CORRUPTED: "corrupted",
        FailureReason.FILE_ENCRYPTED: "encrypted",
    }.get(reason, "other")  # type: ignore[return-value]


def emit_once(sid: str, reason: str) -> bool:
    """True nếu cặp (sid, reason) chưa phát; giữ tối đa 10.000 cặp gần nhất."""
    key = (sid, reason)
    if key in _seen:
        return False
    _seen[key] = None
    if len(_seen) > _SEEN_MAX:
        _seen.popitem(last=False)
    return True


def reset_seen() -> None:
    """Chỉ dùng trong test."""
    _seen.clear()
