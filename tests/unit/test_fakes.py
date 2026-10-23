import math

import pytest

from app.adapters.ai_fake import AiFake
from app.adapters.idp_fake import IdpFake
from app.adapters.ocr_fake import OcrFake
from app.core.config import Settings
from app.core.wiring import build_ai, build_idp, build_ocr
from app.ports.ai import ProviderError, ProviderTimeout


async def test_fake_embed_is_deterministic() -> None:
    ai = AiFake(dim=384)
    a = (await ai.embed(["xin chào"]))[0]
    b = (await ai.embed(["xin chào"]))[0]
    assert a == b
    assert len(a) == 384
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, abs_tol=1e-6)


async def test_fake_embed_differs() -> None:
    a, b = await AiFake(dim=384).embed(["a", "b"])
    assert a != b


async def test_fake_generate_streams_labels() -> None:
    tokens = [t async for t in AiFake(dim=8).generate("hệ thống", "ngữ cảnh [c2] ... [c1]")]
    assert len(tokens) == 4
    assert "".join(tokens) == "Theo tài liệu [c2]."


async def test_fake_generate_without_label_skips_label_token() -> None:
    tokens = [t async for t in AiFake(dim=8).generate("s", "không có nhãn")]
    assert "".join(tokens) == "Theo tài liệu ."


async def test_fake_generate_error_modes() -> None:
    with pytest.raises(ProviderError):
        [t async for t in AiFake(dim=8, fail_mode="error").generate("s", "u")]
    with pytest.raises(ProviderTimeout):
        [t async for t in AiFake(dim=8, fail_mode="timeout").generate("s", "u")]


async def test_fake_ocr_and_idp() -> None:
    result = await OcrFake().recognize(b"png")
    assert (result.text, result.confidence) == ("Văn bản OCR trang 1", 0.95)
    idp = IdpFake("a@x.vn")
    assert idp.login_url("/cb", "s1") == "/cb?state=s1&email=a@x.vn"
    assert idp.login_url("/cb", "s1", "b@x.vn").endswith("email=b@x.vn")
    assert (await idp.complete({"email": "b@x.vn"})).email == "b@x.vn"


def test_wiring_fake(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {
        "CWD_DATABASE_URL": "postgresql+asyncpg://u:p@h/d",
        "CWD_SESSION_SECRET": "s" * 32,
        "CWD_TELEMETRY_SECRET": "t" * 32,
        "CWD_STORAGE_ROOT": "/tmp/s",
        "CWD_EMBEDDING_DIM": "16",
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    ai = build_ai(settings)
    assert isinstance(ai, AiFake) and ai.dim == settings.embedding_dim
    assert isinstance(build_ocr(settings), OcrFake)
    assert isinstance(build_idp(settings), IdpFake)
    settings.ai_provider = "other"
    with pytest.raises(NotImplementedError):
        build_ai(settings)
