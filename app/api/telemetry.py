from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, ValidationError

from app.api.deps import CurrentUserDep, SessionDataDep, SessionDep
from app.core.config import get_settings
from app.core.errors import AppError, ErrorCode
from app.modules.telemetry import schema
from app.modules.telemetry.repository import TelemetryRow, append_event
from app.modules.telemetry.service import anon_id, validate

router = APIRouter(prefix="/api/v1")


class TelemetryIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    props: dict[str, Any] = {}


@router.post("/telemetry/events", status_code=204)
async def post_event(
    body: TelemetryIn, user: CurrentUserDep, data: SessionDataDep, session: SessionDep
) -> Response:
    if body.event not in schema.CLIENT_EVENTS:
        raise AppError(ErrorCode.VALIDATION_ERROR)
    try:
        props = validate(body.event, body.props)
    except (KeyError, ValidationError):
        raise AppError(ErrorCode.VALIDATION_ERROR) from None
    settings = get_settings()
    await append_event(
        session,
        TelemetryRow(
            event=body.event,
            anon_user_id=anon_id(user.email, settings.telemetry_secret),
            session_id=data.sid,
            ts=datetime.now(UTC),
            app_version=settings.app_version,
            props=props,
        ),
    )
    await session.commit()
    return Response(status_code=204)
