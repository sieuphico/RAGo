from collections.abc import AsyncIterator
from pathlib import Path

import httpx

from app.core.db import get_session
from app.main import create_app

PACKAGES = ["core", "api", "domain", "modules", "ports", "adapters", "models", "worker"]


class _Scalar:
    def scalar_one(self) -> int:
        return 0


class _FakeSession:
    """Phiên giả: CSDL trả lời mọi truy vấn; test đơn vị không cần PostgreSQL."""

    async def execute(self, *args: object, **kwargs: object) -> _Scalar:
        return _Scalar()


async def test_health_returns_ok() -> None:
    async def fake_session() -> AsyncIterator[_FakeSession]:
        yield _FakeSession()

    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "db": "ok", "queue": "ok"}  # T-604 mở rộng T-001


def test_app_packages_exist() -> None:
    root = Path(__file__).resolve().parents[2] / "app"
    for name in PACKAGES:
        assert (root / name / "__init__.py").is_file(), name


def test_env_example_has_no_values() -> None:
    env = Path(__file__).resolve().parents[2] / ".env.example"
    for line in env.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            assert line.endswith("="), line
