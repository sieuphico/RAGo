import httpx
import pytest
from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.core.features import ALL_P1, is_enabled, require_feature
from app.main import create_app
from app.modules.auth.cookies import SESSION_COOKIE, issue_cookie

CSRF = {"X-Requested-With": "cwd"}


@pytest.fixture
def features(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    def use(value: str) -> None:
        monkeypatch.setenv("CWD_FEATURES", value)
        get_settings.cache_clear()

    yield use
    monkeypatch.delenv("CWD_FEATURES", raising=False)
    get_settings.cache_clear()


def _client(app: object) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)  # type: ignore[arg-type]
    return httpx.AsyncClient(transport=transport, base_url="https://test")


async def test_disabled_feature_404(features) -> None:  # type: ignore[no-untyped-def]
    features("history")
    app = create_app()
    router = APIRouter()

    @router.get("/t/summary", dependencies=[Depends(require_feature("summary"))])
    async def summary() -> dict[str, bool]:
        return {"ok": True}

    @router.get("/t/history", dependencies=[Depends(require_feature("history"))])
    async def history() -> dict[str, bool]:
        return {"ok": True}

    app.include_router(router)
    async with _client(app) as client:
        off = await client.get("/t/summary")
        on = await client.get("/t/history")
    assert off.status_code == 404 and off.json() == {"code": "NOT_FOUND", "retryable": False}
    assert on.status_code == 200


async def test_features_endpoint(features) -> None:  # type: ignore[no-untyped-def]
    features("summary")
    async with _client(create_app()) as client:
        client.cookies.set(SESSION_COOKIE, issue_cookie("lan@congty.vn", get_settings()))
        resp = await client.get("/api/v1/features")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) == set(ALL_P1) and len(body) == 8
    assert [k for k, v in body.items() if v] == ["summary"]


async def test_features_requires_auth() -> None:
    async with _client(create_app()) as client:
        assert (await client.get("/api/v1/features")).status_code == 401


def test_unknown_feature() -> None:
    with pytest.raises(ValueError):
        is_enabled("abc")
    with pytest.raises(ValueError):
        require_feature("abc")


def test_default_enables_everything(features) -> None:  # type: ignore[no-untyped-def]
    features("")
    get_settings.cache_clear()
    import os

    os.environ.pop("CWD_FEATURES", None)
    get_settings.cache_clear()
    assert all(is_enabled(name) for name in ALL_P1)
