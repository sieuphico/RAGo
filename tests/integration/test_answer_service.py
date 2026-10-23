import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai_gateway import AiGateway
from app.core.config import Settings, get_settings
from app.domain import (
    AnswerEvent,
    ChunkDraft,
    CitationEvent,
    CurrentUser,
    DocumentStatus,
    DoneEvent,
    MessageStatus,
    Role,
    StatusEvent,
    TokenEvent,
)
from app.modules.answer.lang import detect_lang
from app.modules.answer.service import AnswerService
from app.modules.chat import repository as chat
from app.modules.documents import repository as repo
from tests.fixtures.documents import make_document
from tests.integration.helpers import SharedSession

DIM = 384
USER = CurrentUser("lan@congty.vn", Role.BD_USER)


def unit(i: int) -> list[float]:
    v = [0.0] * DIM
    v[i] = 1.0
    return v


class Provider:
    """Nhà cung cấp thử: nhúng cố định, sinh văn bản theo kịch bản, đếm lời gọi."""

    def __init__(self, answer: str = "Theo tài liệu [c1].", embed_delay: float = 0.0) -> None:
        self.answer, self.embed_delay = answer, embed_delay
        self.embed_calls = 0
        self.generate_calls = 0

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.embed_calls += 1
        if self.embed_delay:
            await asyncio.sleep(self.embed_delay)
        return [unit(0) for _ in texts]

    async def generate(self, system: str, user: str) -> AsyncIterator[str]:
        self.generate_calls += 1
        for word in self.answer.split(" "):
            yield word + " "


def _service(
    session: AsyncSession, provider: Provider, settings: Settings | None = None,
    emitted: list[tuple[str, dict[str, Any]]] | None = None,
) -> AnswerService:  # fmt: skip
    settings = settings or get_settings()
    factory = SharedSession(session)
    gateway = AiGateway(provider, settings, factory)  # type: ignore[arg-type]

    async def emit(user: CurrentUser, sid: str, event: str, props: dict[str, Any]) -> None:
        if emitted is not None:
            emitted.append((event, props))

    return AnswerService(factory, gateway, settings, emit)  # type: ignore[arg-type]


async def _ready_doc(session: AsyncSession, text: str = "thời hạn 24 tháng") -> None:
    doc = await make_document(session, name="HD_ABC_2026.pdf", status=DocumentStatus.READY)
    await repo.add_chunks(session, doc.doc_id, [ChunkDraft(page=12, text=text)], [unit(0)])
    await session.commit()


async def _ask(service: AnswerService, session: AsyncSession, text: str = "Thời hạn bao lâu?",
               scope: set[Any] | None = None) -> list[AnswerEvent]:  # fmt: skip
    chat_session = await chat.create_session(session, USER.email)
    await session.commit()
    return [e async for e in service.ask(USER, "sid-1", chat_session.session_id, text, scope or set())]


async def test_answer_has_citations(session: AsyncSession) -> None:
    await _ready_doc(session)
    events = await _ask(_service(session, Provider("Theo tài liệu [c1].")), session)
    kinds = [type(e).__name__ for e in events]
    assert kinds[0] == "StatusEvent" and kinds[-1] == "DoneEvent"
    citations = [e for e in events if isinstance(e, CitationEvent)]
    assert [(c.citation.index, c.citation.page, c.citation.doc_name) for c in citations] == [
        (1, 12, "HD_ABC_2026.pdf")
    ]
    tokens = "".join(e.text for e in events if isinstance(e, TokenEvent))
    assert "[[1]]" in tokens and "[c1]" not in tokens
    # trích dẫn đến trước token chứa [[1]] đầu tiên
    first_cite = next(i for i, e in enumerate(events) if isinstance(e, CitationEvent))
    first_ref = next(i for i, e in enumerate(events) if isinstance(e, TokenEvent) and "[[1]]" in e.text)
    assert first_cite < first_ref
    done = events[-1]
    assert isinstance(done, DoneEvent) and (done.citation_count, done.is_not_found) == (1, False)
    session_id = (await chat.list_sessions(session, USER.email, _epoch()))[0].session_id
    stored = await chat.get_session(session, USER.email, session_id)
    assert stored is not None
    answer = next(m for m in stored.messages if m.role == "assistant")
    assert answer.status == MessageStatus.COMPLETED and len(answer.citations) == 1
    assert "[[1]]" in answer.text and stored.title == "Thời hạn bao lâu?"


