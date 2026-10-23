"""Chỉ số Prometheus (CONTRACTS mục 9). Nhãn không chứa email, mã tài liệu hay nội dung (AD-10)."""

import shutil
import time
from pathlib import Path

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REGISTRY = CollectorRegistry()

HTTP_SECONDS = Histogram(
    "cwd_http_request_seconds", "Thời gian xử lý yêu cầu HTTP", ["route", "method", "status"],
    registry=REGISTRY,
)  # fmt: skip
FIRST_TOKEN = Histogram(
    "cwd_answer_first_token_seconds",
    "Từ lúc nhận câu hỏi tới token đầu tiên",
    buckets=(0.5, 1, 2, 5, 10, 15, 20, 30, 60),
    registry=REGISTRY,
)
QUESTIONS = Counter("cwd_questions_total", "Số câu hỏi đã gửi", registry=REGISTRY)
ERRORS = Counter("cwd_errors_total", "Số lỗi theo mã", ["code"], registry=REGISTRY)
JOBS_QUEUED = Gauge("cwd_jobs_queued", "Số tác vụ đang chờ", registry=REGISTRY)
DOC_SECONDS = Histogram(
    "cwd_document_processing_seconds", "Thời gian xử lý tài liệu", ["ocr"],
    buckets=(5, 15, 30, 60, 120, 180, 300, 600, 900), registry=REGISTRY,
)  # fmt: skip
AI_COST = Gauge("cwd_ai_cost_usd_month", "Chi phí AI ước tính trong tháng (USD)", registry=REGISTRY)
DISK_FREE = Gauge("cwd_disk_free_bytes", "Dung lượng trống của kho tệp", registry=REGISTRY)


class MetricsMiddleware:
    """ASGI thuần (không làm hỏng SSE). Nhãn `route` là mẫu đường dẫn, không phải đường dẫn thật."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = {"code": 500}

        async def capture(message: Message) -> None:
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, capture)
        finally:
            route = scope.get("route")
            template = getattr(route, "path_format", None) or getattr(route, "path", None)
            HTTP_SECONDS.labels(
                route=template or "unmatched", method=scope["method"], status=str(status["code"])
            ).observe(time.perf_counter() - started)


def update_disk_free(root: Path) -> None:
    probe = root if root.exists() else root.parent
    DISK_FREE.set(shutil.disk_usage(probe if probe.exists() else Path(".")).free)


def render() -> tuple[bytes, str]:
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
