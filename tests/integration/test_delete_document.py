from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import DocumentStatus, Role
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document
from tests.integration.helpers import CSRF, login


async def _scalar(session: AsyncSession, sql: str) -> object:
    return (await session.execute(text(sql))).scalar_one()


async def test_owner_can_delete(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn", status=DocumentStatus.READY)
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    before = datetime.now(UTC)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert resp.status_code == 200
    assert resp.json() == {"docId": str(doc.doc_id), "alreadyDeleted": False}
    assert await _scalar(session, "SELECT deleted_at FROM document") is not None
    run_after = await _scalar(session, "SELECT run_after FROM job WHERE type = 'purge'")
    assert isinstance(run_after, datetime)
    assert timedelta(minutes=4) < run_after - before < timedelta(minutes=6)
    assert await _scalar(session, "SELECT count(*) FROM audit_log WHERE action = 'DELETE'") == 1


async def test_other_team_lead_forbidden(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn")
    await login(client, session, "hoa@congty.vn", Role.TEAM_LEAD)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert resp.status_code == 403
    assert resp.json()["code"] == "AUTH_FORBIDDEN"
    assert await _scalar(session, "SELECT deleted_at FROM document") is None


async def test_bd_user_forbidden(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert resp.status_code == 403


async def test_admin_can_delete_any(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn")
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert resp.status_code == 200


async def test_double_delete_idempotent(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn")
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert resp.status_code == 200 and resp.json()["alreadyDeleted"] is True
    assert await _scalar(session, "SELECT count(*) FROM audit_log WHERE action = 'DELETE'") == 1
    assert await _scalar(session, "SELECT count(*) FROM job WHERE type = 'purge'") == 1


async def test_unknown_doc_404(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    resp = await client.delete(f"/api/v1/documents/{uuid4()}", headers=CSRF)
    assert resp.status_code == 404
    assert resp.json()["code"] == "DOC_NOT_FOUND"


async def test_deleted_not_ready(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn", status=DocumentStatus.READY)
    assert await repo.ready_doc_ids(session) == {doc.doc_id}
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    await client.delete(f"/api/v1/documents/{doc.doc_id}", headers=CSRF)
    assert await repo.ready_doc_ids(session) == set()


async def test_csrf_required(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc = await make_document(session, uploaded_by="minh@congty.vn")
    await login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.delete(f"/api/v1/documents/{doc.doc_id}")
    assert resp.status_code == 403 and resp.json()["code"] == "CSRF_REJECTED"
