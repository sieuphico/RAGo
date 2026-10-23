"""Mã lỗi thống nhất (CONTRACTS mục 3). Mã mới phải thêm vào CONTRACTS trước."""

import logging
import uuid
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")


class ErrorCode(str, Enum):
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    CSRF_REJECTED = "CSRF_REJECTED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    FILE_NOT_PDF = "FILE_NOT_PDF"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_TOO_MANY = "FILE_TOO_MANY"
    FILE_CORRUPTED = "FILE_CORRUPTED"
    FILE_ENCRYPTED = "FILE_ENCRYPTED"
    OCR_UNREADABLE = "OCR_UNREADABLE"
    PROCESSING_ERROR = "PROCESSING_ERROR"
    DOC_NOT_FOUND = "DOC_NOT_FOUND"
    DOC_NOT_READY = "DOC_NOT_READY"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    QUESTION_EMPTY = "QUESTION_EMPTY"
    QUESTION_TOO_LONG = "QUESTION_TOO_LONG"
    QUESTION_IN_PROGRESS = "QUESTION_IN_PROGRESS"
    MESSAGE_NOT_RATEABLE = "MESSAGE_NOT_RATEABLE"
    EMAIL_INVALID = "EMAIL_INVALID"
    USER_EXISTS = "USER_EXISTS"
    USER_LIMIT_REACHED = "USER_LIMIT_REACHED"
    LAST_ADMIN = "LAST_ADMIN"
    AI_UNAVAILABLE = "AI_UNAVAILABLE"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    TIMEOUT = "TIMEOUT"
    INTERNAL = "INTERNAL"


E = ErrorCode

# (HTTP, retryable). Mã chỉ là lý do (FILE_*, OCR_*, PROCESSING_ERROR) dùng 400 nếu lỡ ném ra API.
ERROR_DEFAULTS: dict[ErrorCode, tuple[int, bool]] = {
    E.AUTH_EXPIRED: (401, False),
    E.AUTH_FORBIDDEN: (403, False),
    E.CSRF_REJECTED: (403, False),
    E.VALIDATION_ERROR: (422, False),
    E.NOT_FOUND: (404, False),
    E.FILE_NOT_PDF: (400, False),
    E.FILE_TOO_LARGE: (400, False),
    E.FILE_TOO_MANY: (400, False),
    E.FILE_CORRUPTED: (400, False),
    E.FILE_ENCRYPTED: (400, False),
    E.OCR_UNREADABLE: (400, False),
    E.PROCESSING_ERROR: (400, False),
    E.DOC_NOT_FOUND: (404, False),
    E.DOC_NOT_READY: (409, False),
    E.SESSION_NOT_FOUND: (404, False),
    E.QUESTION_EMPTY: (400, False),
    E.QUESTION_TOO_LONG: (400, False),
    E.QUESTION_IN_PROGRESS: (409, True),
    E.MESSAGE_NOT_RATEABLE: (409, False),
    E.EMAIL_INVALID: (400, False),
    E.USER_EXISTS: (409, False),
    E.USER_LIMIT_REACHED: (409, False),
    E.LAST_ADMIN: (409, False),
    E.AI_UNAVAILABLE: (503, True),
    E.BUDGET_EXCEEDED: (503, False),
    E.TIMEOUT: (504, True),
    E.INTERNAL: (500, False),
}


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        *,
        retryable: bool | None = None,
        http_status: int | None = None,
    ) -> None:
        default_status, default_retryable = ERROR_DEFAULTS[code]
        super().__init__(code.value)
        self.code = code
        self.retryable = default_retryable if retryable is None else retryable
        self.http_status = default_status if http_status is None else http_status


def _body(code: ErrorCode, retryable: bool, status: int) -> JSONResponse:
    return JSONResponse({"code": code.value, "retryable": retryable}, status_code=status)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return _body(exc.code, exc.retryable, exc.http_status)

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _body(E.VALIDATION_ERROR, False, 422)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code in (404, 405):
            return _body(E.NOT_FOUND, False, 404)
        if exc.status_code == 401:
            return _body(E.AUTH_EXPIRED, False, 401)
        if exc.status_code == 403:
            return _body(E.AUTH_FORBIDDEN, False, 403)
        return _body(E.INTERNAL, False, 500)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        # Chỉ ghi tên lớp lỗi và mã yêu cầu: không ghi thông điệp hay thân yêu cầu
        logger.error("unhandled %s request_id=%s", type(exc).__name__, request_id)
        return _body(E.INTERNAL, False, 500)
