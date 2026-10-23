"""Chống CSRF: phương thức ghi dưới /api/v1 phải có `X-Requested-With: cwd` (Q-C10).

ASGI thuần (không BaseHTTPMiddleware) để không làm hỏng luồng SSE của API-08.
"""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class CsrfMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] == "http"
            and scope["method"] in WRITE_METHODS
            and scope["path"].startswith("/api/v1")
        ):
            headers = dict(scope["headers"])
            if headers.get(b"x-requested-with") != b"cwd":
                response = JSONResponse(
                    {"code": "CSRF_REJECTED", "retryable": False}, status_code=403
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)
