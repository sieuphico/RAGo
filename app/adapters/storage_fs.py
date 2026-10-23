"""Kho tệp trên đĩa. Khóa do máy chủ tạo; không bao giờ ghép từ tên tệp của người dùng."""

import os
import re
import tempfile
from pathlib import Path

from app.ports.storage import new_file_key

__all__ = ["FsStorage", "new_file_key"]

_KEY = re.compile(r"^[0-9a-f]{32}\.pdf$")


class FsStorage:
    def __init__(self, root: Path) -> None:
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if not _KEY.fullmatch(key):
            raise ValueError("khóa tệp không hợp lệ")
        return self.root / key[:2] / key

    def save(self, key: str, data: bytes) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
            os.chmod(tmp, 0o600)
            os.replace(tmp, path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    def read(self, key: str, start: int | None = None, end: int | None = None) -> bytes:
        """Đọc byte [start, end); `end` không bao gồm."""
        data = self._path(key).read_bytes()
        return data[start:end]

    def size(self, key: str) -> int:
        return self._path(key).stat().st_size

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)
