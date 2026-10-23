from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

ALL_FEATURES = frozenset(
    {"suggestions", "summary", "history", "rating", "copy", "scope", "followup", "duplicateCheck"}
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CWD_", env_file=".env", extra="ignore")

    database_url: str
    session_secret: str = Field(min_length=32)
    telemetry_secret: str = Field(min_length=32)
    storage_root: Path
    embedding_dim: int

    ai_provider: str = "fake"
    ai_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen3:1.7b"
    ollama_embed_model: str = "qwen3-embedding:0.6b"
    ocr_engine: str = "fake"
    idp: str = "fake"
    session_ttl_s: int = 28800
    max_upload_mb: int = 50
    max_files: int = 10
    max_pages: int = 300
    max_question_chars: int = 2000
    ai_timeout_s: int = 60
    ai_slow_notice_s: int = 15
    ai_monthly_budget_usd: float = 300
    ai_budget_alert_ratio: float = 0.8
    ai_price_input_usd_per_1k: float = 0
    ai_price_output_usd_per_1k: float = 0
    timezone: str = "Asia/Ho_Chi_Minh"
    ai_circuit_failures: int = 5
    ai_circuit_open_s: int = 30
    embed_batch_size: int = 32
    retrieval_k: int = 8
    relevance_threshold: float = 0.0
    chunk_target_chars: int = 1200
    chunk_overlap_chars: int = 150
    ocr_min_confidence: float = 0.80
    history_days: int = 90
    audit_days: int = 90
    purge_hours: int = 24
    job_max_attempts: int = 3
    job_stale_after_s: int = 1800
    features: Annotated[frozenset[str], NoDecode] = ALL_FEATURES
    app_version: str = "0.0.0-dev"
    worker_metrics_port: int = 9101

    @field_validator("features", mode="before")
    @classmethod
    def _parse_features(cls, value: object) -> object:
        if isinstance(value, str):
            return frozenset(p.strip() for p in value.split(",") if p.strip())
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
