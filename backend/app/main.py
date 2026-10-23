from fastapi import FastAPI

from app.api import health


def create_app() -> FastAPI:
    app = FastAPI(title="Chat với tài liệu")
    app.include_router(health.router)
    return app
