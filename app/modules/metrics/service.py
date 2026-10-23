"""Số liệu hàng tuần từ telemetry chỉ siêu dữ liệu (US-051, BR-024). Không đọc nội dung câu hỏi hay câu trả lời."""

from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import ApiModel, UtcDatetime

CACHE_TTL = timedelta(hours=1)  # đáp ứng "cập nhật tối thiểu mỗi 24 giờ"
SERIES_WEEKS = 8


class MetricsOut(ApiModel):
    wau_percent: float | None
    wau_count: int
    allowed_count: int
    questions: int
    latency_p50_ms: float | None
    latency_p90_ms: float | None
    thumbs_up_percent: float | None
    not_found_percent: float | None


class SeriesPoint(ApiModel):
    week: date
    questions: int
    wau_percent: float | None


class WeeklyMetricsOut(ApiModel):
    week: date
    weeks: list[date]
    updated_at: UtcDatetime
    metrics: MetricsOut
    series: list[SeriesPoint]


_cache: dict[tuple[date, str], tuple[datetime, WeeklyMetricsOut]] = {}


def clear_cache() -> None:
    _cache.clear()


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _bounds(week_start: date, tz: ZoneInfo) -> tuple[datetime, datetime]:
    start = datetime.combine(week_start, time.min, tzinfo=tz)
    return start, start + timedelta(days=7)


def _pct(part: int, whole: int) -> float | None:
    return round(part / whole * 100, 1) if whole else None


async def _scalar(session: AsyncSession, sql: str, **params: Any) -> Any:
    return (await session.execute(text(sql), params)).scalar_one()


async def _allowed_count(session: AsyncSession) -> int:
    return int(
        await _scalar(session, "SELECT count(*) FROM allow_list_entry WHERE role <> 'SPONSOR'")
    )


async def _questions(
    session: AsyncSession, start: datetime, end: datetime
) -> tuple[int, int]:
    row = (
        await session.execute(
            text(
                "SELECT count(DISTINCT anon_user_id), count(*) FROM telemetry_event "
                "WHERE event = 'question_submitted' AND ts >= :s AND ts < :e"
            ),
            {"s": start, "e": end},
        )
    ).one()
    return int(row[0]), int(row[1])


async def weekly(
    session: AsyncSession, week_start: date, tz: ZoneInfo, now: datetime | None = None
) -> WeeklyMetricsOut:
    now = now or datetime.now(UTC)
    key = (week_start, tz.key)
    cached = _cache.get(key)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1]

    start, end = _bounds(week_start, tz)
    allowed = await _allowed_count(session)
    wau, questions = await _questions(session, start, end)

    latency = (
        await session.execute(
            text(
                "SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY (props->>'latency_ms')::float), "
                "percentile_cont(0.9) WITHIN GROUP (ORDER BY (props->>'latency_ms')::float), "
                "count(*), count(*) FILTER (WHERE (props->>'is_not_found')::boolean) "
                "FROM telemetry_event "
                "WHERE event = 'answer_completed' AND ts >= :s AND ts < :e"
            ),
            {"s": start, "e": end},
        )
    ).one()
    rated = (
        await session.execute(
            text(
                "SELECT count(*), count(*) FILTER (WHERE props->>'rating' = 'up') "
                "FROM telemetry_event WHERE event = 'answer_rated' AND ts >= :s AND ts < :e"
            ),
            {"s": start, "e": end},
        )
    ).one()

    weeks = [
        r[0]
        for r in await session.execute(
            text(
                "SELECT DISTINCT date_trunc('week', ts AT TIME ZONE :tz)::date AS w "
                "FROM telemetry_event ORDER BY w DESC"
            ),
            {"tz": tz.key},
        )
    ]
    series: list[SeriesPoint] = []
    for offset in range(SERIES_WEEKS - 1, -1, -1):
        point = week_start - timedelta(weeks=offset)
        s, e = _bounds(point, tz)
        point_wau, point_questions = await _questions(session, s, e)
        series.append(
            SeriesPoint(week=point, questions=point_questions, wau_percent=_pct(point_wau, allowed))
        )

    result = WeeklyMetricsOut(
        week=week_start,
        weeks=weeks,
        updated_at=now,
        metrics=MetricsOut(
            wau_percent=_pct(wau, allowed),
            wau_count=wau,
            allowed_count=allowed,
            questions=questions,
            latency_p50_ms=round(latency[0], 1) if latency[0] is not None else None,
            latency_p90_ms=round(latency[1], 1) if latency[1] is not None else None,
            thumbs_up_percent=_pct(int(rated[1]), int(rated[0])),
            not_found_percent=_pct(int(latency[3]), int(latency[2])),
        ),
        series=series,
    )
    _cache[key] = (now, result)
    return result
