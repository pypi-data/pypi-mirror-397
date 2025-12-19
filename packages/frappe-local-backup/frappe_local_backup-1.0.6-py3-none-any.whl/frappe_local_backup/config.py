"""Configuration management for the backup service."""

import secrets
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    backup_root: Path = Field(
        default=Path("./backups"),
        description="Root directory for storing backups",
    )
    db_path: Path = Field(
        default=Path("./data/backups.db"),
        description="Path to SQLite database file",
    )

    # Backup retention
    max_backups_per_site: int = Field(
        default=3,
        description="Maximum number of backups to keep per site",
        ge=1,
    )

    # API settings
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="API key for authentication",
    )

    # Scheduler settings
    backup_schedule_hours: int = Field(
        default=6,
        description="Run backup every N hours",
        ge=1,
    )

    # Parallel downloads
    parallel_downloads: int = Field(
        default=3,
        description="Number of sites to backup simultaneously",
        ge=1,
        le=10,
    )

    # Frappe Cloud API
    frappe_cloud_url: str = Field(
        default="https://frappecloud.com",
        description="Frappe Cloud base URL",
    )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.backup_root.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
