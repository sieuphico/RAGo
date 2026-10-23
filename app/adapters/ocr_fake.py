from app.domain import OcrResult


class OcrFake:
    def __init__(self, confidence: float = 0.95, text: str = "Văn bản OCR trang {page}") -> None:
        self.confidence = confidence
        self.text = text
        self._page = 0

    async def recognize(self, image_png: bytes, lang: str = "vie+eng") -> OcrResult:
        self._page += 1
        return OcrResult(text=self.text.format(page=self._page), confidence=self.confidence)
