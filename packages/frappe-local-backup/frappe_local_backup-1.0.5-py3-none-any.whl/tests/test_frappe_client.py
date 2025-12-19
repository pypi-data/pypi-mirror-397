"""Tests for frappe_client module."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from frappe_local_backup.frappe_client import (
    FrappeCloudClient,
    FrappeSiteInfo,
    FrappeBackupInfo,
)


class TestFrappeCloudClient:
    """Tests for FrappeCloudClient class."""

    def test_client_initialization(self):
        """Test client is properly initialized."""
        client = FrappeCloudClient(
            api_key="test-key",
            api_secret="test-secret",
            team="test-team",
        )
        
        assert client.team == "test-team"
        assert client.base_url == "https://frappecloud.com"

    def test_client_custom_base_url(self):
        """Test client with custom base URL."""
        client = FrappeCloudClient(
            api_key="test-key",
            api_secret="test-secret",
            team="test-team",
            base_url="https://custom.frappe.cloud",
        )
        
        assert client.base_url == "https://custom.frappe.cloud"

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_request_headers(self, mock_session_class):
        """Test that requests have correct headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        client = FrappeCloudClient(
            api_key="test-key",
            api_secret="test-secret",
            team="test-team",
        )
        
        # Verify headers were set
        mock_session.headers.update.assert_called_once()
        call_args = mock_session.headers.update.call_args[0][0]
        
        assert "Authorization" in call_args
        assert call_args["Authorization"] == "Token test-key:test-secret"
        assert call_args["X-Press-Team"] == "test-team"


class TestGetSites:
    """Tests for get_sites method."""

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_get_sites_direct_list(self, mock_session_class):
        """Test parsing sites from direct list format."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock API response - direct list format
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": [
                {
                    "name": "site1.frappe.cloud",
                    "status": "Active",
                    "bench": "bench-1234",
                },
                {
                    "name": "site2.frappe.cloud",
                    "status": "Suspended",
                    "bench": "bench-5678",
                },
            ]
        }
        mock_session.request.return_value = mock_response
        
        client = FrappeCloudClient("key", "secret", "team")
        sites = client.get_sites()
        
        assert len(sites) == 2
        assert sites[0].name == "site1.frappe.cloud"
        assert sites[0].status == "Active"
        assert sites[1].name == "site2.frappe.cloud"
        assert sites[1].status == "Suspended"

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_get_sites_empty(self, mock_session_class):
        """Test handling empty sites list."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": []}
        mock_session.request.return_value = mock_response
        
        client = FrappeCloudClient("key", "secret", "team")
        sites = client.get_sites()
        
        assert len(sites) == 0


class TestGetBackups:
    """Tests for get_backups method."""

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_get_backups(self, mock_session_class):
        """Test parsing backups response."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": [
                {
                    "creation": "2024-12-15 12:00:30",
                    "database_url": "https://example.com/db.sql.gz",
                    "private_url": "https://example.com/private.tar",
                    "public_url": "https://example.com/public.tar",
                    "offsite": True,
                    "with_files": True,
                },
                {
                    "creation": "2024-12-14 12:00:30",
                    "database_url": "https://example.com/db2.sql.gz",
                    "offsite": False,
                    "with_files": False,
                },
            ]
        }
        mock_session.request.return_value = mock_response
        
        client = FrappeCloudClient("key", "secret", "team")
        backups = client.get_backups("site.frappe.cloud")
        
        assert len(backups) == 2
        assert backups[0].offsite == True
        assert backups[0].database_url == "https://example.com/db.sql.gz"
        assert backups[1].offsite == False


class TestTestConnection:
    """Tests for test_connection method."""

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_connection_success(self, mock_session_class):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"user": "test@example.com"}}
        mock_session.request.return_value = mock_response
        
        client = FrappeCloudClient("key", "secret", "team")
        result = client.test_connection()
        
        assert result == True

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_connection_failure(self, mock_session_class):
        """Test failed connection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_session.request.side_effect = Exception("Connection failed")
        
        client = FrappeCloudClient("key", "secret", "team")
        result = client.test_connection()
        
        assert result == False


class TestDetectTeam:
    """Tests for detect_team_from_credentials method."""

    @patch("frappe_local_backup.frappe_client.requests.Session")
    def test_detect_team_success(self, mock_session_class):
        """Test successful team detection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "team": {
                    "name": "detected-team-123",
                    "title": "My Team",
                },
                "user": {"email": "test@example.com"},
            }
        }
        mock_session.return_value.get.return_value = mock_response
        
        with patch("frappe_local_backup.frappe_client.requests.Session") as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            
            result = FrappeCloudClient.detect_team_from_credentials("key", "secret")
        
            assert result is not None
            assert result["name"] == "detected-team-123"

    @patch("frappe_local_backup.frappe_client.requests")
    def test_detect_team_failure(self, mock_requests):
        """Test failed team detection."""
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_session.get.side_effect = Exception("API error")
        
        result = FrappeCloudClient.detect_team_from_credentials("key", "secret")
        
        assert result is None


class TestFrappeSiteInfo:
    """Tests for FrappeSiteInfo dataclass."""

    def test_site_info_creation(self):
        """Test creating site info."""
        site = FrappeSiteInfo(
            name="test.frappe.cloud",
            status="Active",
            bench="bench-1234",
        )
        
        assert site.name == "test.frappe.cloud"
        assert site.status == "Active"
        assert site.bench == "bench-1234"


class TestFrappeBackupInfo:
    """Tests for FrappeBackupInfo dataclass."""

    def test_backup_info_creation(self):
        """Test creating backup info."""
        backup = FrappeBackupInfo(
            backup_id="20241215_120000",
            creation=datetime(2024, 12, 15, 12, 0, 0),
            database_url="https://example.com/db.sql.gz",
            offsite=True,
            with_files=True,
        )
        
        assert backup.backup_id == "20241215_120000"
        assert backup.offsite == True
        assert backup.database_url == "https://example.com/db.sql.gz"
