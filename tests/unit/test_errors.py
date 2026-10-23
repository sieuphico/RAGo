import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from app.core.errors import ERROR_DEFAULTS, AppError, ErrorCode, install_error_handlers
from app.main import create_app

# 27 mã chép từ CONTRACTS mục 3
CONTRACT_CODES = {
    "AUTH_EXPIRED", "AUTH_FORBIDDEN", "CSRF_REJECTED", "VALIDATION_ERROR", "NOT_FOUND",
    "FILE_NOT_PDF", "FILE_TOO_LARGE", "FILE_TOO_MANY", "FILE_CORRUPTED", "FILE_ENCRYPTED",
    "OCR_UNREADABLE", "PROCESSING_ERROR", "DOC_NOT_FOUND", "DOC_NOT_READY",
    "SESSION_NOT_FOUND", "QUESTION_EMPTY", "QUESTION_TOO_LONG", "QUESTION_IN_PROGRESS",
    "MESSAGE_NOT_RATEABLE", "EMAIL_INVALID", "USER_EXISTS", "USER_LIMIT_REACHED",
    "LAST_ADMIN", "AI_UNAVAILABLE", "BUDGET_EXCEEDED", "TIMEOUT", "INTERNAL",
}  # fmt: skip


class _Ask(BaseModel):
    text: str


def _app() -> FastAPI:
    app = FastAPI()
    install_error_handlers(app)

    @app.get("/expired")
    async def expired() -> None:
        raise AppError(ErrorCode.AUTH_EXPIRED)

    @app.get("/ai")
    async def ai() -> None:
        raise AppError(ErrorCode.AI_UNAVAILABLE)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("db password=x")

    @app.post("/ask")
    async def ask(body: _Ask) -> dict[str, str]:
        return {"text": body.text}

    return app


def _client(app: FastAPI) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


async def test_app_error_serialization() -> None:
    async with _client(_app()) as c:
        resp = await c.get("/expired")
    assert resp.status_code == 401
    assert resp.json() == {"code": "AUTH_EXPIRED", "retryable": False}


async def test_retryable_default() -> None:
    async with _client(_app()) as c:
        resp = await c.get("/ai")
    assert resp.status_code == 503
    assert resp.json()["retryable"] is True


async def test_validation_error_shape() -> None:
    async with _client(_app()) as c:
        resp = await c.post("/ask", json={"x": 1})
    assert resp.status_code == 422
    assert resp.json() == {"code": "VALIDATION_ERROR", "retryable": False}


async def test_unknown_route() -> None:
    async with _client(create_app()) as c:
        resp = await c.get("/api/v1/khong-co")
    assert resp.status_code == 404
    assert resp.json() == {"code": "NOT_FOUND", "retryable": False}


async def test_unhandled_error_is_generic() -> None:
    async with _client(_app()) as c:
        resp = await c.get("/boom")
    assert resp.status_code == 500
    assert resp.json() == {"code": "INTERNAL", "retryable": False}
    assert "password" not in resp.text and "Traceback" not in resp.text


def test_codes_match_contract() -> None:
    assert {c.value for c in ErrorCode} == CONTRACT_CODES
    assert len(CONTRACT_CODES) == 27
    assert set(ERROR_DEFAULTS) == set(ErrorCode)
