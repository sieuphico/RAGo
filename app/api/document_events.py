from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.deps import require_roles
from app.domain import Role
from app.modules.documents import events

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(require_roles(Role.BD_USER, Role.TEAM_LEAD, Role.ADMIN))],
)


@router.get("/documents/events")
async def document_events(request: Request) -> StreamingResponse:
    hub: events.StatusHub = request.app.state.hub
    return StreamingResponse(
        events.event_stream(hub, request.is_disconnected),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
