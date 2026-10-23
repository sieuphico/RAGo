from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_fake import AiFake
from app.adapters.ocr_fake import OcrFake
from app.adapters.storage_fs import FsStorage
from app.core.config import get_settings
from app.domain import DocumentStatus, FailureReason, Job
from app.models.document import Document
from app.ports.ai import ProviderError
from app.ports.storage import new_file_key
from app.worker import chunker, ingest
from app.worker.ingest import IngestDeps, handle_ingest
from tests.fixtures.documents import make_document


class SharedSession:
    """Factory trả về cùng một session của test (rollback sau test)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def __call__(self) -> "SharedSession":
        return self

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, *exc: object) -> None:
        return None


@pytest.fixture
def published(monkeypatch: pytest.MonkeyPatch) -> list[DocumentStatus]:
    calls: list[DocumentStatus] = []

    async def record(
        session: AsyncSession,
        doc_id: UUID,
        status: DocumentStatus,
        reason: FailureReason | None = None,
        page_count: int | None = None,
    ) -> None:
        calls.append(status)

    monkeypatch.setattr(ingest, "publish_status", record)
    return calls


def _deps(session: AsyncSession, tmp_path: Path, **overrides: Any) -> IngestDeps:
    settings = overrides.pop("settings", get_settings())
    values: dict[str, Any] = {
        "factory": SharedSession(session),
        "storage": FsStorage(tmp_path),
        "embed": AiFake(dim=settings.embedding_dim).embed,
        "ocr": OcrFake(confidence=0.95),
        "render": lambda pdf, page: b"png",
        "settings": settings,
    }
    values.update(overrides)
    return IngestDeps(**values)


async def _doc_from(
    session: AsyncSession, deps: IngestDeps, sample_pdfs: Path, name: str
) -> tuple[Document, Job]:
    key = new_file_key()
    deps.storage.save(key, (sample_pdfs / name).read_bytes())
    doc = await make_document(session, file_key=key)
    await session.commit()
    return doc, Job(uuid4(), "ingest", {"docId": str(doc.doc_id)}, attempts=1)


async def _chunks(session: AsyncSession) -> int:
    return int((await session.execute(text("SELECT count(*) FROM chunk"))).scalar_one())


async def _reload(session: AsyncSession, doc: Document) -> Document:
    fresh = (
        await session.execute(
            select(Document)
            .where(Document.doc_id == sa_inspect(doc).identity[0])  # type: ignore[index]
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    return fresh


async def test_text_pdf_reaches_ready(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    deps = _deps(session, tmp_path)
    doc, job = await _doc_from(session, deps, sample_pdfs, "text_12p.pdf")
    await handle_ingest(job, deps)
    fresh = await _reload(session, doc)
    assert (fresh.status, fresh.page_count, fresh.used_ocr) == (DocumentStatus.READY, 12, False)
    assert fresh.processed_at is not None
    assert await _chunks(session) > 0
    assert published == [DocumentStatus.READY]


@pytest.mark.parametrize(
    ("name", "reason"),
    [
        ("corrupted.pdf", FailureReason.FILE_CORRUPTED),
        ("encrypted.pdf", FailureReason.FILE_ENCRYPTED),
    ],
)
async def test_bad_pdf_failed_without_retry(
    session: AsyncSession,
    tmp_path: Path,
    sample_pdfs: Path,
    published: list[DocumentStatus],
    name: str,
    reason: FailureReason,
) -> None:
    deps = _deps(session, tmp_path)
    doc, job = await _doc_from(session, deps, sample_pdfs, name)
    await handle_ingest(job, deps)  # không ném lỗi: tác vụ sẽ DONE, không thử lại
    fresh = await _reload(session, doc)
    assert (fresh.status, fresh.failure_reason) == (DocumentStatus.FAILED, reason)
    assert published == [DocumentStatus.FAILED]
    assert await _chunks(session) == 0


async def test_scanned_pdf_uses_ocr_state(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    deps = _deps(session, tmp_path)
    doc, job = await _doc_from(session, deps, sample_pdfs, "scan_1p.pdf")
    await handle_ingest(job, deps)
    fresh = await _reload(session, doc)
    assert fresh.status == DocumentStatus.READY and fresh.used_ocr is True
    assert published == [DocumentStatus.OCR_PROCESSING, DocumentStatus.READY]


async def test_scan_below_threshold_is_unreadable(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    deps = _deps(session, tmp_path, ocr=OcrFake(confidence=0.3))
    doc, job = await _doc_from(session, deps, sample_pdfs, "scan_1p.pdf")
    await handle_ingest(job, deps)
    fresh = await _reload(session, doc)
    assert (fresh.status, fresh.failure_reason) == (
        DocumentStatus.FAILED,
        FailureReason.OCR_UNREADABLE,
    )
    assert await _chunks(session) == 0


async def test_deleted_midway_no_chunks(
    session: AsyncSession,
    tmp_path: Path,
    sample_pdfs: Path,
    published: list[DocumentStatus],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deps = _deps(session, tmp_path)
    doc, job = await _doc_from(session, deps, sample_pdfs, "text_1p.pdf")
    real_split = chunker.split

    def split_then_delete(*args: Any, **kwargs: Any) -> Any:
        doc.deleted_at = datetime.now(UTC)  # người dùng xóa trong lúc đang xử lý
        return real_split(*args, **kwargs)

    monkeypatch.setattr("app.worker.ingest.split", split_then_delete)
    await handle_ingest(job, deps)
    fresh = await _reload(session, doc)
    # (rollback của handler cũng hoàn tác việc xóa giả lập cùng giao dịch; chỉ kiểm hành vi)
    assert fresh.status == DocumentStatus.PROCESSING
    assert await _chunks(session) == 0
    assert published == []


async def test_transient_error_retried(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    ai, state = AiFake(dim=384), {"calls": 0}

    async def flaky(texts: list[str]) -> list[list[float]]:
        state["calls"] += 1
        if state["calls"] == 1:
            raise ProviderError("down")
        return await ai.embed(texts)

    deps = _deps(session, tmp_path, embed=flaky)
    doc, job = await _doc_from(session, deps, sample_pdfs, "text_1p.pdf")
    with pytest.raises(ProviderError):
        await handle_ingest(job, deps)
    assert (await _reload(session, doc)).status == DocumentStatus.PROCESSING  # chờ thử lại
    await handle_ingest(Job(job.job_id, "ingest", job.payload, attempts=2), deps)
    assert (await _reload(session, doc)).status == DocumentStatus.READY


async def test_last_attempt_marks_failed(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    async def broken(texts: list[str]) -> list[list[float]]:
        raise ProviderError("down")

    deps = _deps(session, tmp_path, embed=broken)
    doc, job = await _doc_from(session, deps, sample_pdfs, "text_1p.pdf")
    last = Job(job.job_id, "ingest", job.payload, attempts=deps.settings.job_max_attempts)
    with pytest.raises(ProviderError):
        await handle_ingest(last, deps)
    fresh = await _reload(session, doc)
    assert (fresh.status, fresh.failure_reason) == (
        DocumentStatus.FAILED,
        FailureReason.PROCESSING_ERROR,
    )


@pytest.mark.parametrize(("enabled", "expected"), [(True, 1), (False, 0)])
async def test_suggest_enqueued(
    session: AsyncSession,
    tmp_path: Path,
    sample_pdfs: Path,
    published: list[DocumentStatus],
    enabled: bool,
    expected: int,
) -> None:
    settings = get_settings().model_copy(
        update={"features": frozenset({"suggestions"} if enabled else set())}
    )
    deps = _deps(session, tmp_path, settings=settings)
    _, job = await _doc_from(session, deps, sample_pdfs, "text_1p.pdf")
    await handle_ingest(job, deps)
    count = (
        await session.execute(text("SELECT count(*) FROM job WHERE type = 'suggest'"))
    ).scalar_one()
    assert count == expected


async def test_already_done_is_noop(
    session: AsyncSession, tmp_path: Path, sample_pdfs: Path, published: list[DocumentStatus]
) -> None:
    deps = _deps(session, tmp_path)
    _, job = await _doc_from(session, deps, sample_pdfs, "text_1p.pdf")
    await handle_ingest(job, deps)
    published.clear()
    await handle_ingest(job, deps)  # chạy lại: không đổi trạng thái, không phát lại
    assert published == [] and await _chunks(session) > 0
