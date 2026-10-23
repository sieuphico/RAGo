"""Chọn bộ nối (giả hay thật). Chỉ file này được nhập app.adapters."""

from app.adapters.ai_fake import AiFake
from app.adapters.ai_gateway import AiGateway
from app.adapters.ai_ollama import OllamaAi
from app.adapters.idp_fake import IdpFake
from app.adapters.ocr_fake import OcrFake
from app.adapters.storage_fs import FsStorage
from app.core import db
from app.core.config import Settings
from app.ports.ai import AiPort
from app.ports.idp import IdpPort
from app.ports.ocr import OcrPort
from app.ports.storage import StoragePort
from app.worker.ocr_step import Render


def build_ai(settings: Settings) -> AiPort:
    if settings.ai_provider == "fake":
        return AiFake(dim=settings.embedding_dim)
    if settings.ai_provider == "ollama":
        return OllamaAi(settings)
    raise NotImplementedError(settings.ai_provider)


def build_ocr(settings: Settings) -> OcrPort:
    if settings.ocr_engine == "fake":
        return OcrFake()
    raise NotImplementedError(settings.ocr_engine)


def build_idp(settings: Settings) -> IdpPort:
    if settings.idp == "fake":
        if not settings.allow_fake_idp:
            # IdP giả nhận email bất kỳ qua login_hint: mặc định đóng để không lọt vào môi trường thật
            raise RuntimeError(
                "IdP giả đang tắt. Đặt CWD_ALLOW_FAKE_IDP=true chỉ ở máy phát triển hoặc staging; "
                "môi trường thật phải dùng IdP thật (T-006)."
            )
        return IdpFake(default_email="user@example.com")
    raise NotImplementedError(settings.idp)


def build_storage(settings: Settings) -> StoragePort:
    return FsStorage(settings.storage_root)


def build_renderer(settings: Settings) -> Render:
    """Dựng ảnh trang PDF cho OCR. Bản giả đủ cho OcrFake; bản thật chờ T-004/T-010."""
    if settings.ocr_engine == "fake":
        return lambda pdf, page: b"PNG-fake"
    raise NotImplementedError(settings.ocr_engine)


_gateway: AiGateway | None = None


def build_gateway(settings: Settings) -> AiGateway:
    """Thể hiện duy nhất của cổng AI; mọi mô-đun gọi AI qua đây (AD-04)."""
    global _gateway
    if _gateway is None:
        _gateway = AiGateway(build_ai(settings), settings, db.get_session_factory())
    return _gateway


async def ai_startup_check(settings: Settings) -> None:
    """Dừng sớm khi nhà cung cấp AI cấu hình sai (ví dụ số chiều vector); bản giả bỏ qua."""
    if settings.ai_provider == "fake":
        return
    check = getattr(build_gateway(settings).provider, "self_check", None)
    if check is not None:
        await check()
