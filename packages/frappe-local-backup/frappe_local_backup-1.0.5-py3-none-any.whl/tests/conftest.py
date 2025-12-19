"""Shared test fixtures."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from frappe_local_backup.config import Settings
from frappe_local_backup.database import Database, Team, Site, Backup


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_settings(temp_dir):
    """Create test settings with temporary directories."""
    return Settings(
        backup_root=temp_dir / "backups",
        db_path=temp_dir / "data" / "test.db",
        max_backups_per_site=3,
        parallel_downloads=2,
        api_host="127.0.0.1",
        api_port=8000,
        api_key="test-api-key-12345",
        backup_schedule_hours=6,
        frappe_cloud_url="https://frappecloud.com",
    )


@pytest.fixture
def test_db(test_settings):
    """Create a test database."""
    test_settings.ensure_directories()
    db = Database(test_settings.db_path)
    yield db
    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_team():
    """Create a sample team object."""
    return Team(
        id=None,
        name="test-team-123",
        enabled=True,
    )


@pytest.fixture
def sample_site():
    """Create a sample site object."""
    return Site(
        id=None,
        team_id=1,
        name="testsite.frappe.cloud",
        bench="bench-1234-000001",
        status="Active",
    )


@pytest.fixture
def mock_credentials():
    """Mock credential manager."""
    with patch("frappe_local_backup.credentials.get_credential_manager") as mock:
        cred_manager = MagicMock()
        cred_manager.get_credentials.return_value = MagicMock(
            api_key="test-api-key",
            api_secret="test-api-secret",
        )
        mock.return_value = cred_manager
        yield cred_manager


@pytest.fixture
def mock_frappe_client():
    """Mock Frappe Cloud client."""
    with patch("frappe_local_backup.frappe_client.FrappeCloudClient") as mock:
        client = MagicMock()
        client.test_connection.return_value = True
        client.get_sites.return_value = []
        client.get_backups.return_value = []
        mock.return_value = client
        yield client


@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch("frappe_local_backup.frappe_client.requests") as mock:
        yield mock
