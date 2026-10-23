import time

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Role
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document
from tests.integration.helpers import login

KEYS = {
    "docId", "name", "pageCount", "uploadedBy", "uploadedAt", "sizeBytes",
    "status", "failureReason", "usedOcr", "canDelete",
}  # fmt: skip


async def test_list_three_documents(client: httpx.AsyncClient, session: AsyncSession) -> None:
    for i in range(3):
        await make_document(session, name=f"{i}.pdf")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get("/api/v1/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3 and len(body["items"]) == 3
    assert all(set(item) == KEYS for item in body["items"])
    assert body["items"][0]["uploadedAt"].endswith("Z")


async def test_search_filters(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await make_document(session, name="Hợp đồng A.pdf")
    await make_document(session, name="Báo cáo.pdf")
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get("/api/v1/documents", params={"search": "hop dong"})
    assert [i["name"] for i in resp.json()["items"]] == ["Hợp đồng A.pdf"]


async def test_bad_sort_422(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get("/api/v1/documents", params={"sort": "size"})
    assert resp.status_code == 422
    assert resp.json() == {"code": "VALIDATION_ERROR", "retryable": False}


async def test_can_delete_flags(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await make_document(session, uploaded_by="minh@congty.vn")
    expected = {
        "minh@congty.vn": (Role.TEAM_LEAD, True),
        "hoa@congty.vn": (Role.TEAM_LEAD, False),
        "lan@congty.vn": (Role.BD_USER, False),
        "quantri@congty.vn": (Role.ADMIN, True),
    }
    for email, (role, can) in expected.items():
        await login(client, session, email, role)
        item = (await client.get("/api/v1/documents")).json()["items"][0]
        assert item["canDelete"] is can, email


async def test_deleted_documents_hidden(client: httpx.AsyncClient, session: AsyncSession) -> None:
    from datetime import UTC, datetime

    doc = await make_document(session)
    await repo.soft_delete(session, doc.doc_id, datetime.now(UTC))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert (await client.get("/api/v1/documents")).json()["total"] == 0


async def test_list_requires_auth(client: httpx.AsyncClient, session: AsyncSession) -> None:
    assert (await client.get("/api/v1/documents")).status_code == 401
    await login(client, session, "ntt@congty.vn", Role.SPONSOR)
    assert (await client.get("/api/v1/documents")).status_code == 403


async def test_list_500_perf(client: httpx.AsyncClient, session: AsyncSession) -> None:
    for i in range(500):
        await repo.add(
            session, name=f"tai-lieu-{i}.pdf", uploaded_by="m@x.vn", size_bytes=1, file_key=f"k{i}"
        )
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    started = time.perf_counter()
    resp = await client.get("/api/v1/documents")
    elapsed = time.perf_counter() - started
    assert resp.json()["total"] == 500
    assert elapsed <= 0.5, elapsed
