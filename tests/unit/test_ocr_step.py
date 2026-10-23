import pytest

from app.adapters.ocr_fake import OcrFake
from app.domain import FailureReason, OcrResult, PageText
from app.worker.extract import ExtractError
from app.worker.ocr_step import OcrRenderUnavailable, ocr_pages


def _png(pdf: bytes, page: int) -> bytes:
    return b"png"


class _Counting(OcrFake):
    def __init__(self, confidences: list[float]) -> None:
        super().__init__()
        self.confidences = confidences
        self.calls = 0

    async def recognize(self, image_png: bytes, lang: str = "vie+eng") -> OcrResult:
        value = self.confidences[self.calls]
        self.calls += 1
        return OcrResult(text=f"ocr {self.calls}", confidence=value)


async def test_ocr_only_scanned_pages() -> None:
    ocr = _Counting([0.95])
    pages = [PageText(1, "van ban 1", True), PageText(2, "", False), PageText(3, "van ban 3", True)]
    result, _ = await ocr_pages(ocr, b"pdf", pages, 0.8, render=_png)
    assert ocr.calls == 1
    assert [p.text for p in result] == ["van ban 1", "ocr 1", "van ban 3"]


async def test_below_threshold_failed() -> None:
    with pytest.raises(ExtractError) as info:
        await ocr_pages(
            OcrFake(confidence=0.5), b"pdf", [PageText(1, "", False)], 0.8, render=_png
        )
    assert info.value.reason == FailureReason.OCR_UNREADABLE


async def test_returns_mean_confidence() -> None:
    pages = [PageText(1, "", False), PageText(2, "", False)]
    _, mean = await ocr_pages(_Counting([0.9, 0.8]), b"pdf", pages, 0.8, render=_png)
    assert mean == pytest.approx(0.85)


async def test_no_scanned_pages_is_noop() -> None:
    ocr = _Counting([])
    pages = [PageText(1, "van ban", True)]
    result, mean = await ocr_pages(ocr, b"pdf", pages, 0.8, render=_png)
    assert result == pages and ocr.calls == 0 and mean == 1.0


async def test_default_renderer_is_unavailable() -> None:
    with pytest.raises(OcrRenderUnavailable):
        await ocr_pages(OcrFake(), b"pdf", [PageText(1, "", False)], 0.8)
