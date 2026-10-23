import asyncio
import hashlib
import math
import random
import re
from collections.abc import AsyncIterator
from typing import Literal

from app.ports.ai import ProviderError, ProviderTimeout

_LABEL = re.compile(r"\[c\d+\]")


class AiFake:
    def __init__(
        self,
        dim: int,
        fail_mode: Literal["error", "timeout"] | None = None,
        delay_s: float = 0,
    ) -> None:
        self.dim = dim
        self.fail_mode = fail_mode
        self.delay_s = delay_s

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._vector(t) for t in texts]

    def _vector(self, text: str) -> list[float]:
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest(), "big")
        rng = random.Random(seed)
        vec = [rng.uniform(-1, 1) for _ in range(self.dim)]
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec]

    async def generate(self, system: str, user: str) -> AsyncIterator[str]:
        label = _LABEL.search(user)
        tokens = ["Theo ", "tài liệu "] + ([label.group()] if label else []) + ["."]
        for token in tokens:
            if self.delay_s:
                await asyncio.sleep(self.delay_s)
            if self.fail_mode == "error":
                raise ProviderError("fake error")
            if self.fail_mode == "timeout":
                raise ProviderTimeout("fake timeout")
            yield token
