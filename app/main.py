from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import (
    admin_audit,
    admin_users,
    auth,
    chat,
    chat_history,
    document_events,
    document_file,
    documents,
    documents_delete,
    documents_upload,
    features,
    health,
    me,
    metrics,
    rating,
    suggestions,
    summary,
    telemetry,
)
from app.api.csrf import CsrfMiddleware
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.core.metrics import MetricsMiddleware
from app.core.wiring import ai_startup_check
from app.modules.documents.events import StatusHub


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await ai_startup_check(get_settings())
    hub = StatusHub()
    await hub.start(get_settings().database_url)
    app.state.hub = hub
    try:
        yield
    finally:
        await hub.stop()


def create_app() -> FastAPI:
    app = FastAPI(title="Chat với tài liệu", lifespan=lifespan)
    install_error_handlers(app)
    app.add_middleware(CsrfMiddleware)
    app.add_middleware(MetricsMiddleware)  # ngoài cùng: đo cả yêu cầu bị CSRF từ chối
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(features.router)
    app.include_router(admin_audit.router)
    app.include_router(admin_users.router)
    app.include_router(chat.router)
    app.include_router(chat_history.router)
    app.include_router(rating.router)
    app.include_router(suggestions.router)
    app.include_router(summary.router)
    app.include_router(document_events.router)  # trước các route /documents/{docId}
    app.include_router(documents.router)
    app.include_router(document_file.router)
    app.include_router(documents_upload.router)
    app.include_router(documents_delete.router)
    app.include_router(telemetry.router)
    app.include_router(metrics.router)
    return app
