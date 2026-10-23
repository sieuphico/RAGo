from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage_fs import FsStorage
from app.api.deps import get_storage
from app.domain import Role
from app.modules.documents import repository as repo
from app.ports.storage import new_file_key
from tests.fixtures.documents import make_document
from tests.integration.helpers import login

DATA = bytes(range(250)) * 4  # 1.000 byte


@pytest.fixture
async def doc_id(app: FastAPI, session: AsyncSession, tmp_path: Path) -> str:
    storage = FsStorage(tmp_path)
    app.dependency_overrides[get_storage] = lambda: storage
    key = new_file_key()
    storage.save(key, DATA)
    doc = await make_document(session, name="Hợp đồng ABC.pdf", file_key=key)
    return str(doc.doc_id)


async def test_file_requires_auth(client: httpx.AsyncClient, session: AsyncSession, doc_id: str) -> None:
    assert (await client.get(f"/api/v1/documents/{doc_id}/file")).status_code == 401
    await login(client, session, "ntt@congty.vn", Role.SPONSOR)
    assert (await client.get(f"/api/v1/documents/{doc_id}/file")).status_code == 403


async def test_full_file_200(client: httpx.AsyncClient, session: AsyncSession, doc_id: str) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(f"/api/v1/documents/{doc_id}/file")
    assert resp.status_code == 200
    assert resp.content == DATA
    assert resp.headers["content-length"] == "1000"
    assert resp.headers["accept-ranges"] == "bytes"
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["cache-control"] == "private, max-age=0"
    assert resp.headers["content-disposition"].startswith("inline; filename*=UTF-8''H%E1%BB%A3p")


async def test_range_request_206(client: httpx.AsyncClient, session: AsyncSession, doc_id: str) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(f"/api/v1/documents/{doc_id}/file", headers={"Range": "bytes=0-99"})
    assert resp.status_code == 206
    assert resp.content == DATA[:100]
    assert resp.headers["content-range"] == "bytes 0-99/1000"


async def test_open_ended_range(client: httpx.AsyncClient, session: AsyncSession, doc_id: str) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(f"/api/v1/documents/{doc_id}/file", headers={"Range": "bytes=900-"})
    assert resp.status_code == 206 and resp.content == DATA[900:]
    assert resp.headers["content-range"] == "bytes 900-999/1000"


async def test_suffix_and_clipped_range(
    client: httpx.AsyncClient, session: AsyncSession, doc_id: str
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    suffix = await client.get(f"/api/v1/documents/{doc_id}/file", headers={"Range": "bytes=-10"})
    assert suffix.status_code == 206 and suffix.content == DATA[-10:]
    clipped = await client.get(f"/api/v1/documents/{doc_id}/file", headers={"Range": "bytes=990-5000"})
    assert clipped.status_code == 206 and clipped.headers["content-range"] == "bytes 990-999/1000"


@pytest.mark.parametrize("value", ["bytes=2000-3000", "bytes=0-1,5-9", "bytes=abc", "bytes=-"])
async def test_bad_range_416(
    client: httpx.AsyncClient, session: AsyncSession, doc_id: str, value: str
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(f"/api/v1/documents/{doc_id}/file", headers={"Range": value})
    assert resp.status_code == 416
    assert resp.headers["content-range"] == "bytes */1000"


async def test_deleted_file_404(client: httpx.AsyncClient, session: AsyncSession, doc_id: str) -> None:
    from uuid import UUID

    await repo.soft_delete(session, UUID(doc_id), datetime.now(UTC))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get(f"/api/v1/documents/{doc_id}/file")
    assert resp.status_code == 404
    assert resp.json() == {"code": "DOC_NOT_FOUND", "retryable": False}
