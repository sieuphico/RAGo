import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.domain import ScoredChunk
from app.modules.answer.lang import detect_lang
from app.modules.answer.prompt import SYSTEM_PROMPT, build_prompt

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "lang_questions.json"


def _chunks() -> list[ScoredChunk]:
    return [ScoredChunk(uuid4(), uuid4(), "a.pdf", 1, "nội dung", 0.1)]


def test_english_instruction() -> None:
    prompt = build_prompt("What is the term?", _chunks(), lang="en")
    assert prompt.system.endswith("Answer in English.")
    assert prompt.system.startswith(SYSTEM_PROMPT)


def test_other_language_note() -> None:
    prompt = build_prompt("Was ist die Laufzeit?", _chunks(), lang="other")
    assert prompt.system.endswith("Trả lời bằng tiếng Việt.")


def test_vietnamese_unchanged() -> None:
    chunks = _chunks()
    default = build_prompt("Thời hạn?", chunks)
    explicit = build_prompt("Thời hạn?", chunks, lang="vi")
    assert (default.system, default.user) == (explicit.system, explicit.user)
    assert default.system == SYSTEM_PROMPT


def test_lang_eval_fixture_is_balanced_and_detected() -> None:
    """Tệp sẵn để T-607 đo AC-026; ở đây kiểm tra bộ dò và lời nhắc cho từng câu."""
    questions = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert [q["lang"] for q in questions].count("vi") == 10
    assert [q["lang"] for q in questions].count("en") == 10
    for item in questions:
        lang = detect_lang(item["question"])
        assert lang == item["lang"], item["question"]
        system = build_prompt(item["question"], _chunks(), lang=lang).system
        assert system.endswith("Answer in English.") == (item["lang"] == "en")


@pytest.mark.parametrize("text", ["", "   ", "12345", "Was ist das?"])
def test_non_vi_en_is_other(text: str) -> None:
    assert detect_lang(text) == "other"
