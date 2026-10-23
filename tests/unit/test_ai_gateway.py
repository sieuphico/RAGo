import logging
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime
from typing import Any

import pytest

from app.adapters.ai_fake import AiFake
from app.adapters.ai_gateway import AiGateway
from app.core.config import Settings, get_settings
from app.core.errors import AppError, ErrorCode
from app.modules.usage import repository as usage_repo
from app.ports.ai import ProviderError

MONTH = date(2026, 11, 1)
NOW = datetime(2026, 11, 5, 8, tzinfo=UTC)


class _Session:
    async def commit(self) -> None:
        return None


class _Factory:
    def __call__(self) -> "_Factory":
        return self

    async def __aenter__(self) -> _Session:
        return _Session()

    async def __aexit__(self, *exc: object) -> None:
        return None


class Costs:
    def __init__(self, initial: float = 0.0) -> None:
        self.value = initial


@pytest.fixture
def costs(monkeypatch: pytest.MonkeyPatch) -> Costs:
    state = Costs()

    async def get_cost(session: object, month: date) -> float:
        assert month == MONTH
        return state.value

    async def add_cost(session: object, month: date, usd: float) -> None:
        state.value += usd

    monkeypatch.setattr(usage_repo, "get_cost", get_cost)
    monkeypatch.setattr(usage_repo, "add_cost", add_cost)
    return state


class Stub:
    """Nhà cung cấp giả có đếm lời gọi và kịch bản lỗi."""

    def __init__(self, *, fail_times: int = 0, tokens: list[str] | None = None) -> None:
        self.calls = 0
        self.fail_times = fail_times
        self.tokens = tokens or ["a", "b"]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ProviderError("down")
        return [[0.0] for _ in texts]

    async def generate(self, system: str, user: str) -> AsyncIterator[str]:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ProviderError("down")
        for token in self.tokens:
            yield token


def _settings(**overrides: Any) -> Settings:
    return get_settings().model_copy(update=overrides)


def _gateway(provider: Any, settings: Settings | None = None, **kwargs: Any) -> AiGateway:
    async def no_sleep(seconds: float) -> None:
        return None

    kwargs.setdefault("sleep", no_sleep)
    return AiGateway(
        provider, settings or _settings(), _Factory(), wall_clock=lambda: NOW, **kwargs  # type: ignore[arg-type]
    )


async def _drain(gateway: AiGateway, system: str = "s", user: str = "u") -> str:
    return "".join([t async for t in gateway.generate(system, user)])


async def test_timeout_maps_to_timeout(costs: Costs) -> None:
    gateway = _gateway(AiFake(dim=8, delay_s=2), _settings(ai_timeout_s=1))
    with pytest.raises(AppError) as info:
        await _drain(gateway)
    assert info.value.code == ErrorCode.TIMEOUT


async def test_embed_retried(costs: Costs) -> None:
    provider = Stub(fail_times=2)
    result = await _gateway(provider).embed(["a", "b"])
    assert result == [[0.0], [0.0]] and provider.calls == 3


async def test_embed_gives_up_with_unavailable(costs: Costs) -> None:
    provider = Stub(fail_times=99)
    with pytest.raises(AppError) as info:
        await _gateway(provider).embed(["a"])
    assert info.value.code == ErrorCode.AI_UNAVAILABLE and provider.calls == 3


async def test_generate_not_retried(costs: Costs) -> None:
    provider = Stub(fail_times=99)
    with pytest.raises(AppError) as info:
        await _drain(_gateway(provider))
    assert info.value.code == ErrorCode.AI_UNAVAILABLE and provider.calls == 1


async def test_generate_streams_tokens(costs: Costs) -> None:
    assert await _drain(_gateway(Stub(tokens=["Xin ", "chào"]))) == "Xin chào"


async def test_budget_warning_and_block(costs: Costs, caplog: pytest.LogCaptureFixture) -> None:
    gateway = _gateway(Stub(), _settings(ai_monthly_budget_usd=1.0, ai_budget_alert_ratio=0.8))
    costs.value = 0.85
    with caplog.at_level(logging.WARNING, logger="app.ai"):
        await _drain(gateway)
        await _drain(gateway)  # cảnh báo chỉ một lần mỗi tháng
    alerts = [r for r in caplog.records if "ai_budget_alert" in r.getMessage()]
    assert len(alerts) == 1
    costs.value = 1.0
    with pytest.raises(AppError) as info:
        await _drain(gateway)
    assert info.value.code == ErrorCode.BUDGET_EXCEEDED


async def test_circuit_opens_after_failures(costs: Costs) -> None:
    now = {"t": 1000.0}
    provider = Stub(fail_times=5)
    gateway = _gateway(
        provider, _settings(ai_circuit_failures=5, ai_circuit_open_s=30), clock=lambda: now["t"]
    )
    for _ in range(5):
        with pytest.raises(AppError):
            await _drain(gateway)
    assert provider.calls == 5
    with pytest.raises(AppError) as info:
        await _drain(gateway)
    assert info.value.code == ErrorCode.AI_UNAVAILABLE and provider.calls == 5  # chặn ngay
    now["t"] += 31
    assert await _drain(gateway) == "ab"  # một lời gọi thử, thành công đóng mạch
    assert provider.calls == 6
    assert await _drain(gateway) == "ab"


async def test_failed_trial_reopens_circuit(costs: Costs) -> None:
    now = {"t": 0.0}
    provider = Stub(fail_times=99)
    gateway = _gateway(
        provider, _settings(ai_circuit_failures=2, ai_circuit_open_s=30), clock=lambda: now["t"]
    )
    for _ in range(2):
        with pytest.raises(AppError):
            await _drain(gateway)
    now["t"] += 31
    with pytest.raises(AppError):
        await _drain(gateway)  # lần thử thất bại
    assert provider.calls == 3
    with pytest.raises(AppError):
        await _drain(gateway)  # mạch mở lại, không gọi nhà cung cấp
    assert provider.calls == 3


async def test_logs_have_no_content(costs: Costs, caplog: pytest.LogCaptureFixture) -> None:
    gateway = _gateway(Stub(tokens=["BÍ_MẬT_TRẢ_VỀ"]))
    with caplog.at_level(logging.DEBUG):
        await _drain(gateway, "BÍ_MẬT_HỆ_THỐNG", "BÍ_MẬT_NGƯỜI_DÙNG")
        await gateway.embed(["BÍ_MẬT_NHÚNG"])
    assert caplog.records
    assert "BÍ_MẬT" not in caplog.text


async def test_cost_accumulates(costs: Costs) -> None:
    settings = _settings(ai_price_input_usd_per_1k=0.001, ai_price_output_usd_per_1k=0.002)
    gateway = _gateway(Stub(tokens=["y" * 400]), settings)
    assert await _drain(gateway, "x" * 2000, "x" * 2000)  # vào 4.000 ký tự, ra 400 ký tự
    assert costs.value == pytest.approx(0.0012)


async def test_aclose_closes_provider_stream(costs: Costs) -> None:
    closed = {"value": False}

    class Provider(Stub):
        async def generate(self, system: str, user: str) -> AsyncIterator[str]:
            try:
                for token in ["a", "b", "c"]:
                    yield token
            finally:
                closed["value"] = True

    stream = _gateway(Provider()).generate("s", "u")
    assert await anext(stream) == "a"
    await stream.aclose()
    assert closed["value"] is True
