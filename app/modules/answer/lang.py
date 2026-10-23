"""Phát hiện ngôn ngữ câu hỏi, đủ dùng cho telemetry và cảnh báo ngôn ngữ (EC-12)."""

import re
from typing import Literal

_VI_CHARS = set(
    "ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ"
)
_EN_WORDS = {"the", "what", "is", "are", "of", "how", "which", "when", "who"}


def detect_lang(text: str) -> Literal["vi", "en", "other"]:
    lowered = text.lower()
    if any(ch in _VI_CHARS for ch in lowered):
        return "vi"
    letters = [ch for ch in lowered if ch.isalpha()]
    if letters:
        ascii_ratio = sum("a" <= ch <= "z" for ch in letters) / len(letters)
        words = set(re.findall(r"[a-z]+", lowered))
        if ascii_ratio >= 0.8 and words & _EN_WORDS:
            return "en"
    return "other"
