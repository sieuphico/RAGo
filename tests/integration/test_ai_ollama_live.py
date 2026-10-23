"""Chạy thật với Ollama: `make ai-up ai-pull` rồi `pytest -m ollama`."""

import time

import pytest

from app.adapters.ai_ollama import OllamaAi
from app.core.config import get_settings

pytestmark = pytest.mark.ollama


def _settings() -> OllamaAi:
    settings = get_settings().model_copy(update={"embedding_dim": 1024, "ai_timeout_s": 120})
    return OllamaAi(settings)


async def test_embed_live_dimension() -> None:
    ai = _settings()
    vectors = await ai.embed(["Hợp đồng có thời hạn 24 tháng", "contract term is 24 months"])
    assert len(vectors) == 2 and all(len(v) == 1024 for v in vectors)
    await ai.self_check()


async def test_embed_live_is_semantic() -> None:
    ai = _settings()
    a, b, c = await ai.embed(
        ["Thời hạn hợp đồng là hai năm", "Contract duration is two years", "Công thức nấu phở bò"]
    )

    def cos(x: list[float], y: list[float]) -> float:
        dot = sum(i * j for i, j in zip(x, y, strict=True))
        return float(dot / ((sum(i * i for i in x) ** 0.5) * (sum(j * j for j in y) ** 0.5)))

    assert cos(a, b) > cos(a, c)


async def test_generate_live_streams_with_citation() -> None:
    ai = _settings()
    started = time.monotonic()
    system = "Trả lời ngắn gọn bằng tiếng Việt, chỉ dựa vào ngữ cảnh. Trích nguồn bằng nhãn như [c1]."
    user = "[c1] Hợp đồng HD-2026-012 có thời hạn 24 tháng.\n\nCâu hỏi: Hợp đồng HD-2026-012 có thời hạn bao lâu?"
    tokens = [t async for t in ai.generate(system, user)]
    text = "".join(tokens)
    assert len(tokens) >= 1 and "24" in text, text
    assert "<think>" not in text
    print(f"\nQwen3 trả lời sau {time.monotonic() - started:.1f}s: {text!r}")
