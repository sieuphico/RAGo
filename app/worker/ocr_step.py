"""OCR cho trang không có lớp văn bản (US-013). Bộ nối OCR thật và dựng ảnh trang chờ T-004/T-010."""

import asyncio
from collections.abc import Callable

from app.domain import FailureReason, PageText
from app.ports.ocr import OcrPort
from app.worker.extract import ExtractError

Render = Callable[[bytes, int], bytes]  # (nội dung PDF, số trang) -> ảnh PNG


class OcrRenderUnavailable(RuntimeError):
    """Chưa có bộ dựng ảnh trang PDF (cần thư viện được duyệt, xem T-209)."""


def render_unavailable(pdf: bytes, page: int) -> bytes:
    raise OcrRenderUnavailable("chưa cấu hình bộ dựng ảnh trang")


async def ocr_pages(
    ocr: OcrPort,
    pdf: bytes,
    pages: list[PageText],
    threshold: float,
    *,
    render: Render = render_unavailable,
) -> tuple[list[PageText], float]:
    """OCR các trang `has_text_layer=False`; trung bình độ tin cậy < `threshold` → OCR_UNREADABLE."""
    confidences: list[float] = []
    result: list[PageText] = []
    for page in pages:
        if page.has_text_layer:
            result.append(page)
            continue
        image = await asyncio.to_thread(render, pdf, page.page)
        recognized = await ocr.recognize(image)
        confidences.append(recognized.confidence)
        result.append(PageText(page=page.page, text=recognized.text.strip(), has_text_layer=False))
    mean = sum(confidences) / len(confidences) if confidences else 1.0
    if confidences and mean < threshold:
        raise ExtractError(FailureReason.OCR_UNREADABLE)
    return result, mean
