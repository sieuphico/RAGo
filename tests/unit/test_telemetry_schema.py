import logging
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import CurrentUser, Role
from app.modules.telemetry import service
from app.modules.telemetry.schema import CLIENT_EVENTS, EVENTS
from app.modules.telemetry.service import anon_id, emit

Q, D = str(uuid4()), str(uuid4())

# Một mẫu hợp lệ cho mỗi sự kiện (CONTRACTS mục 6)
SAMPLES: dict[str, dict[str, Any]] = {
    "auth_login_succeeded": {"is_first_login": True},
    "auth_access_denied": {"reason": "revoked"},
    "onboarding_viewed": {"doc_count": 0},
    "document_upload_started": {"file_count": 3, "total_size_mb": 12.5},
    "document_upload_rejected": {"reason": "too_large"},
    "document_processing_completed": {"doc_id": D, "page_count": 12, "processing_seconds": 31.2},
    "document_processing_failed": {"doc_id": D, "reason": "encrypted", "used_ocr": False},
    "suggestion_clicked": {"suggestion_index": 2},
    "document_deleted": {"doc_id": D, "actor_role": "ADMIN"},
    "question_submitted": {"question_id": Q, "length_chars": 40, "language": "vi",
                           "is_followup": False, "scope_doc_count": 0},
    "answer_first_token": {"question_id": Q, "latency_ms": 900},
    "answer_completed": {"question_id": Q, "latency_ms": 6000, "citation_count": 2,
                         "distinct_doc_count": 2, "is_not_found": False},
    "question_failed": {"question_id": Q, "reason": "timeout"},
    "answer_stopped": {"question_id": Q, "elapsed_ms": 1500},
    "citation_clicked": {"question_id": Q, "doc_id": D, "page": 3},
    "answer_copied": {"question_id": Q},
    "answer_rated": {"question_id": Q, "rating": "down", "reason_code": "WRONG_INFO"},
    "summary_requested": {"doc_id": D, "latency_ms": 4000},
    "history_session_opened": {"session_age_days": 5},
}  # fmt: skip


def test_all_19_events_valid() -> None:
    assert len(EVENTS) == 19 and set(SAMPLES) == set(EVENTS)
    for name, props in SAMPLES.items():
        EVENTS[name].model_validate(props)


@pytest.mark.parametrize("name", sorted(EVENTS))
def test_unknown_field_rejected(name: str) -> None:
    with pytest.raises(ValidationError):
        EVENTS[name].model_validate({**SAMPLES[name], "text": "abc"})


def test_free_text_values_rejected() -> None:
    with pytest.raises(ValidationError):
        EVENTS["auth_access_denied"].model_validate({"reason": "email lan@x.vn bị chặn"})
    with pytest.raises(ValidationError):
        EVENTS["suggestion_clicked"].model_validate({"suggestion_index": 3})


def test_client_events_subset() -> None:
    assert CLIENT_EVENTS <= set(EVENTS)
    assert "answer_completed" not in CLIENT_EVENTS
    assert {"citation_clicked", "document_upload_rejected"} <= CLIENT_EVENTS


def test_anon_id_stable() -> None:
    secret = "s" * 32
    assert anon_id("Lan@x.vn", secret) == anon_id("lan@x.vn", secret)
    assert anon_id("minh@x.vn", secret) != anon_id("lan@x.vn", secret)
    assert "lan" not in anon_id("lan@x.vn", secret)


async def test_emit_failure_swallowed(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class FakeSession:
        def begin_nested(self) -> Any:
            raise RuntimeError("db down")

    async def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("db down")

    monkeypatch.setattr(service, "append_event", boom)
    user = CurrentUser("lan@x.vn", Role.BD_USER)
    session: AsyncSession = FakeSession()  # type: ignore[assignment]
    with caplog.at_level(logging.WARNING, logger="app.telemetry"):
        await emit(session, user, "sid", "answer_copied", question_id=Q)
    assert [r.levelno for r in caplog.records] == [logging.WARNING]
    assert "lan@x.vn" not in caplog.text
