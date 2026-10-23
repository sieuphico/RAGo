from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage_fs import FsStorage
from app.core.config import get_settings
from app.domain import ChunkDraft, DocumentStatus, Job
from app.modules.documents import repository as repo
from app.ports.storage import new_file_key
from app.worker import purge
from app.worker.purge import PurgeDeps, purge_document, purge_sweep
from tests.fixtures.documents import make_document
from tests.integration.helpers import SharedSession

T = datetime(2026, 11, 2, 8, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _no_notify(monkeypatch: pytest.MonkeyPatch) -> None:
    async def noop(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr(purge, "publish_status", noop)


def _deps(session: AsyncSession, tmp_path: Path) -> PurgeDeps:
    return PurgeDeps(SharedSession(session), FsStorage(tmp_path), get_settings())


async def _ready_doc(session: AsyncSession, deps: PurgeDeps, *, deleted: bool) -> UUID:
    key = new_file_key()
    deps.storage.save(key, b"%PDF-1.4 data")
    doc = await make_document(session, name="HD.pdf", file_key=key, status=DocumentStatus.READY)
    await repo.add_chunks(
        session, doc.doc_id, [ChunkDraft(page=i + 1, text=f"c{i}") for i in range(5)],
        [[0.1] * 384] * 5,
    )  # fmt: skip
    await session.execute(
        text("INSERT INTO suggestion (doc_id, questions) VALUES (:d, CAST(:q AS jsonb))"),
        {"d": doc.doc_id, "q": '["a","b","c"]'},
    )
    if deleted:
        await repo.soft_delete(session, doc.doc_id, T)
    await session.commit()
    return doc.doc_id


async def _count(session: AsyncSession, table: str) -> int:
    return int((await session.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one())


def _job(doc_id: UUID) -> Job:
    return Job(uuid4(), "purge", {"docId": str(doc_id)}, attempts=1)


async def test_purge_removes_chunks_and_file(session: AsyncSession, tmp_path: Path) -> None:
    deps = _deps(session, tmp_path)
    doc_id = await _ready_doc(session, deps, deleted=True)
    key = (await session.execute(text("SELECT file_key FROM document"))).scalar_one()
    await purge_document(_job(doc_id), deps)
    assert await _count(session, "chunk") == 0 and await _count(session, "suggestion") == 0
    with pytest.raises(FileNotFoundError):
        deps.storage.size(key)
    status = (await session.execute(text("SELECT status FROM document"))).scalar_one()
    assert status == "DELETED"
    assert await _count(session, "document") == 1  # giữ hàng cho trích dẫn cũ (EC-14)


async def test_audit_purge_record(session: AsyncSession, tmp_path: Path) -> None:
    deps = _deps(session, tmp_path)
    doc_id = await _ready_doc(session, deps, deleted=True)
    await purge_document(_job(doc_id), deps)
    rows = (await session.execute(text("SELECT actor, action, doc_name FROM audit_log"))).all()
    assert [tuple(r) for r in rows] == [("system", "PURGE", "HD.pdf")]


async def test_purge_twice_is_noop(session: AsyncSession, tmp_path: Path) -> None:
    deps = _deps(session, tmp_path)
    doc_id = await _ready_doc(session, deps, deleted=True)
    await purge_document(_job(doc_id), deps)
    await purge_document(_job(doc_id), deps)
    assert await _count(session, "audit_log") == 1


async def test_not_deleted_skipped(
    session: AsyncSession, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    deps = _deps(session, tmp_path)
    doc_id = await _ready_doc(session, deps, deleted=False)
    with caplog.at_level("WARNING", logger="app.worker.purge"):
        await purge_document(_job(doc_id), deps)
    assert await _count(session, "chunk") == 5
    assert "purge skipped" in caplog.text


async def test_scheduler_catches_missed_purge(session: AsyncSession, tmp_path: Path) -> None:
    deps = _deps(session, tmp_path)
    await _ready_doc(session, deps, deleted=True)  # deleted_at = T, không có tác vụ purge
    assert await purge_sweep(T + timedelta(hours=22), deps) == 0  # chưa gần hết hạn
    assert await purge_sweep(T + timedelta(hours=23), deps) == 1
    assert await purge_sweep(T + timedelta(hours=23), deps) == 0  # đã có tác vụ đang chờ
    assert await _count(session, "job") == 1
