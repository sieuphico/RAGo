import uuid
from typing import Protocol


def new_file_key() -> str:
    """Khóa tệp do máy chủ tạo; không bao giờ lấy từ tên tệp của người dùng."""
    return f"{uuid.uuid4().hex}.pdf"


class StoragePort(Protocol):
    def save(self, key: str, data: bytes) -> None: ...

    def read(self, key: str, start: int | None = None, end: int | None = None) -> bytes:
        """`end` không bao gồm."""
        ...

    def size(self, key: str) -> int: ...

    def delete(self, key: str) -> None: ...
