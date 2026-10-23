"""API-06: tải PDF cho khung xem nguồn, hỗ trợ `Range` một khoảng (AD-07)."""

import asyncio
import re
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import SessionDep, StorageDep, require_roles
from app.core.errors import AppError, ErrorCode
from app.domain import Role
from app.modules.documents import repository as documents

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN))],
)

_RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")


def _unsatisfiable(size: int) -> Response:
    return Response(status_code=416, headers={"Content-Range": f"bytes */{size}"})


def _parse_range(header: str, size: int) -> tuple[int, int] | None:
    """Trả (start, end) bao gồm; None nếu không hợp lệ hoặc ngoài kích thước."""
    match = _RANGE.fullmatch(header.strip())
    if match is None:  # sai cú pháp hoặc nhiều khoảng
        return None
    first, last = match.groups()
    if first == "" and last == "":
        return None
    if first == "":  # bytes=-n: n byte cuối
        length = int(last)
        if length == 0:
            return None
        return max(size - length, 0), size - 1
    start = int(first)
    end = size - 1 if last == "" else min(int(last), size - 1)
    if start >= size or end < start:
        return None
    return start, end


@router.get("/documents/{doc_id}/file")
async def get_file(
    doc_id: UUID, request: Request, session: SessionDep, storage: StorageDep
) -> Response:
    doc = await documents.get(session, doc_id)
    if doc is None:
        raise AppError(ErrorCode.DOC_NOT_FOUND)
    size = await asyncio.to_thread(storage.size, doc.file_key)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Disposition": f"inline; filename*=UTF-8''{quote(doc.name)}",
        "Cache-Control": "private, max-age=0",
        "X-Content-Type-Options": "nosniff",
    }
    range_header = request.headers.get("range")
    if range_header is None:
        data = await asyncio.to_thread(storage.read, doc.file_key)
        return Response(data, media_type="application/pdf", headers=headers)
    parsed = _parse_range(range_header, size)
    if parsed is None:
        return _unsatisfiable(size)
    start, end = parsed
    data = await asyncio.to_thread(storage.read, doc.file_key, start, end + 1)
    headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    return Response(data, status_code=206, media_type="application/pdf", headers=headers)
