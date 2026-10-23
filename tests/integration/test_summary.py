import re
from datetime import UTC, datetime
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_gateway import AiGateway
from app.api.deps import get_gateway
from app.core.config import get_settings
from app.domain import ChunkDraft, DocumentStatus, Role
from app.modules.documents import repository as repo
from app.modules.summary.service import pick_evenly
from tests.fixtures.documents import make_document
from tests.integration.helpers import CSRF, SharedSession, login
from tests.integration.test_answer_service import Provider, unit


class Recording(Provider):
    def __init__(self, answer: str = "Ý 1 [c1].") -> None:
        super().__init__(answer)
        self.users: list[str] = []
        self.fail = False

    async def generate(self, system: str, user: str):  # type: ignore[no-untyped-def]
        self.users.append(user)
        if self.fail:
            from app.ports.ai import ProviderError

            raise ProviderError("down")
        async for token in super().generate(system, user):
            yield token


def _use(app: FastAPI, session: AsyncSession, provider: Provider) -> None:
    settings = get_settings()
    gateway = AiGateway(provider, settings, SharedSession(session))  # type: ignore[arg-type]
    app.dependency_overrides[get_gateway] = lambda: gateway


async def _doc(session: AsyncSession, chunks: int, status: DocumentStatus = DocumentStatus.READY) -> Any:
    doc = await make_document(session, name="HD_BAO_MAT.pdf", status=status)
    drafts = [ChunkDraft(page=i + 1, text=f"nội dung trang {i + 1}") for i in range(chunks)]
    await repo.add_chunks(session, doc.doc_id, drafts, [unit(i % 300) for i in range(chunks)])
    return doc.doc_id


def _url(doc_id: Any) -> str:
    return f"/api/v1/documents/{doc_id}/summary"


async def test_summary_has_citations(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    _use(app, session, Recording("Ý 1 [c1]."))
    doc_id = await _doc(session, 3)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.post(_url(doc_id), json={}, headers=CSRF)
    assert resp.status_code == 200
    body = resp.json()
    assert body["docName"] == "HD_BAO_MAT.pdf" and "[[1]]" in body["text"] and "[c1]" not in body["text"]
    assert body["citations"][0]["page"] == 1 and body["citations"][0]["index"] == 1
    event = (
        await session.execute(
            text("SELECT props FROM telemetry_event WHERE event = 'summary_requested'")
        )
    ).scalar_one()
    assert event["doc_id"] == str(doc_id) and event["latency_ms"] >= 0


async def test_summary_not_ready_rejected(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    _use(app, session, Recording())
    doc_id = await _doc(session, 1, DocumentStatus.PROCESSING)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.post(_url(doc_id), json={}, headers=CSRF)
    assert resp.status_code == 409 and resp.json()["code"] == "DOC_NOT_READY"


async def test_summary_deleted_404(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    _use(app, session, Recording())
    doc_id = await _doc(session, 1)
    await repo.soft_delete(session, doc_id, datetime.now(UTC))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.post(_url(doc_id), json={}, headers=CSRF)
    assert resp.status_code == 404 and resp.json()["code"] == "DOC_NOT_FOUND"


async def test_summary_chunk_limit(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    provider = Recording()
    _use(app, session, provider)
    doc_id = await _doc(session, 100)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert (await client.post(_url(doc_id), json={}, headers=CSRF)).status_code == 200
    labels = re.findall(r"^\[c(\d+)\]", provider.users[0], flags=re.MULTILINE)
    assert labels == [str(i) for i in range(1, 21)]
    assert "HD_BAO_MAT" not in provider.users[0]
    assert "trang 1)" in provider.users[0] and "trang 100)" in provider.users[0]


async def test_summary_ai_error(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    provider = Recording()
    provider.fail = True
    _use(app, session, provider)
    doc_id = await _doc(session, 2)
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.post(_url(doc_id), json={}, headers=CSRF)
    assert resp.status_code == 503 and resp.json() == {"code": "AI_UNAVAILABLE", "retryable": True}


async def test_summary_flag_off(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CWD_FEATURES", "history")
    get_settings.cache_clear()
    try:
        _use(app, session, Recording())
        doc_id = await _doc(session, 1)
        await login(client, session, "lan@congty.vn", Role.BD_USER)
        assert (await client.post(_url(doc_id), json={}, headers=CSRF)).status_code == 404
    finally:
        monkeypatch.delenv("CWD_FEATURES")
        get_settings.cache_clear()


def test_pick_evenly() -> None:
    assert pick_evenly(5) == [0, 1, 2, 3, 4]
    picked = pick_evenly(100)
    assert len(picked) == 20 and picked[0] == 0 and picked[-1] == 99
    assert picked == sorted(set(picked))
