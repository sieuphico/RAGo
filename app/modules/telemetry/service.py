import hashlib
import hmac
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain import CurrentUser
from app.modules.telemetry import schema
from app.modules.telemetry.repository import TelemetryRow, append_event

logger = logging.getLogger("app.telemetry")


def anon_id(email: str, secret: str) -> str:
    return hmac.new(secret.encode(), email.lower().encode(), hashlib.sha256).hexdigest()


def validate(event: str, props: dict[str, Any]) -> dict[str, Any]:
    """Ném KeyError (sự kiện lạ) hoặc ValidationError (thuộc tính sai/thừa)."""
    model = schema.EVENTS[event].model_validate(props)
    return model.model_dump(mode="json")


async def emit(
    session: AsyncSession, user: CurrentUser, sid: str, event: str, **props: object
) -> None:
    """Ghi một sự kiện; lỗi ghi chỉ cảnh báo, không bao giờ ném ra ngoài."""
    try:
        data = validate(event, dict(props))
        settings = get_settings()
        row = TelemetryRow(
            event=event,
            anon_user_id=anon_id(user.email, settings.telemetry_secret),
            session_id=sid,
            ts=datetime.now(UTC),
            app_version=settings.app_version,
            props=data,
        )
        async with session.begin_nested():  # savepoint: lỗi ghi không làm hỏng giao dịch chính
            await append_event(session, row)
    except (KeyError, ValidationError) as exc:
        logger.warning("telemetry %s rejected: %s", event, type(exc).__name__)
    except Exception as exc:  # noqa: BLE001 - đo lường không được làm hỏng luồng chính
        logger.warning("telemetry %s failed: %s", event, type(exc).__name__)
