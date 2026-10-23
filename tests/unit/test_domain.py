from dataclasses import FrozenInstanceError

import pytest

from app.domain import (
    DocumentStatus,
    FailureReason,
    InvalidTransition,
    MessageStatus,
    PageText,
    Role,
    assert_transition,
)

S = DocumentStatus


def test_enum_values_match_contract() -> None:
    assert {m.value for m in Role} == {"BD_USER", "TEAM_LEAD", "ADMIN", "SPONSOR"}
    assert {m.value for m in S} == {"PROCESSING", "OCR_PROCESSING", "READY", "FAILED", "DELETED"}
    assert len(FailureReason) == 4
    assert len(MessageStatus) == 7


# Bảng 2.1: 9 cặp giữa các trạng thái + tạo mới (None -> PROCESSING)
VALID = [
    (None, S.PROCESSING),
    (S.PROCESSING, S.OCR_PROCESSING),
    (S.PROCESSING, S.READY),
    (S.PROCESSING, S.FAILED),
    (S.PROCESSING, S.DELETED),
    (S.OCR_PROCESSING, S.READY),
    (S.OCR_PROCESSING, S.FAILED),
    (S.OCR_PROCESSING, S.DELETED),
    (S.READY, S.DELETED),
    (S.FAILED, S.DELETED),
]


def test_allowed_transitions() -> None:
    for old, new in VALID:
        assert_transition(old, new)


def test_all_other_transitions_rejected() -> None:
    for old in [None, *S]:
        for new in S:
            if (old, new) not in VALID:
                with pytest.raises(InvalidTransition):
                    assert_transition(old, new)


def test_invalid_transition_message() -> None:
    with pytest.raises(InvalidTransition, match="^READY -> PROCESSING$"):
        assert_transition(S.READY, S.PROCESSING)


def test_frozen_dataclass() -> None:
    page = PageText(1, "a", True)
    with pytest.raises(FrozenInstanceError):
        page.page = 2  # type: ignore[misc]
