import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from prometheus_client.parser import text_string_to_metric_families
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import health
from app.core import metrics
from app.domain import Role
from tests.integration.helpers import login

ALERTS = Path(__file__).resolve().parents[2] / "deploy" / "alerts.yml"


def _samples(body: str) -> dict[str, list[tuple[dict[str, str], float]]]:
    out: dict[str, list[tuple[dict[str, str], float]]] = {}
    for family in text_string_to_metric_families(body):
        for sample in family.samples:
            out.setdefault(sample.name, []).append((sample.labels, sample.value))
    return out


async def test_healthz_ok(client: httpx.AsyncClient) -> None:
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "db": "ok", "queue": "ok"}


async def test_healthz_db_down(client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    async def down(session: AsyncSession) -> None:
        raise ConnectionError("db down")

    monkeypatch.setattr(health, "check_db", down)
    resp = await client.get("/healthz")
    assert resp.status_code == 503
    assert resp.json()["status"] == "degraded" and resp.json()["db"] == "down"
    assert "db down" not in resp.text


async def test_healthz_reports_stale_queue(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await session.execute(
        text(
            "INSERT INTO job (type, payload, status, created_at) "
            "VALUES ('ingest', '{}', 'QUEUED', now() - interval '31 minutes')"
        )
    )
    body = (await client.get("/healthz")).json()
    assert body == {"status": "degraded", "db": "ok", "queue": "backlog"}


async def test_metrics_no_content_labels(
    client: httpx.AsyncClient, session: AsyncSession
) -> None:
    await login(client, session, "lan@congty.vn", Role.BD_USER)
    doc_id = uuid4()
    await client.get(f"/api/v1/documents/{doc_id}/file")  # 404 nhưng route khớp mẫu
    await client.get("/khong-co-duong-dan-nay")
    body = (await client.get("/metrics")).text
    routes = {labels["route"] for labels, _ in _samples(body)["cwd_http_request_seconds_count"]}
    assert "/api/v1/documents/{doc_id}/file" in routes
    assert "unmatched" in routes
    assert str(doc_id) not in body and "@" not in body and "lan" not in body


async def test_metrics_names_present(client: httpx.AsyncClient, session: AsyncSession) -> None:
    body = (await client.get("/metrics")).text
    for name in (
        "cwd_http_request_seconds", "cwd_answer_first_token_seconds", "cwd_questions_total",
        "cwd_errors_total", "cwd_jobs_queued", "cwd_document_processing_seconds",
        "cwd_ai_cost_usd_month", "cwd_disk_free_bytes",
    ):  # fmt: skip
        assert f"# TYPE {name}" in body, name
    assert _samples(body)["cwd_disk_free_bytes"][0][1] > 0


async def test_jobs_queued_gauge(client: httpx.AsyncClient, session: AsyncSession) -> None:
    await session.execute(text("INSERT INTO job (type, payload, status) VALUES ('x','{}','QUEUED')"))
    body = (await client.get("/metrics")).text
    assert _samples(body)["cwd_jobs_queued"][0][1] == 1.0


async def test_cost_gauge(session: AsyncSession) -> None:
    from datetime import UTC, datetime

    from app.adapters.ai_gateway import AiGateway
    from app.core.config import get_settings
    from tests.integration.helpers import SharedSession
    from tests.integration.test_answer_service import Provider

    settings = get_settings().model_copy(
        update={"ai_price_input_usd_per_1k": 1.5, "ai_price_output_usd_per_1k": 0}
    )
    gateway = AiGateway(
        Provider(),
        settings,
        SharedSession(session),  # type: ignore[arg-type]
        wall_clock=lambda: datetime(2026, 11, 5, tzinfo=UTC),
    )
    await gateway.embed(["x" * 4000])  # 1.000 token vào × 1,5 USD / 1.000
    assert metrics.AI_COST._value.get() == pytest.approx(1.5)


@pytest.mark.skipif(shutil.which("docker") is None, reason="cần Docker để chạy promtool")
def test_alert_rules_valid() -> None:
    result = subprocess.run(
        [
            "docker", "run", "--rm", "-v", f"{ALERTS.parent}:/rules:ro", "--entrypoint", "promtool",
            "prom/prometheus:latest", "check", "rules", "/rules/alerts.yml",
        ],
        check=False, capture_output=True, text=True, timeout=120,
    )  # fmt: skip
    assert result.returncode == 0, result.stdout + result.stderr
