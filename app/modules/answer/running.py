"""Các câu trả lời đang chạy trong tiến trình API, để API-09 (Dừng) báo được cho đúng luồng."""

import asyncio
from uuid import UUID


class RunningAnswers:
    def __init__(self) -> None:
        self._events: dict[UUID, asyncio.Event] = {}

    def start(self, message_id: UUID) -> asyncio.Event:
        event = asyncio.Event()
        self._events[message_id] = event
        return event

    def stop(self, message_id: UUID) -> bool:
        """True nếu câu trả lời đang chạy và đã được yêu cầu dừng."""
        event = self._events.get(message_id)
        if event is None:
            return False
        event.set()
        return True

    def finish(self, message_id: UUID) -> None:
        self._events.pop(message_id, None)

    def __contains__(self, message_id: UUID) -> bool:
        return message_id in self._events


# Một thể hiện cho cả tiến trình API
RUNNING = RunningAnswers()
