"""`python -m app.worker`: chạy worker và scheduler; SIGTERM dừng nhẹ nhàng (chờ tối đa 30 giây)."""

import asyncio
import logging
import signal
import socket
import uuid

from prometheus_client import start_http_server

from app.core.config import get_settings
from app.core.metrics import REGISTRY
from app.core.wiring import ai_startup_check
from app.worker.main import register_defaults, run_worker
from app.worker.scheduler import run_scheduler

GRACE_S = 30


def _clock():  # type: ignore[no-untyped-def]
    from datetime import datetime

    return datetime.now().astimezone()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await ai_startup_check(get_settings())
    start_http_server(get_settings().worker_metrics_port, registry=REGISTRY)  # /metrics của worker
    register_defaults()
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:  # Windows
            signal.signal(sig, lambda *_: loop.call_soon_threadsafe(stop.set))
    worker_id = f"{socket.gethostname()}-{uuid.uuid4().hex[:6]}"
    tasks = [
        asyncio.create_task(run_worker(worker_id, stop)),
        asyncio.create_task(run_scheduler(_clock, stop)),
    ]
    await stop.wait()
    _, pending = await asyncio.wait(tasks, timeout=GRACE_S)
    for task in pending:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
