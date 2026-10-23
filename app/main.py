from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import admin_audit, auth, document_events, documents_upload, health, me
from app.api.csrf import CsrfMiddleware
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.modules.documents.events import StatusHub


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(admin_audit.router)
    app.include_router(document_events.router)  # trước các route /documents/{docId}
    app.include_router(documents_upload.router)
    return app
