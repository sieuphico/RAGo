from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_fake import AiFake
from app.adapters.ocr_fake import OcrFake
from app.adapters.storage_fs import FsStorage
from app.api.deps import get_storage
from app.core.config import get_settings
from app.domain import FailureReason, Job, Role
from app.modules.telemetry import mapping
from app.modules.users import repository as users
from app.ports.storage import new_file_key
from app.worker import ingest
from app.worker.ingest import IngestDeps, handle_ingest
from tests.fixtures.documents import make_document
from tests.fixtures.pdfs import PNG_BYTES, minimal_pdf
from tests.integration.helpers import CSRF, SharedSession, login

PROPS = "SELECT event, props, session_id FROM telemetry_event ORDER BY id"


@pytest.fixture(autouse=True)
def _fresh_dedupe() -> None:
    mapping.reset_seen()


async def _events(session: AsyncSession, name: str) -> list[Any]:
    rows = (await session.execute(text(PROPS))).all()
    return [r for r in rows if r[0] == name]


async def test_login_events(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    await login(client, session, "x@congty.vn", None)
    ok = await _events(session, "auth_login_succeeded")
    denied = await _events(session, "auth_access_denied")
    assert [r[1] for r in ok] == [{"is_first_login": True}]
    assert [r[1] for r in denied] == [{"reason": "not_in_allowlist"}]


async def test_revoked_event_once(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    await users.remove(session, "lan@congty.vn")
    for _ in range(3):
        assert (await client.get("/api/v1/documents")).status_code == 403
    assert [r[1] for r in await _events(session, "auth_access_denied")] == [{"reason": "revoked"}]


async def test_wrong_role_event_once(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "ntt@congty.vn", Role.SPONSOR)
    for _ in range(2):
        assert (await client.get("/api/v1/documents")).status_code == 403
    assert [r[1] for r in await _events(session, "auth_access_denied")] == [
        {"reason": "wrong_role"}
    ]


async def test_upload_rejected_events(
    app: Any, client: httpx.AsyncClient, session: AsyncSession, tmp_path: Path
) -> None:
    app.dependency_overrides[get_storage] = lambda: FsStorage(tmp_path)
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    files = [
        ("files", ("a.png", PNG_BYTES, "image/png")),
        ("files", ("not_pdf.pdf", PNG_BYTES, "application/pdf")),
        ("files", ("ok.pdf", minimal_pdf(), "application/pdf")),
    ]
    assert (await client.post("/api/v1/documents", files=files, headers=CSRF)).status_code == 202
    rejected = [r[1]["reason"] for r in await _events(session, "document_upload_rejected")]
    assert rejected == ["not_pdf", "invalid_pdf"]


async def test_too_many_files_event(
    app: Any, client: httpx.AsyncClient, session: AsyncSession, tmp_path: Path
) -> None:
    app.dependency_overrides[get_storage] = lambda: FsStorage(tmp_path)
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    files = [("files", (f"{i}.pdf", minimal_pdf(), "application/pdf")) for i in range(11)]
    assert (await client.post("/api/v1/documents", files=files, headers=CSRF)).status_code == 400
    assert [r[1] for r in await _events(session, "document_upload_rejected")] == [
        {"reason": "too_many"}
    ]


async def test_processing_events(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def no_notify(*args: object, **kwargs: object) -> None:
        return None

    monkeypatch.setattr(ingest, "publish_status", no_notify)
    settings = get_settings()
    deps = IngestDeps(
        SharedSession(session),
        FsStorage(tmp_path),
        AiFake(dim=settings.embedding_dim).embed,
        OcrFake(),
        lambda pdf, page: b"png",
        settings,
    )
    for name in ("text_1p.pdf", "corrupted.pdf"):
        key = new_file_key()
        deps.storage.save(key, (sample_pdfs / name).read_bytes())
        doc = await make_document(session, file_key=key, uploaded_by="minh@congty.vn")
        await session.commit()
        await handle_ingest(Job(uuid4(), "ingest", {"docId": str(doc.doc_id)}, 1), deps)
    done = await _events(session, "document_processing_completed")
    failed = await _events(session, "document_processing_failed")
    assert done[0][1]["page_count"] == 1 and done[0][1]["processing_seconds"] >= 0
    assert done[0][2] == "worker"
    assert failed[0][1]["reason"] == "corrupted" and failed[0][1]["used_ocr"] is False


async def test_document_deleted_event(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    doc = await make_document(session, uploaded_by="minh@congty.vn")
    for _ in range(2):
        await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    events = await _events(session, "document_deleted")
    assert len(events) == 1 and events[0][1]["actor_role"] == "TEAM_LEAD"


async def test_telemetry_failure_does_not_break_flow(
    app: Any,
    client: httpx.AsyncClient,
    session: AsyncSession,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.telemetry import service

    async def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr(service, "append_event", boom)
    app.dependency_overrides[get_storage] = lambda: FsStorage(tmp_path)
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    files = [("files", ("ok.pdf", minimal_pdf(), "application/pdf"))]
    assert (await client.post("/api/v1/documents", files=files, headers=CSRF)).status_code == 202


def test_mapping_helpers() -> None:
    assert mapping.upload_reason("FILE_TOO_LARGE", extension_ok=True) == "too_large"
    assert mapping.upload_reason("FILE_NOT_PDF", extension_ok=False) == "not_pdf"
    assert mapping.upload_reason("FILE_NOT_PDF", extension_ok=True) == "invalid_pdf"
    assert mapping.failure_reason(FailureReason.PROCESSING_ERROR) == "other"
    assert mapping.failure_reason(FailureReason.FILE_ENCRYPTED) == "encrypted"
    assert mapping.emit_once("s", "r") is True and mapping.emit_once("s", "r") is False
