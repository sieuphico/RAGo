"""Bảng đăng ký handler tác vụ và tác vụ định kỳ (CONTRACTS mục 8). Mỗi task thêm dòng của mình."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.domain import Job

Handler = Callable[[Job], Awaitable[None]]
Fn = Callable[[], Awaitable[None]]


@dataclass(frozen=True)
class Every:
    name: str
    seconds: int
    fn: Fn


@dataclass(frozen=True)
class Daily:
    name: str
    at: str  # "HH:MM", giờ máy chủ
    fn: Fn


_handlers: dict[str, Handler] = {}
_every: dict[str, Every] = {}
_daily: dict[str, Daily] = {}


def register(job_type: str, handler: Handler) -> None:
    _handlers[job_type] = handler


def every(name: str, seconds: int, fn: Fn) -> None:
    _every[name] = Every(name, seconds, fn)


def daily(name: str, at: str, fn: Fn) -> None:
    hour, minute = at.split(":")
    if not (0 <= int(hour) < 24 and 0 <= int(minute) < 60):
        raise ValueError(f"giờ không hợp lệ: {at}")
    _daily[name] = Daily(name, at, fn)


def handler_for(job_type: str) -> Handler | None:
    return _handlers.get(job_type)


def every_tasks() -> list[Every]:
    return list(_every.values())


def daily_tasks() -> list[Daily]:
    return list(_daily.values())


def clear() -> None:
    """Chỉ dùng trong test."""
    _handlers.clear()
    _every.clear()
    _daily.clear()
