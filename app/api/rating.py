"""API-11: đánh giá 👍/👎 một câu trả lời (US-050, BR-023)."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import ConfigDict, model_validator

from app.api.deps import CurrentUserDep, SessionDataDep, SessionDep, require_roles
from app.core.errors import AppError, ErrorCode
from app.core.features import require_feature
from app.core.schemas import ApiModel
from app.domain import MessageStatus, Role
from app.modules.chat import repository as chat
from app.modules.telemetry.service import emit

router = APIRouter(
    prefix="/api/v1/chat",
    dependencies=[
        Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN)),
        Depends(require_feature("rating")),
    ],
)

ReasonCode = Literal["WRONG_INFO", "WRONG_CITATION", "MISSING_INFO", "OTHER"]
_RATEABLE = {MessageStatus.COMPLETED, MessageStatus.NOT_FOUND}


class RatingIn(ApiModel):
    model_config = ConfigDict(
        alias_generator=ApiModel.model_config["alias_generator"],
        populate_by_name=True,
        extra="forbid",
    )

    value: Literal["UP", "DOWN"]
    reason_code: ReasonCode | None = None

    @model_validator(mode="after")
    def _reason_only_with_down(self) -> "RatingIn":
        if self.value == "UP" and self.reason_code is not None:
            raise ValueError("reasonCode chỉ dùng với DOWN")
        return self


@router.post("/messages/{message_id}/rating", status_code=204)
async def rate_api(
    message_id: UUID,
    body: RatingIn,
    user: CurrentUserDep,
    data: SessionDataDep,
    session: SessionDep,
) -> Response:
    message = await chat.get_message_for_user(session, user.email, message_id)
    if message is None:
        raise AppError(ErrorCode.NOT_FOUND)
    if message.role != "assistant" or message.status not in _RATEABLE:
        raise AppError(ErrorCode.MESSAGE_NOT_RATEABLE)
    await chat.upsert_rating(session, message_id, body.value, body.reason_code)
    await emit(
        session,
        user,
        data.sid,
        "answer_rated",
        question_id=str(message_id),
        rating=body.value.lower(),
        reason_code=body.reason_code,
    )
    await session.commit()
    return Response(status_code=204)
