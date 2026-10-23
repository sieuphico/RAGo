from collections.abc import AsyncIterator
from typing import Protocol


class ProviderError(Exception):
    pass


class ProviderTimeout(ProviderError):
    pass


class AiPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

    def generate(self, system: str, user: str) -> AsyncIterator[str]: ...
