"""Cờ tính năng cho phần P1: cắt phạm vi mà không phá luồng P0 (DD-08, RSK-005).

Thứ tự cắt khi trễ theo BRD: BR-020 (gợi ý) → BR-019 (tóm tắt) → BR-021 (lịch sử) → BR-022 (sao chép).
"""

from collections.abc import Callable

from app.core.config import get_settings
from app.core.errors import AppError, ErrorCode

ALL_P1: tuple[str, ...] = (
    "suggestions",
    "summary",
    "history",
    "rating",
    "copy",
    "scope",
    "followup",
    "duplicateCheck",
)


def is_enabled(name: str) -> bool:
    if name not in ALL_P1:
        raise ValueError(f"tính năng không tồn tại: {name}")
    return name in get_settings().features


def require_feature(name: str) -> Callable[[], None]:
    """Dependency FastAPI: tính năng tắt thì route trả 404 NOT_FOUND."""
    if name not in ALL_P1:
        raise ValueError(f"tính năng không tồn tại: {name}")

    def dependency() -> None:
        if not is_enabled(name):
            raise AppError(ErrorCode.NOT_FOUND)

    return dependency
