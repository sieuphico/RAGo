from fastapi import FastAPI

from app.api import health
from app.core.errors import install_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Chat với tài liệu")
    install_error_handlers(app)
    app.include_router(health.router)
    return app
