"""Điểm duy nhất gọi AI (AD-04): thời hạn, thử lại, ngắt mạch, hạn mức chi phí, ánh xạ lỗi.

Nhật ký mỗi lời gọi chỉ có `op`, `chars_in`, `chars_out`, `latency_ms`, `outcome`;
không bao giờ có prompt hay văn bản trả về.
"""

import asyncio
import logging
import math
import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.errors import AppError, ErrorCode
from app.core.metrics import AI_COST
from app.modules.usage import repository as usage
from app.ports.ai import AiPort, ProviderError, ProviderTimeout

logger = logging.getLogger("app.ai")
EMBED_RETRY_DELAYS_S = (1.0, 2.0)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class _Circuit:
    """Ngắt mạch: mở sau N lỗi liên tiếp; hết thời gian mở thì cho đúng một lời gọi thử."""

    def __init__(self, failures: int, open_s: float, clock: Callable[[], float]) -> None:
        self.threshold, self.open_s, self.clock = failures, open_s, clock
        self.count = 0
        self.opened_at: float | None = None
        self.trial_in_flight = False

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if self.clock() - self.opened_at < self.open_s or self.trial_in_flight:
            return False
        self.trial_in_flight = True
        return True

    def success(self) -> None:
        self.count, self.opened_at, self.trial_in_flight = 0, None, False

    def failure(self) -> None:
        self.count += 1
        if self.trial_in_flight or self.count >= self.threshold:
            self.opened_at = self.clock()
        self.trial_in_flight = False


class AiGateway:
    def __init__(
        self,
        provider: AiPort,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
        clock: Callable[[], float] = time.monotonic,
        *,
        wall_clock: Callable[[], datetime] = _utcnow,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.provider = provider
        self.settings = settings
        self.session_factory = session_factory
        self.clock = clock
        self.wall_clock = wall_clock
        self.sleep = sleep
        self.circuit = _Circuit(settings.ai_circuit_failures, settings.ai_circuit_open_s, clock)
        self._alerted_month: date | None = None

    # ---- hạn mức chi phí
    def _month(self) -> date:
        return self.wall_clock().date().replace(day=1)

    async def _check_budget(self) -> None:
        month = self._month()
        async with self.session_factory() as session:
            cost = await usage.get_cost(session, month)
        AI_COST.set(cost)
        budget = self.settings.ai_monthly_budget_usd
        if cost >= budget:
            raise AppError(ErrorCode.BUDGET_EXCEEDED)
        if cost >= self.settings.ai_budget_alert_ratio * budget and self._alerted_month != month:
            self._alerted_month = month
            logger.warning("ai_budget_alert month=%s ratio=%.2f", month, cost / budget)

    def _estimate(self, chars_in: int, chars_out: int) -> float:
        s = self.settings
        return (
            math.ceil(chars_in / 4) / 1000 * s.ai_price_input_usd_per_1k
            + math.ceil(chars_out / 4) / 1000 * s.ai_price_output_usd_per_1k
        )

    async def _record_cost(self, chars_in: int, chars_out: int) -> None:
        cost = self._estimate(chars_in, chars_out)
        if cost <= 0:
            return
        async with self.session_factory() as session:
            await usage.add_cost(session, self._month(), cost)
            await session.commit()
            AI_COST.set(await usage.get_cost(session, self._month()))

    def _log(self, op: str, chars_in: int, chars_out: int, started: float, outcome: str) -> None:
        logger.info(
            "ai_call op=%s chars_in=%d chars_out=%d latency_ms=%d outcome=%s",
            op, chars_in, chars_out, int((self.clock() - started) * 1000), outcome,
        )  # fmt: skip

    def _admit(self) -> None:
        if not self.circuit.allow():
            raise AppError(ErrorCode.AI_UNAVAILABLE)

    # ---- embed
    async def embed(self, texts: list[str]) -> list[list[float]]:
        await self._check_budget()
        self._admit()
        started = self.clock()
        chars_in = sum(len(t) for t in texts)
        error = AppError(ErrorCode.AI_UNAVAILABLE)
        for attempt in range(len(EMBED_RETRY_DELAYS_S) + 1):
            try:
                result = await asyncio.wait_for(
                    self.provider.embed(texts), timeout=self.settings.ai_timeout_s
                )
            except (TimeoutError, ProviderTimeout):
                error = AppError(ErrorCode.TIMEOUT)
            except ProviderError:
                error = AppError(ErrorCode.AI_UNAVAILABLE)
            else:
                self.circuit.success()
                await self._record_cost(chars_in, 0)
                self._log("embed", chars_in, 0, started, "ok")
                return result
            if attempt < len(EMBED_RETRY_DELAYS_S):
                await self.sleep(EMBED_RETRY_DELAYS_S[attempt])
        self.circuit.failure()
        self._log("embed", chars_in, 0, started, error.code.value)
        raise error

    # ---- generate
    async def generate(self, system: str, user: str) -> AsyncGenerator[str]:
        await self._check_budget()
        self._admit()
        started = self.clock()
        deadline = started + self.settings.ai_timeout_s
        chars_in, chars_out, outcome = len(system) + len(user), 0, "ok"
        stream = self.provider.generate(system, user).__aiter__()
        try:
            while True:
                remaining = deadline - self.clock()
                if remaining <= 0:
                    raise AppError(ErrorCode.TIMEOUT)
                try:
                    token = await asyncio.wait_for(anext(stream), timeout=remaining)
                except StopAsyncIteration:
                    break
                except (TimeoutError, ProviderTimeout):
                    raise AppError(ErrorCode.TIMEOUT) from None
                except ProviderError:
                    raise AppError(ErrorCode.AI_UNAVAILABLE) from None
                chars_out += len(token)
                yield token
            self.circuit.success()
        except AppError as exc:
            outcome = exc.code.value
            self.circuit.failure()
            raise
        except GeneratorExit:
            outcome = "closed"
            self.circuit.trial_in_flight = False
            raise
        finally:
            aclose: Any = getattr(stream, "aclose", None)
            if aclose is not None:
                await aclose()
            await self._record_cost(chars_in, chars_out)
            self._log("generate", chars_in, chars_out, started, outcome)
