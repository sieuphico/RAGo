from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.storage_fs import FsStorage
from app.api.deps import get_storage
from app.domain import Role
from app.modules.users import repository as users
from tests.fixtures.pdfs import MB, PNG_BYTES, minimal_pdf

CSRF = {"X-Requested-With": "cwd"}


@pytest.fixture
def storage_root(app: FastAPI, tmp_path: Path) -> Path:
    app.dependency_overrides[get_storage] = lambda: FsStorage(tmp_path)
    return tmp_path


async def _login(client: httpx.AsyncClient, session: AsyncSession, email: str, role: Role) -> None:
    await users.add(session, email, role, "root")
    resp = await client.get("/auth/login", params={"login_hint": email})
    await client.get(resp.headers["location"].removeprefix("https://test"))


def _files(*items: tuple[str, bytes]) -> list[tuple[str, tuple[str, bytes, str]]]:
    return [("files", (name, data, "application/octet-stream")) for name, data in items]


async def _count(session: AsyncSession, table: str) -> int:
    return int((await session.execute(text(f"SELECT count(*) FROM {table}"))).scalar_one())


def _stored(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.pdf")]


async def test_upload_valid_pdf_202(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents", files=_files(("text_1p.pdf", minimal_pdf())), headers=CSRF
    )
    assert resp.status_code == 202
    result = resp.json()["results"][0]
    assert result["status"] == "PROCESSING" and result["error"] is None
    jobs = (await session.execute(text("SELECT type, payload FROM job"))).all()
    assert [(j[0], j[1]) for j in jobs] == [("ingest", {"docId": result["docId"]})]
    audit = (await session.execute(text("SELECT actor, action FROM audit_log"))).all()
    assert [tuple(a) for a in audit] == [("minh@congty.vn", "UPLOAD")]
    assert len(_stored(storage_root)) == 1


async def test_reject_non_pdf_extension(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents",
        files=_files(("a.docx", minimal_pdf()), ("b.png", PNG_BYTES)),
        headers=CSRF,
    )
    assert resp.status_code == 202
    assert [r["error"] for r in resp.json()["results"]] == ["FILE_NOT_PDF", "FILE_NOT_PDF"]
    assert await _count(session, "document") == 0
    assert _stored(storage_root) == []


async def test_reject_non_pdf_magic(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents", files=_files(("not_pdf.pdf", PNG_BYTES)), headers=CSRF
    )
    assert resp.json()["results"][0]["error"] == "FILE_NOT_PDF"
    assert await _count(session, "document") == 0


async def test_reject_oversize(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents",
        files=_files(("big_51mb.pdf", minimal_pdf(51 * MB)), ("ok_49mb.pdf", minimal_pdf(49 * MB))),
        headers=CSRF,
    )
    results = resp.json()["results"]
    assert results[0]["error"] == "FILE_TOO_LARGE"
    assert results[1]["status"] == "PROCESSING"
    assert await _count(session, "document") == 1


async def test_too_many_files(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    files = _files(*[(f"{i}.pdf", minimal_pdf()) for i in range(11)])
    resp = await client.post("/api/v1/documents", files=files, headers=CSRF)
    assert resp.status_code == 400
    assert resp.json() == {"code": "FILE_TOO_MANY", "retryable": False}
    assert await _count(session, "document") == 0
    assert _stored(storage_root) == []


async def test_no_files_is_too_many(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post("/api/v1/documents", headers=CSRF)
    assert resp.status_code == 400
    assert resp.json()["code"] == "FILE_TOO_MANY"


async def test_batch_partial_valid(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents",
        files=_files(("text_1p.pdf", minimal_pdf()), ("a.png", PNG_BYTES),
                     ("text_12p.pdf", minimal_pdf())),
        headers=CSRF,
    )  # fmt: skip
    results = resp.json()["results"]
    assert [r["name"] for r in results] == ["text_1p.pdf", "a.png", "text_12p.pdf"]
    assert [r["status"] for r in results] == ["PROCESSING", None, "PROCESSING"]
    assert results[1]["error"] == "FILE_NOT_PDF"
    assert await _count(session, "document") == 2
    assert await _count(session, "job") == 2
    assert await _count(session, "audit_log") == 2


async def test_non_team_lead_forbidden(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    for email, role in (("lan@congty.vn", Role.BD_USER), ("qt@congty.vn", Role.ADMIN)):
        client.cookies.clear()
        await _login(client, session, email, role)
        resp = await client.post(
            "/api/v1/documents", files=_files(("text_1p.pdf", minimal_pdf())), headers=CSRF
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == "AUTH_FORBIDDEN"
    assert await _count(session, "document") == 0


async def test_name_is_not_used_as_path(
    client: httpx.AsyncClient, session: AsyncSession, storage_root: Path
) -> None:
    await _login(client, session, "minh@congty.vn", Role.TEAM_LEAD)
    resp = await client.post(
        "/api/v1/documents", files=_files(("..\\..\\evil.pdf", minimal_pdf())), headers=CSRF
    )
    assert resp.status_code == 202
    assert all(storage_root in p.parents for p in _stored(storage_root))
    name = (await session.execute(text("SELECT name FROM document"))).scalar_one()
    assert name.endswith("evil.pdf")
