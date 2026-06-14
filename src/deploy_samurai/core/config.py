from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    app_name: str = "DeploySamurai"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = Field(
        default="postgresql+asyncpg://deploy_samurai:deploy_samurai@localhost:5432/deploy_samurai"
    )
    repo_workspace_root: Path = Path(".workspaces/repos")
    artifact_root: Path = Path("artifacts")
    aws_region: str = "us-east-1"
    cors_allow_origins: str = "http://localhost:3000,http://localhost:8077,http://127.0.0.1:8077"
    cors_allow_origin_regex: str | None = r"http://(localhost|127\.0\.0\.1):\d+"
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_timeout_seconds: int = 30

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
