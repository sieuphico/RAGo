from datetime import date
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, SettingsDep, require_roles
from app.core.errors import AppError, ErrorCode
from app.domain import Role
from app.modules.metrics.service import WeeklyMetricsOut, monday_of, weekly

router = APIRouter(
    prefix="/api/v1/metrics", dependencies=[Depends(require_roles(Role.ADMIN, Role.SPONSOR))]
)


@router.get("/weekly", response_model=WeeklyMetricsOut)
async def weekly_metrics(
    session: SessionDep, settings: SettingsDep, week: str | None = None
) -> WeeklyMetricsOut:
    tz = ZoneInfo(settings.timezone)
    if week is None:
        # Bỏ trống = tuần gần nhất có dữ liệu (tuần hiện tại nếu chưa có gì)
        latest = await weekly(session, monday_of(date.today()), tz)
        week_start = latest.weeks[0] if latest.weeks else monday_of(date.today())
    else:
        try:
            week_start = date.fromisoformat(week)
        except ValueError:
            raise AppError(ErrorCode.VALIDATION_ERROR) from None
        if week_start.weekday() != 0:  # phải là thứ Hai
            raise AppError(ErrorCode.VALIDATION_ERROR)
    return await weekly(session, week_start, tz)
