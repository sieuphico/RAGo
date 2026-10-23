"""Ngôn ngữ (T-309), câu hỏi nối tiếp (T-310) và phạm vi tài liệu (T-311) của AnswerService."""

from typing import Any
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.domain import (
    AnswerEvent,
    ChunkDraft,
    CitationEvent,
    DocumentStatus,
    DoneEvent,
    MessageStatus,
    StatusEvent,
)
from app.modules.answer.history import recent_turns
from app.modules.answer.scope import normalize_scope
from app.modules.answer.service import AnswerService
from app.modules.chat import repository as chat
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document
from tests.integration.test_answer_service import USER, Provider, _ready_doc, _service, unit


class Recording(Provider):
    """Ghi lại truy vấn nhúng và prompt gửi cho AI."""

    def __init__(self) -> None:
        super().__init__("Theo tài liệu [c1].")
        self.queries: list[str] = []
        self.systems: list[str] = []
        self.users: list[str] = []

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.queries += texts
        return await super().embed(texts)

    async def generate(self, system: str, user: str):  # type: ignore[no-untyped-def]
        self.systems.append(system)
        self.users.append(user)
        async for token in super().generate(system, user):
            yield token


def _settings(**features: bool) -> Settings:
    enabled = frozenset(name for name, on in features.items() if on)
    return get_settings().model_copy(update={"features": enabled})


async def _ask(
    service: AnswerService, session: AsyncSession, text: str, session_id: UUID | None = None,
    scope: set[UUID] | None = None,
) -> tuple[UUID, list[AnswerEvent]]:  # fmt: skip
    if session_id is None:
        session_id = (await chat.create_session(session, USER.email)).session_id
        await session.commit()
    events = [e async for e in service.ask(USER, "sid", session_id, text, scope or set())]
    return session_id, events


# ---- T-309
async def test_other_language_note(session: AsyncSession) -> None:
    await _ready_doc(session)
    provider = Recording()
    _, events = await _ask(_service(session, provider), session, "Was ist die Laufzeit?")
    done = events[-1]
    assert isinstance(done, DoneEvent) and done.notice == "LANG_UNSUPPORTED"
    assert provider.systems[0].endswith("Trả lời bằng tiếng Việt.")


async def test_english_question_gets_english_instruction_without_notice(
    session: AsyncSession,
) -> None:
    await _ready_doc(session)
    provider = Recording()
    _, events = await _ask(_service(session, provider), session, "What is the term?")
    done = events[-1]
    assert isinstance(done, DoneEvent) and done.notice is None
    assert provider.systems[0].endswith("Answer in English.")


# ---- T-310
async def test_followup_uses_previous_turn(session: AsyncSession) -> None:
    await _ready_doc(session)
    provider = Recording()
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, provider, _settings(followup=True), emitted)
    session_id, _ = await _ask(service, session, "Hợp đồng X là gì?")
    await _ask(service, session, "Còn giá trị của nó?", session_id)
    assert "Hợp đồng X" in provider.queries[-1] and "giá trị" in provider.queries[-1]
    assert "<history>" in provider.users[-1] and "Hợp đồng X là gì?" in provider.users[-1]
    flags = [p["is_followup"] for n, p in emitted if n == "question_submitted"]
    assert flags == [False, True]


async def test_no_cross_session_history(session: AsyncSession) -> None:
    await _ready_doc(session)
    provider = Recording()
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, provider, _settings(followup=True), emitted)
    await _ask(service, session, "Hợp đồng X là gì?")
    await _ask(service, session, "Còn giá trị của nó?")  # phiên mới
    assert "<history>" not in provider.users[-1] and "Hợp đồng X" not in provider.queries[-1]
    assert [p["is_followup"] for n, p in emitted if n == "question_submitted"] == [False, False]


async def test_followup_flag_off(session: AsyncSession) -> None:
    await _ready_doc(session)
    provider = Recording()
    emitted: list[tuple[str, dict[str, Any]]] = []
    service = _service(session, provider, _settings(followup=False), emitted)
    session_id, _ = await _ask(service, session, "Hợp đồng X là gì?")
    await _ask(service, session, "Còn giá trị của nó?", session_id)
    assert "<history>" not in provider.users[-1]
    assert provider.queries[-1] == "Còn giá trị của nó?"


