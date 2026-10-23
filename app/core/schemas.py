"""Nền cho mô hình vào/ra của API: JSON camelCase, thời điểm ISO 8601 UTC hậu tố Z."""

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer
from pydantic.alias_generators import to_camel


def _utc_z(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


UtcDatetime = Annotated[datetime, PlainSerializer(_utc_z, return_type=str)]


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
