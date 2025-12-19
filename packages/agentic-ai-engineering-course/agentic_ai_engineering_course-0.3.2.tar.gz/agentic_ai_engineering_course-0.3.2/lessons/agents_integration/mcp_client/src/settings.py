"""Client configuration settings."""

import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings for the MCP Client."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # Server settings and paths
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent, description="The root directory of the mcp_client project"
    )
    mcp_config_path: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "mcp_servers_config.json",
        description="Path to the MCP servers configuration file",
    )
    log_level: int = Field(default=logging.INFO, alias="LOG_LEVEL", description="The log level")
    log_level_dependencies: int = Field(
        default=logging.WARNING, alias="LOG_LEVEL_DEPENDENCIES", description="The log level for dependencies"
    )


# Global settings instance
settings = Settings()
