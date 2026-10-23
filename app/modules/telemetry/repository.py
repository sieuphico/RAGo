"""Telemetry chỉ siêu dữ liệu (AD-10): không có cột văn bản tự do ngoài `props`."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin import TelemetryEvent


@dataclass(frozen=True)
class TelemetryRow:
    event: str
    anon_user_id: str
    session_id: str
    ts: datetime
    app_version: str
    props: dict[str, Any] = field(default_factory=dict)


async def append_event(session: AsyncSession, row: TelemetryRow) -> None:
    session.add(
        TelemetryEvent(
            event=row.event,
            anon_user_id=row.anon_user_id,
            session_id=row.session_id,
            ts=row.ts,
            app_version=row.app_version,
            props=row.props,
        )
    )
    await session.flush()


async def events_between(
    session: AsyncSession, names: list[str], start: datetime, end: datetime
) -> list[TelemetryEvent]:
    query = (
        select(TelemetryEvent)
        .where(TelemetryEvent.event.in_(names), TelemetryEvent.ts >= start, TelemetryEvent.ts < end)
        .order_by(TelemetryEvent.ts, TelemetryEvent.id)
    )
    return list((await session.execute(query)).scalars())
