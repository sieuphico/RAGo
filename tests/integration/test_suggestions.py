import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_gateway import AiGateway
from app.core.config import Settings, get_settings
from app.domain import ChunkDraft, DocumentStatus, Job, Role
from app.modules.documents import repository as repo
from app.worker import suggest
from app.worker.suggest import SuggestDeps, generate_suggestions, parse_questions, pick_positions
from tests.fixtures.documents import make_document
from tests.integration.helpers import SharedSession, login
from tests.integration.test_answer_service import Provider, unit

QUESTIONS = ["Câu 1?", "Câu 2?", "Câu 3?"]


class Counting(Provider):
    def __init__(self, answer: str) -> None:
        super().__init__(answer)
        self.users: list[str] = []

    async def generate(self, system: str, user: str):  # type: ignore[no-untyped-def]
        self.users.append(user)
        async for token in super().generate(system, user):
            yield token


def _deps(session: AsyncSession, provider: Provider, settings: Settings | None = None) -> SuggestDeps:
    settings = settings or get_settings()
    factory = SharedSession(session)
    return SuggestDeps(factory, AiGateway(provider, settings, factory), settings)  # type: ignore[arg-type]


async def _ready(session: AsyncSession, chunks: int = 6) -> Any:
    doc = await make_document(session, name="HD_BAO_MAT.pdf", status=DocumentStatus.READY)
    drafts = [ChunkDraft(page=i + 1, text=f"đoạn số {i}") for i in range(chunks)]
    await repo.add_chunks(session, doc.doc_id, drafts, [unit(i) for i in range(chunks)])
    await session.commit()
    return doc.doc_id


def _job(doc_id: Any) -> Job:
    return Job(uuid4(), "suggest", {"docId": str(doc_id)}, 1)


async def test_three_suggestions(
    app: FastAPI, client: httpx.AsyncClient, session: AsyncSession
) -> None:
    doc_id = await _ready(session)
    await generate_suggestions(_job(doc_id), _deps(session, Counting(json.dumps(QUESTIONS))))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    resp = await client.get("/api/v1/suggestions")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3 and {i["text"] for i in items} == set(QUESTIONS)
    assert all(i["docId"] == str(doc_id) for i in items)


async def test_empty_when_no_ready(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert (await client.get("/api/v1/suggestions")).json() == {"items": []}


async def test_generated_once_and_no_filename_sent(session: AsyncSession) -> None:
    doc_id = await _ready(session)
    provider = Counting(json.dumps(QUESTIONS))
    deps = _deps(session, provider)
    await generate_suggestions(_job(doc_id), deps)
    await generate_suggestions(_job(doc_id), deps)
    assert len(provider.users) == 1
    assert "HD_BAO_MAT" not in provider.users[0] and "đoạn số 0" in provider.users[0]


async def test_fenced_json_accepted(session: AsyncSession) -> None:
    doc_id = await _ready(session)
    fenced = "```json\n" + json.dumps(QUESTIONS) + "\n```"
    await generate_suggestions(_job(doc_id), _deps(session, Counting(fenced)))
    stored = (await session.execute(text("SELECT questions FROM suggestion"))).scalar_one()
    assert stored == QUESTIONS


BAD_OUTPUTS = [
    "Đây là gợi ý",
    json.dumps(["một", "hai"]),
    json.dumps(["a", "b", ""]),
    json.dumps(["x" * 151, "b", "c"]),
    json.dumps({"q": 1}),
]


@pytest.mark.parametrize("bad", BAD_OUTPUTS)
async def test_invalid_output_raises_for_retry(session: AsyncSession, bad: str) -> None:
    doc_id = await _ready(session)
    with pytest.raises(ValueError):
        await generate_suggestions(_job(doc_id), _deps(session, Counting(bad)))
    assert (await session.execute(text("SELECT count(*) FROM suggestion"))).scalar_one() == 0


async def test_deleted_doc_excluded(client: httpx.AsyncClient, session: AsyncSession) -> None:
    doc_id = await _ready(session)
    await generate_suggestions(_job(doc_id), _deps(session, Counting(json.dumps(QUESTIONS))))
    await repo.soft_delete(session, doc_id, datetime.now(UTC))
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    assert (await client.get("/api/v1/suggestions")).json() == {"items": []}


async def test_flag_off(
    client: httpx.AsyncClient, session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CWD_FEATURES", "history")
    get_settings.cache_clear()
    try:
        doc_id = await _ready(session)
        provider = Counting(json.dumps(QUESTIONS))
        await generate_suggestions(_job(doc_id), _deps(session, provider, get_settings()))
        assert provider.users == []
        await login(client, session, "lan@congty.vn", Role.BD_USER)
        assert (await client.get("/api/v1/suggestions")).status_code == 404
    finally:
        monkeypatch.delenv("CWD_FEATURES")
        get_settings.cache_clear()


def test_helpers() -> None:
    assert pick_positions(1) == [0] and pick_positions(0) == []
    assert pick_positions(4) == [0, 1, 2, 3] and pick_positions(100) == [0, 25, 50, 75]
    assert parse_questions('["a ", " b", "c"]') == ["a", "b", "c"]
    assert suggest.SYSTEM.startswith("Đề xuất đúng 3 câu hỏi")
