from fastapi import APIRouter

from app.api.deps import SessionDataDep
from app.core.features import ALL_P1, is_enabled

router = APIRouter(prefix="/api/v1")


@router.get("/features")
async def get_features(_: SessionDataDep) -> dict[str, bool]:
    """Đã xác thực (kể cả ngoài allow-list): giao diện cần biết để ẩn mục P1."""
    return {name: is_enabled(name) for name in ALL_P1}
