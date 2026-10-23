"""Nhận tệp tải lên: kiểm tra lại ở máy chủ, lưu tệp, tạo tài liệu, đưa tác vụ ingest vào hàng đợi."""

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.domain import CurrentUser, DocumentStatus, UploadResult
from app.modules.audit import service as audit
from app.modules.documents import repository as documents
from app.modules.jobs import service as jobs
from app.ports.storage import StoragePort, new_file_key

CHUNK = 1024 * 1024
NAME_MAX = 255


async def _read_limited(file: UploadFile, limit: int) -> bytes | None:
    """Đọc theo khối 1 MB; None nếu vượt `limit` byte."""
    parts: list[bytes] = []
    total = 0
    while chunk := await file.read(CHUNK):
        total += len(chunk)
        if total > limit:
            return None
        parts.append(chunk)
    return b"".join(parts)


def _rejected(name: str, code: ErrorCode) -> UploadResult:
    return UploadResult(name=name, doc_id=None, status=None, error=code.value)


async def upload_documents(
    session: AsyncSession,
    storage: StoragePort,
    files: list[UploadFile],
    actor: CurrentUser,
    settings: Settings,
) -> list[UploadResult]:
    if not 1 <= len(files) <= settings.max_files:
        raise AppError(ErrorCode.FILE_TOO_MANY)
    limit = settings.max_upload_mb * 1024 * 1024
    results: list[UploadResult] = []
    saved_keys: list[str] = []
    try:
        for file in files:
            name = (file.filename or "")[:NAME_MAX]
            if not name.lower().endswith(".pdf"):
                results.append(_rejected(name, ErrorCode.FILE_NOT_PDF))
                continue
            data = await _read_limited(file, limit)
            if data is None:
                results.append(_rejected(name, ErrorCode.FILE_TOO_LARGE))
                continue
            if not data.startswith(b"%PDF-"):
                results.append(_rejected(name, ErrorCode.FILE_NOT_PDF))
                continue
            key = new_file_key()
            storage.save(key, data)
            saved_keys.append(key)
            doc = await documents.add(
                session,
                name=name,
                uploaded_by=actor.email,
                size_bytes=len(data),
                file_key=key,
            )
            await jobs.enqueue(session, "ingest", {"docId": str(doc.doc_id)})
            await audit.record(session, actor.email, "UPLOAD", doc.doc_id, name)
            results.append(
                UploadResult(
                    name=name, doc_id=doc.doc_id, status=DocumentStatus.PROCESSING, error=None
                )
            )
        await session.commit()
    except BaseException:
        await session.rollback()
        for key in saved_keys:
            storage.delete(key)
        raise
    return results