async def test_recent_turns_limit_and_order(session: AsyncSession) -> None:
    session_id = (await chat.create_session(session, USER.email)).session_id
    for i in range(5):
        await chat.add_message(session, session_id, "user", f"hỏi {i}", MessageStatus.COMPLETED)
        await chat.add_message(session, session_id, "assistant", f"đáp {i}", MessageStatus.COMPLETED)
    # lượt đang chạy không được tính
    await chat.add_message(session, session_id, "user", "hỏi 5", MessageStatus.COMPLETED)
    await chat.add_message(session, session_id, "assistant", "", MessageStatus.SEARCHING)
    turns = await recent_turns(session, session_id)
    assert [(t.question, t.answer) for t in turns] == [("hỏi 2", "đáp 2"), ("hỏi 3", "đáp 3"), ("hỏi 4", "đáp 4")]


# ---- T-311
async def _doc(session: AsyncSession, name: str, vector: int = 0) -> UUID:
    doc = await make_document(session, name=name, status=DocumentStatus.READY)
    await repo.add_chunks(session, doc.doc_id, [ChunkDraft(page=1, text="noi dung chung")], [unit(vector)])
    await session.commit()
    return doc.doc_id


def _citations(events: list[AnswerEvent]) -> list[Any]:
    return [e.citation for e in events if isinstance(e, CitationEvent)]


async def test_scope_only_cites_selected(session: AsyncSession) -> None:
    a, _b = await _doc(session, "A.pdf"), await _doc(session, "B.pdf")
    service = _service(session, Recording(), _settings(scope=True))
    _, events = await _ask(service, session, "noi dung chung", scope={a})
    assert {c.doc_id for c in _citations(events)} == {a}


async def test_deleted_doc_removed_from_scope(session: AsyncSession) -> None:
    from datetime import UTC, datetime

    a, d = await _doc(session, "A.pdf"), await _doc(session, "D.pdf")
    await repo.soft_delete(session, d, datetime.now(UTC))
    await session.commit()
    service = _service(session, Recording(), _settings(scope=True))
    _, events = await _ask(service, session, "noi dung chung", scope={a, d})
    status = events[0]
    assert isinstance(status, StatusEvent) and status.scope_removed == [d]
    assert {c.doc_id for c in _citations(events)} == {a}


async def test_all_removed_falls_back(session: AsyncSession) -> None:
    from datetime import UTC, datetime

    a, d = await _doc(session, "A.pdf"), await _doc(session, "D.pdf")
    await repo.soft_delete(session, d, datetime.now(UTC))
    await session.commit()
    service = _service(session, Recording(), _settings(scope=True))
    _, events = await _ask(service, session, "noi dung chung", scope={d})
    status = events[0]
    assert isinstance(status, StatusEvent) and status.scope_removed == [d] and status.doc_count == 1
    assert {c.doc_id for c in _citations(events)} == {a}


async def test_flag_off_ignores_scope(session: AsyncSession) -> None:
    a, b = await _doc(session, "A.pdf"), await _doc(session, "B.pdf")
    provider = Recording()
    service = _service(session, provider, _settings(scope=False))
    _, events = await _ask(service, session, "noi dung chung", scope={a})
    status = events[0]
    assert isinstance(status, StatusEvent) and status.scope_removed == [] and status.doc_count == 2
    assert "[c1]" in provider.users[0] and "[c2]" in provider.users[0]  # cả hai tài liệu vào prompt


async def test_normalize_scope_unit(session: AsyncSession) -> None:
    a = await _doc(session, "A.pdf")
    assert (await normalize_scope(session, set())).effective == set()
    result = await normalize_scope(session, {a})
    assert result.effective == {a} and result.removed == set()


@pytest.mark.parametrize("flag", [True, False])
async def test_scope_saved_on_session(session: AsyncSession, flag: bool) -> None:
    a = await _doc(session, "A.pdf")
    service = _service(session, Recording(), _settings(scope=flag))
    session_id, _ = await _ask(service, session, "noi dung chung", scope={a})
    stored = await chat.get_session(session, USER.email, session_id)
    assert stored is not None and stored.scope_doc_ids == ([a] if flag else [])
