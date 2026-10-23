"""`/healthz` và `/metrics` (CONTRACTS mục 9). Không qua /api/v1; nginx chỉ chuyển /healthz, giữ /metrics nội bộ."""

import asyncio
import contextlib
from typing import Any

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep, SettingsDep
from app.core import metrics

router = APIRouter()
DB_TIMEOUT_S = 2.0
STALE_MINUTES = 30


async def check_db(session: AsyncSession) -> None:
    await asyncio.wait_for(session.execute(text("SELECT 1")), timeout=DB_TIMEOUT_S)


async def queued_count(session: AsyncSession, *, older_than_minutes: int | None = None) -> int:
    sql = "SELECT count(*) FROM job WHERE status = 'QUEUED'"
    params: dict[str, int] = {}
    if older_than_minutes is not None:
        sql += " AND created_at < now() - make_interval(mins => :m)"
        params["m"] = older_than_minutes
    return int((await session.execute(text(sql), params)).scalar_one())


@router.get("/healthz")
async def healthz(session: SessionDep) -> JSONResponse:
    try:
        await check_db(session)
    except Exception:  # noqa: BLE001 - mọi lỗi CSDL đều là "down", không lộ chi tiết
        return JSONResponse({"status": "degraded", "db": "down", "queue": "unknown"}, status_code=503)
    try:
        stale = await queued_count(session, older_than_minutes=STALE_MINUTES)
    except Exception:  # noqa: BLE001
        stale = 0
    body: dict[str, Any] = {
        "status": "ok" if stale == 0 else "degraded",
        "db": "ok",
        "queue": "ok" if stale == 0 else "backlog",
    }
    return JSONResponse(body)


@router.get("/metrics", include_in_schema=False)
async def metrics_endpoint(session: SessionDep, settings: SettingsDep) -> Response:
    """Chỉ mạng nội bộ: nginx không chuyển tiếp ra ngoài (T-602)."""
    with contextlib.suppress(Exception):  # thiếu CSDL không làm hỏng việc thu thập
        metrics.JOBS_QUEUED.set(await queued_count(session))
    metrics.update_disk_free(settings.storage_root)
    body, content_type = metrics.render()
    return Response(body, media_type=content_type)
