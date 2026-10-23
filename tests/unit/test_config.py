from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import ALL_FEATURES, Settings, get_settings

REQUIRED = {
    "CWD_DATABASE_URL": "postgresql+asyncpg://u:p@localhost/db",
    "CWD_SESSION_SECRET": "s" * 32,
    "CWD_TELEMETRY_SECRET": "t" * 32,
    "CWD_STORAGE_ROOT": "/tmp/storage",
    "CWD_EMBEDDING_DIM": "384",
}


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path(__file__).parent)  # tránh đọc .env của dự án
    get_settings.cache_clear()


def _set(monkeypatch: pytest.MonkeyPatch, **overrides: str) -> None:
    for key, value in {**REQUIRED, **overrides}.items():
        monkeypatch.setenv(key, value)


def test_missing_required_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch)
    monkeypatch.delenv("CWD_DATABASE_URL")
    with pytest.raises(ValidationError, match="database_url"):
        Settings()  # type: ignore[call-arg]


def test_defaults_match_requirements(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch)
    s = Settings()  # type: ignore[call-arg]
    assert (s.max_upload_mb, s.max_files, s.max_question_chars) == (50, 10, 2000)
    assert (s.ai_timeout_s, s.history_days, s.purge_hours) == (60, 90, 24)
    assert s.ai_monthly_budget_usd == 300


def test_secret_min_length(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch, CWD_SESSION_SECRET="abc")
    with pytest.raises(ValidationError, match="session_secret"):
        Settings()  # type: ignore[call-arg]


def test_features_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    _set(monkeypatch, CWD_FEATURES="summary,history")
    assert Settings().features == {"summary", "history"}  # type: ignore[call-arg]
    monkeypatch.delenv("CWD_FEATURES")
    assert Settings().features == ALL_FEATURES  # type: ignore[call-arg]
    assert len(ALL_FEATURES) == 8


def test_env_example_lists_all_keys() -> None:
    env = Path(__file__).resolve().parents[2] / ".env.example"
    lines = [ln for ln in env.read_text(encoding="utf-8").splitlines() if ln and ln[0] != "#"]
    assert all(ln.endswith("=") for ln in lines)
    assert {ln[:-1] for ln in lines} == {f"CWD_{k.upper()}" for k in Settings.model_fields}
