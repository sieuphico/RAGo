import json
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import Role
from app.modules.metrics import service as metrics
from app.modules.telemetry.repository import TelemetryRow, append_event
from app.modules.users import repository as users
from tests.integration.helpers import login

WEEK = "2026-12-21"  # thứ Hai
BASE = datetime(2026, 12, 21, 3, tzinfo=UTC)  # 10:00 giờ Việt Nam, trong tuần


@pytest.fixture(autouse=True)
def _fresh_cache() -> None:
    metrics.clear_cache()


async def _event(session: AsyncSession, name: str, user: str, props: dict[str, object], day: int = 0) -> None:
    await append_event(
        session,
        TelemetryRow(name, user, "s", BASE + timedelta(days=day, minutes=len(name)), "0.0.0", props),
    )


async def _seed(session: AsyncSession) -> None:
    for i in range(18):
        await users.add(session, f"u{i}@congty.vn", Role.BD_USER, "root")
    await users.add(session, "ntt@congty.vn", Role.SPONSOR, "root")
    for q in range(241):
        await _event(session, "question_submitted", f"anon{q % 13}", {"question_id": str(uuid4())}, q % 5)
    for n in range(1, 201):
        await _event(
            session, "answer_completed", f"anon{n % 13}",
            {"latency_ms": n * 100, "is_not_found": n <= 36, "citation_count": 1},
            n % 5,
        )  # fmt: skip
    for n in range(50):
        await _event(
            session, "answer_rated", "anon1", {"rating": "up" if n < 38 else "down"}, n % 5
        )


async def test_weekly_aggregation(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await _seed(session)
    await login(client, session, "ntt@congty.vn", None)
    resp = await client.get("/api/v1/metrics/weekly", params={"week": WEEK})
    assert resp.status_code == 200
    body = resp.json()
    m = body["metrics"]
    assert (m["wauCount"], m["allowedCount"], m["questions"]) == (13, 18, 241)
    assert m["wauPercent"] == 72.2
    assert m["latencyP50Ms"] == pytest.approx(10050, abs=1)
    assert m["latencyP90Ms"] == pytest.approx(18010, abs=1)
    assert m["notFoundPercent"] == 18.0 and m["thumbsUpPercent"] == 76.0
    assert body["week"] == WEEK and WEEK in body["weeks"] and body["updatedAt"].endswith("Z")
    assert len(body["series"]) == 8 and body["series"][-1] == {
        "week": WEEK, "questions": 241, "wauPercent": 72.2,
    }  # fmt: skip


async def test_metrics_roles(client: httpx.AsyncClient, session: AsyncSession) -> None:
    expected = {
        "lan@congty.vn": (Role.BD_USER, 403),
        "minh@congty.vn": (Role.TEAM_LEAD, 403),
        "ntt@congty.vn": (Role.SPONSOR, 200),
        "quantri@congty.vn": (Role.ADMIN, 200),
    }
    for email, (role, code) in expected.items():
        await login(client, session, email, role)
        resp = await client.get("/api/v1/metrics/weekly", params={"week": WEEK})
        assert resp.status_code == code, email


async def test_metrics_no_content(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await _seed(session)
    await _event(session, "answer_copied", "anon1", {"question_id": "BÍ_MẬT_NỘI_DUNG"})
    await login(client, session, "ntt@congty.vn", None)
    text = (await client.get("/api/v1/metrics/weekly", params={"week": WEEK})).text
    assert "BÍ_MẬT" not in text and "question_id" not in text
    assert "anon" not in text and "@" not in text
    json.loads(text)


async def test_empty_week(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    m = (await client.get("/api/v1/metrics/weekly", params={"week": "2026-01-05"})).json()["metrics"]
    assert m["questions"] == 0 and m["wauCount"] == 0
    assert m["thumbsUpPercent"] is None and m["notFoundPercent"] is None
    assert m["latencyP50Ms"] is None and m["wauPercent"] == 0.0  # allowedCount = 1 (quản trị viên)


async def test_week_must_be_monday(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    for bad in ("2026-12-22", "khong-phai-ngay", "2026-13-01"):
        resp = await client.get("/api/v1/metrics/weekly", params={"week": bad})
        assert resp.status_code == 422 and resp.json()["code"] == "VALIDATION_ERROR", bad


async def test_default_week_is_latest_with_data(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await _seed(session)
    await login(client, session, "quantri@congty.vn", Role.ADMIN)
    body = (await client.get("/api/v1/metrics/weekly")).json()
    # Đăng nhập tạo sự kiện auth_* ở tuần hiện tại (2026-10-19) nên tuần 2026-12-21 vẫn mới nhất
    assert body["week"] == WEEK


async def test_cache_is_reused_within_an_hour(session: AsyncSession) -> None:
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    first = await metrics.weekly(session, date(2026, 12, 21), tz, BASE)
    await _event(session, "question_submitted", "anon1", {})
    again = await metrics.weekly(session, date(2026, 12, 21), tz, BASE + timedelta(minutes=30))
    assert again is first
    later = await metrics.weekly(session, date(2026, 12, 21), tz, BASE + timedelta(hours=2))
    assert later.metrics.questions == first.metrics.questions + 1
