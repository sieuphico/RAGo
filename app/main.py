from fastapi import FastAPI

from app.api import admin_audit, auth, health, me
from app.api.csrf import CsrfMiddleware
from app.core.errors import install_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Chat với tài liệu")
    install_error_handlers(app)
    app.add_middleware(CsrfMiddleware)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(admin_audit.router)
    return app
