"""Tests for config module."""

import os
from pathlib import Path

import pytest

from frappe_local_backup.config import Settings, get_settings


class TestSettings:
    """Tests for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.backup_root == Path("./backups")
        assert settings.db_path == Path("./data/backups.db")
        assert settings.max_backups_per_site == 3
        assert settings.parallel_downloads == 3
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.backup_schedule_hours == 6
        assert settings.frappe_cloud_url == "https://frappecloud.com"

    def test_custom_settings(self, temp_dir):
        """Test custom settings values."""
        settings = Settings(
            backup_root=temp_dir / "custom_backups",
            db_path=temp_dir / "custom.db",
            max_backups_per_site=5,
            parallel_downloads=10,
        )
        
        assert settings.backup_root == temp_dir / "custom_backups"
        assert settings.db_path == temp_dir / "custom.db"
        assert settings.max_backups_per_site == 5
        assert settings.parallel_downloads == 10

    def test_ensure_directories(self, test_settings):
        """Test that ensure_directories creates required directories."""
        assert not test_settings.backup_root.exists()
        assert not test_settings.db_path.parent.exists()
        
        test_settings.ensure_directories()
        
        assert test_settings.backup_root.exists()
        assert test_settings.db_path.parent.exists()

    def test_api_key_auto_generated(self):
        """Test that API key is auto-generated if not provided."""
        settings = Settings()
        
        assert settings.api_key is not None
        assert len(settings.api_key) > 20  # Should be a secure random token

    def test_settings_from_env(self, temp_dir, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("BACKUP_ROOT", str(temp_dir / "env_backups"))
        monkeypatch.setenv("MAX_BACKUPS_PER_SITE", "10")
        monkeypatch.setenv("PARALLEL_DOWNLOADS", "5")
        
        settings = Settings()
        
        assert settings.backup_root == temp_dir / "env_backups"
        assert settings.max_backups_per_site == 10
        assert settings.parallel_downloads == 5


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns a Settings object."""
        settings = get_settings()
        
        assert isinstance(settings, Settings)
