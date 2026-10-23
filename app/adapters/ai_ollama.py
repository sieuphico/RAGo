"""Bộ nối AI chạy nội bộ qua Ollama (AD-06): nhúng bằng /api/embed, sinh văn bản bằng /api/chat.

Dữ liệu không rời máy chủ. Chỉ gửi văn bản và tên mô hình; không gửi email, mã người dùng hay tên tệp.
"""

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.core.config import Settings
from app.ports.ai import ProviderError, ProviderTimeout

logger = logging.getLogger("app.ai.ollama")
TEMPERATURE = 0.1
MAX_TOKENS = 800
_OPEN, _CLOSE = "<think>", "</think>"


class _ThinkFilter:
    """Bỏ phần suy luận <think>…</think> của Qwen3 nếu mô hình vẫn xuất ra (thẻ có thể bị cắt giữa các khối)."""

    def __init__(self) -> None:
        self.buffer = ""
        self.in_think = False

    def feed(self, text: str) -> str:
        self.buffer += text
        out: list[str] = []
        while True:
            if self.in_think:
                end = self.buffer.find(_CLOSE)
                if end == -1:
                    self.buffer = self.buffer[-(len(_CLOSE) - 1) :]
                    break
                self.buffer = self.buffer[end + len(_CLOSE) :].lstrip("\n")
                self.in_think = False
                continue
            start = self.buffer.find(_OPEN)
            if start != -1:
                out.append(self.buffer[:start])
                self.buffer = self.buffer[start + len(_OPEN) :]
                self.in_think = True
                continue
            hold = next(
                (n for n in range(len(_OPEN) - 1, 0, -1) if self.buffer.endswith(_OPEN[:n])), 0
            )
            out.append(self.buffer[: len(self.buffer) - hold])
            self.buffer = self.buffer[len(self.buffer) - hold :]
            break
        return "".join(out)

    def flush(self) -> str:
        rest, self.buffer = ("" if self.in_think else self.buffer), ""
        return rest


class OllamaAi:
    def __init__(
        self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self.settings = settings
        self.chat_model = settings.ollama_chat_model
        self.embed_model = settings.ollama_embed_model
        self.client = httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=httpx.Timeout(connect=5, read=settings.ai_timeout_s, write=30, pool=5),
            transport=transport,
        )

    @staticmethod
    def _status_error(status: int) -> ProviderError:
        if status in (401, 403):
            logger.error("ai_auth_failed status=%d", status)  # không kèm khóa
        return ProviderError(f"HTTP {status}")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        size = self.settings.embed_batch_size
        for start in range(0, len(texts), size):
            batch = texts[start : start + size]
            body = {"model": self.embed_model, "input": batch}
            try:
                resp = await self.client.post("/api/embed", json=body)
            except httpx.TimeoutException as exc:
                raise ProviderTimeout("embed timeout") from exc
            except httpx.HTTPError as exc:
                raise ProviderError("embed network error") from exc
            if resp.status_code != 200:
                raise self._status_error(resp.status_code)
            try:
                data: list[list[float]] = resp.json()["embeddings"]
            except (ValueError, KeyError, TypeError) as exc:
                raise ProviderError("embed bad response") from exc
            if len(data) != len(batch):
                raise ProviderError("embed count mismatch")
            vectors.extend(data)
        return vectors

    async def generate(self, system: str, user: str) -> AsyncGenerator[str]:
        body: dict[str, Any] = {
            "model": self.chat_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": True,
            "think": False,
            "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS},
        }
        think = _ThinkFilter()
        try:
            async with self.client.stream("POST", "/api/chat", json=body) as resp:
                if resp.status_code != 200:
                    await resp.aread()
                    raise self._status_error(resp.status_code)
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except ValueError as exc:
                        raise ProviderError("generate bad stream") from exc
                    if "error" in data:
                        raise ProviderError("generate provider error")
                    piece = think.feed(data.get("message", {}).get("content", ""))
                    if piece:
                        yield piece
                    if data.get("done"):
                        break
        except httpx.TimeoutException as exc:
            raise ProviderTimeout("generate timeout") from exc
        except httpx.HTTPError as exc:  # gồm lỗi mạng giữa luồng
            raise ProviderError("generate network error") from exc
        tail = think.flush()
        if tail:
            yield tail

    async def self_check(self) -> None:
        """Khởi động: nhúng một chuỗi và kiểm số chiều; sai thì dừng tiến trình sớm."""
        vector = (await self.embed(["kiểm tra"]))[0]
        if len(vector) != self.settings.embedding_dim:
            raise RuntimeError(
                f"embedding_dim={self.settings.embedding_dim} nhưng mô hình "
                f"{self.embed_model} trả {len(vector)} chiều"
            )

    async def aclose(self) -> None:
        await self.client.aclose()
