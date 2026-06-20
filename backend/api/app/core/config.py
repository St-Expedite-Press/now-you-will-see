"""Application-level settings loaded from environment and .env.studio file."""

from __future__ import annotations

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Path to the workspace root (where workspace.yaml lives)
    workspace_root: Path = Path(".")

    # FastAPI
    app_title: str = "Texgraph Studio"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Anthropic (for agent chat)
    anthropic_api_key: str = ""

    # Studio server
    host: str = "127.0.0.1"
    port: int = 8765

    @field_validator("workspace_root", mode="before")
    @classmethod
    def resolve_workspace(cls, v: object) -> Path:
        return Path(str(v)).resolve()

    model_config = {"env_file": ".env.studio", "env_file_encoding": "utf-8"}


settings = Settings()
