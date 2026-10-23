from typing import Protocol

from app.domain import OcrResult


class OcrPort(Protocol):
    async def recognize(self, image_png: bytes, lang: str = "vie+eng") -> OcrResult: ...
