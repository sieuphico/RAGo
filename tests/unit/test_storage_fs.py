import os
from pathlib import Path

import pytest

from app.adapters import storage_fs
from app.adapters.storage_fs import FsStorage, new_file_key


def test_path_traversal_rejected(tmp_path: Path) -> None:
    store = FsStorage(tmp_path)
    for bad in ("../x.pdf", "/etc/passwd", "a/b.pdf", "x.pdf"):
        with pytest.raises(ValueError):
            store.save(bad, b"..")
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_range_read(tmp_path: Path) -> None:
    store, key = FsStorage(tmp_path), new_file_key()
    store.save(key, bytes(range(100)))
    assert store.read(key, 10, 20) == bytes(range(10, 20))
    assert store.size(key) == 100


def test_read_to_end(tmp_path: Path) -> None:
    store, key = FsStorage(tmp_path), new_file_key()
    store.save(key, bytes(range(100)))
    assert store.read(key, 95, None) == bytes(range(95, 100))
    assert store.read(key) == bytes(range(100))


def test_delete_missing_ok(tmp_path: Path) -> None:
    store = FsStorage(tmp_path)
    store.delete(new_file_key())
    key = new_file_key()
    store.save(key, b"x")
    store.delete(key)
    store.delete(key)


def test_atomic_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store, key = FsStorage(tmp_path), new_file_key()

    def boom(src: object, dst: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        store.save(key, b"data")
    assert [p for p in tmp_path.rglob("*") if p.is_file()] == []


def test_new_file_key_matches_pattern() -> None:
    assert storage_fs._KEY.fullmatch(new_file_key())
