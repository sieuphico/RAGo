from pathlib import Path

import httpx

from app.main import create_app

PACKAGES = ["core", "api", "domain", "modules", "ports", "adapters", "models", "worker"]


async def test_health_returns_ok() -> None:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_app_packages_exist() -> None:
    root = Path(__file__).resolve().parents[2] / "app"
    for name in PACKAGES:
        assert (root / name / "__init__.py").is_file(), name


def test_env_example_has_no_values() -> None:
    env = Path(__file__).resolve().parents[2] / ".env.example"
    for line in env.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            assert line.endswith("="), line
