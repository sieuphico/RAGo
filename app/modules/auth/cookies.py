"""Cookie phiên ký bằng HMAC-SHA256 (thư viện chuẩn; không thêm phụ thuộc)."""

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.core.config import Settings

SESSION_COOKIE = "cwd_session"
STATE_COOKIE = "cwd_state"
STATE_TTL_S = 600
_SESSION_SALT = "cwd-session"
_STATE_SALT = "cwd-state"


@dataclass(frozen=True)
class SessionData:
    email: str
    sid: str
    issued_at: datetime


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _mac(body: str, secret: str, salt: str) -> str:
    key = hashlib.sha256(f"{salt}:{secret}".encode()).digest()
    return _b64(hmac.new(key, body.encode(), hashlib.sha256).digest())


def _dump(data: dict[str, Any], secret: str, salt: str) -> str:
    body = _b64(json.dumps(data, separators=(",", ":")).encode())
    return f"{body}.{_mac(body, secret, salt)}"


def _load(
    value: str, secret: str, salt: str, ttl_s: int, now: datetime
) -> dict[str, Any] | None:
    try:
        body, mac = value.split(".")
        if not hmac.compare_digest(mac, _mac(body, secret, salt)):
            return None
        data = json.loads(_unb64(body))
        age = now.timestamp() - float(data["iat"])
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(data, dict) or age > ttl_s or age < -60:
        return None
    return data


def issue_cookie(email: str, settings: Settings, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    data = {"email": email, "sid": secrets.token_hex(16), "iat": int(now.timestamp())}
    return _dump(data, settings.session_secret, _SESSION_SALT)


def read_cookie(value: str, settings: Settings, now: datetime | None = None) -> SessionData | None:
    data = _load(
        value, settings.session_secret, _SESSION_SALT, settings.session_ttl_s, now or datetime.now(UTC)
    )
    if data is None or not isinstance(data.get("email"), str) or not isinstance(data.get("sid"), str):
        return None
    return SessionData(data["email"], data["sid"], datetime.fromtimestamp(data["iat"], UTC))


def issue_state_cookie(
    state: str, next_url: str, settings: Settings, now: datetime | None = None
) -> str:
    now = now or datetime.now(UTC)
    data = {"state": state, "next": next_url, "iat": int(now.timestamp())}
    return _dump(data, settings.session_secret, _STATE_SALT)


def read_state_cookie(
    value: str, settings: Settings, now: datetime | None = None
) -> tuple[str, str] | None:
    data = _load(value, settings.session_secret, _STATE_SALT, STATE_TTL_S, now or datetime.now(UTC))
    if data is None or not isinstance(data.get("state"), str) or not isinstance(data.get("next"), str):
        return None
    return data["state"], data["next"]


def safe_next(next_url: str | None) -> str:
    """Chỉ nhận đường dẫn tương đối: bắt đầu `/`, không bắt đầu `//` và không có `\\`."""
    if next_url and next_url.startswith("/") and not next_url.startswith("//") and "\\" not in next_url:
        return next_url
    return "/"