def _epoch() -> Any:
    from datetime import UTC, datetime

    return datetime(2000, 1, 1, tzinfo=UTC)


async def test_no_ready_docs_skips_ai(session: AsyncSession) -> None:
    provider = Provider()
    events = await _ask(_service(session, provider), session)
    done = events[-1]
    assert isinstance(done, DoneEvent)
    assert done.is_not_found and done.not_found_reason == "NO_READY_DOCS"
    assert provider.embed_calls == 0 and provider.generate_calls == 0
    assert isinstance(events[0], StatusEvent) and events[0].doc_count == 0


async def test_not_found_skips_generate(session: AsyncSession) -> None:
    await _ready_doc(session)
    settings = get_settings().model_copy(update={"relevance_threshold": 0.99})

    class Orthogonal(Provider):
        async def embed(self, texts: list[str]) -> list[list[float]]:
            self.embed_calls += 1
            return [unit(5) for _ in texts]  # vuông góc với chunk, không có từ khóa chung

    provider = Orthogonal()
    events = await _ask(_service(session, provider, settings), session, text="xyzzy plugh")
    done = events[-1]
    assert isinstance(done, DoneEvent) and done.not_found_reason == "NO_EVIDENCE"
    assert provider.generate_calls == 0 and provider.embed_calls == 1


async def test_status_first_and_fast(session: AsyncSession) -> None:
    await _ready_doc(session)
    service = _service(session, Provider(embed_delay=3))
    chat_session = await chat.create_session(session, USER.email)
    await session.commit()
    stream = service.ask(USER, "sid", chat_session.session_id, "Thời hạn bao lâu?", set())
    started = time.monotonic()
    first = await anext(stream)
    assert isinstance(first, StatusEvent) and first.doc_count == 1
    assert time.monotonic() - started <= 1
    await stream.aclose()


async def test_model_says_not_found(session: AsyncSession) -> None:
    await _ready_doc(session)
    provider = Provider("Không tìm thấy thông tin này trong các tài liệu hiện có.")
    events = await _ask(_service(session, provider), session)
    done = events[-1]
    assert isinstance(done, DoneEvent) and done.is_not_found and done.citation_count == 0
    session_id = (await chat.list_sessions(session, USER.email, _epoch()))[0].session_id
    stored = await chat.get_session(session, USER.email, session_id)
    assert stored is not None
    assert next(m for m in stored.messages if m.role == "assistant").status == MessageStatus.NOT_FOUND


def test_detect_lang() -> None:
    assert detect_lang("Thời hạn hợp đồng?") == "vi"
    assert detect_lang("What is the term?") == "en"
    assert detect_lang("Was ist das?") == "other"
    assert detect_lang("") == "other"


async def test_telemetry_events(session: AsyncSession) -> None:
    await _ready_doc(session)
    emitted: list[tuple[str, dict[str, Any]]] = []
    events = await _ask(_service(session, Provider(), emitted=emitted), session, "Thời hạn bao lâu?")
    assert [name for name, _ in emitted] == [
        "question_submitted", "answer_first_token", "answer_completed",
    ]  # fmt: skip
    done = events[-1]
    assert isinstance(done, DoneEvent)
    assert {props["question_id"] for _, props in emitted} == {str(done.message_id)}
    flat = repr(emitted)
    assert "Thời hạn bao lâu" not in flat  # không có văn bản câu hỏi
    assert emitted[0][1]["language"] == "vi" and emitted[0][1]["length_chars"] == 17
    assert emitted[2][1]["citation_count"] == 1 and emitted[2][1]["distinct_doc_count"] == 1


async def test_scope_limits_retrieval(session: AsyncSession) -> None:
    await _ready_doc(session)
    other = await make_document(session, name="Khac.pdf", status=DocumentStatus.READY)
    await repo.add_chunks(session, other.doc_id, [ChunkDraft(page=1, text="noi dung khac")], [unit(0)])
    await session.commit()
    only_other = other.doc_id
    events = await _ask(_service(session, Provider()), session, scope={only_other})
    citation = next(e for e in events if isinstance(e, CitationEvent))
    assert citation.citation.doc_name == "Khac.pdf"

