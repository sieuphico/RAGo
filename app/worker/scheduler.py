"""Tác vụ định kỳ: `every` theo giây, `daily` theo giờ máy chủ. Một tác vụ lỗi không chặn tác vụ khác."""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime

from app.worker import registry

logger = logging.getLogger("app.worker.scheduler")


class Scheduler:
    def __init__(self) -> None:
        self._last_every: dict[str, datetime] = {}
        self._last_daily: dict[str, object] = {}  # name -> ngày đã chạy
        self._tasks: set[asyncio.Task[None]] = set()

    def _spawn(self, name: str, fn: registry.Fn) -> None:
        async def run() -> None:
            try:
                await fn()
            except Exception as exc:  # noqa: BLE001 - không để một tác vụ làm sập vòng lặp
                logger.error("scheduled %s failed: %s", name, type(exc).__name__)

        task = asyncio.create_task(run())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def tick(self, now: datetime) -> None:
        for item in registry.every_tasks():
            last = self._last_every.setdefault(item.name, now)
            if (now - last).total_seconds() >= item.seconds:
                self._last_every[item.name] = now
                self._spawn(item.name, item.fn)
        for daily in registry.daily_tasks():
            hour, minute = (int(x) for x in daily.at.split(":"))
            due = (now.hour, now.minute) >= (hour, minute)
            if daily.name not in self._last_daily:
                # Lần tick đầu: nếu đã qua giờ hẹn hôm nay thì coi như hôm nay đã chạy
                self._last_daily[daily.name] = now.date() if due else None
                continue
            if due and self._last_daily[daily.name] != now.date():
                self._last_daily[daily.name] = now.date()
                self._spawn(daily.name, daily.fn)

    async def drain(self) -> None:
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)


async def run_scheduler(clock: Callable[[], datetime], stop: asyncio.Event) -> None:
    scheduler = Scheduler()
    while not stop.is_set():
        await scheduler.tick(clock())
        try:
            await asyncio.wait_for(stop.wait(), timeout=1.0)
        except TimeoutError:
            pass
    await scheduler.drain()
