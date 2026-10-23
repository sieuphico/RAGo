from fastapi import FastAPI

from app.api import auth, health, me
from app.core.errors import install_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Chat với tài liệu")
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    return app
