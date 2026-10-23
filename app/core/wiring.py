"""Chọn bộ nối (giả hay thật). Chỉ file này được nhập app.adapters."""

from app.adapters.ai_fake import AiFake
from app.adapters.idp_fake import IdpFake
from app.adapters.ocr_fake import OcrFake
from app.adapters.storage_fs import FsStorage
from app.core.config import Settings
from app.ports.ai import AiPort
from app.ports.idp import IdpPort
from app.ports.ocr import OcrPort
from app.ports.storage import StoragePort
from app.worker.ocr_step import Render


def build_ai(settings: Settings) -> AiPort:
    if settings.ai_provider == "fake":
        return AiFake(dim=settings.embedding_dim)
    raise NotImplementedError(settings.ai_provider)


def build_ocr(settings: Settings) -> OcrPort:
    if settings.ocr_engine == "fake":
        return OcrFake()
    raise NotImplementedError(settings.ocr_engine)


def build_idp(settings: Settings) -> IdpPort:
    if settings.idp == "fake":
        return IdpFake(default_email="user@example.com")
    raise NotImplementedError(settings.idp)


def build_storage(settings: Settings) -> StoragePort:
    return FsStorage(settings.storage_root)


def build_renderer(settings: Settings) -> Render:
    """Dựng ảnh trang PDF cho OCR. Bản giả đủ cho OcrFake; bản thật chờ T-004/T-010."""
    if settings.ocr_engine == "fake":
        return lambda pdf, page: b"PNG-fake"
    raise NotImplementedError(settings.ocr_engine)
