"""Validated settings, loaded once per process."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    openai_api_key: str = ""
    tavily_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_temperature: float = Field(0, ge=0, le=2)
    llm_timeout_seconds: float = Field(60, gt=0)
    llm_max_retries: int = Field(2, ge=0, le=10)
    tavily_max_results: int = Field(3, ge=1, le=20)
    interview_max_turns: int = Field(2, ge=1, le=20)
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://research:research@localhost:5432/research"
    checkpoint_database_url: str = "postgresql://research:research@localhost:5432/research"
    worker_poll_seconds: float = Field(1, gt=0)
    worker_lease_seconds: int = Field(900, ge=60)
    worker_heartbeat_seconds: int = Field(15, ge=1)
    max_worker_attempts: int = Field(3, ge=1)
    api_key: SecretStr = SecretStr("")
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "research-assistant"
    prompt_version: str = "v1"
    enforce_report_sources: bool = True
    cors_origins: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
