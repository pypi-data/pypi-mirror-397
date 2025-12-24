"""Configuration management for hwdocs-mcp."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_hwdocs_dir() -> Path:
    """Get the hwdocs configuration directory."""
    return Path.home() / ".hwdocs"


def get_manuals_dir() -> Path:
    """Get the directory where manuals are stored."""
    return get_hwdocs_dir() / "manuals"


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return get_hwdocs_dir() / "config.json"


class Config(BaseModel):
    """Configuration for hwdocs-mcp."""

    api_token: str | None = Field(default=None, description="API token for cloud services")
    api_base: str = Field(
        default="https://hwdocs-production.up.railway.app",
        description="Base URL for the cloud API",
    )

    @classmethod
    def load(cls) -> Config:
        """Load configuration from file, or return defaults."""
        config_path = get_config_path()
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                return cls.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                pass
        return cls()

    def save(self) -> None:
        """Save configuration to file."""
        config_path = get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(self.model_dump(exclude_none=True), indent=2),
            encoding="utf-8",
        )

    def has_cloud_access(self) -> bool:
        """Check if cloud features are available."""
        return self.api_token is not None


class ServerSettings(BaseSettings):
    """Server settings from environment variables."""

    model_config = SettingsConfigDict(env_prefix="HWDOCS_")

    debug: bool = False
    log_level: str = "INFO"
