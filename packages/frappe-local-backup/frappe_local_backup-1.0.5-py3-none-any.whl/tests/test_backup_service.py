"""Tests for backup_service module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from frappe_local_backup.backup_service import BackupService
from frappe_local_backup.database import Team, Site, Backup
from frappe_local_backup.frappe_client import FrappeSiteInfo, FrappeBackupInfo


class TestBackupService:
    """Tests for BackupService class."""

    def test_service_initialization(self, test_settings, test_db, mock_credentials):
        """Test service is properly initialized."""
        service = BackupService(
            settings=test_settings,
            db=test_db,
            cred_manager=mock_credentials,
        )
        
        assert service.settings == test_settings
        assert service.db == test_db

    def test_get_site_backup_dir(self, test_settings, test_db, mock_credentials):
        """Test backup directory path generation."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        team = Team(id=1, name="test-team", enabled=True)
        site = Site(id=1, team_id=1, name="site.frappe.cloud", status="Active")
        
        backup_dir = service.get_site_backup_dir(team, site)
        
        expected = test_settings.backup_root / "test-team" / "site.frappe.cloud"
        assert backup_dir == expected


class TestSyncSites:
    """Tests for sync_sites method."""

    def test_sync_sites_adds_new_sites(self, test_settings, test_db, mock_credentials):
        """Test that sync adds new sites to database."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Add team first
        team = Team(id=None, name="test-team", enabled=True)
        team_id = test_db.add_team(team)
        team.id = team_id
        
        # Mock the Frappe client
        with patch.object(service, "get_client_for_team") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_sites.return_value = [
                FrappeSiteInfo(name="site1.frappe.cloud", status="Active", bench="bench-1"),
                FrappeSiteInfo(name="site2.frappe.cloud", status="Active", bench="bench-2"),
            ]
            mock_get_client.return_value = mock_client
            
            sites = service.sync_sites(team)
        
        assert len(sites) == 2
        
        # Verify sites in database
        db_sites = test_db.get_sites_by_team(team_id)
        assert len(db_sites) == 2

    def test_sync_sites_updates_existing(self, test_settings, test_db, mock_credentials):
        """Test that sync updates existing sites."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Add team and site
        team = Team(id=None, name="test-team", enabled=True)
        team_id = test_db.add_team(team)
        team.id = team_id
        
        existing_site = Site(
            id=None, team_id=team_id, name="site1.frappe.cloud",
            status="Active", bench="old-bench"
        )
        test_db.upsert_site(existing_site)
        
        # Mock client returns updated status
        with patch.object(service, "get_client_for_team") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_sites.return_value = [
                FrappeSiteInfo(name="site1.frappe.cloud", status="Suspended", bench="new-bench"),
            ]
            mock_get_client.return_value = mock_client
            
            sites = service.sync_sites(team)
        
        # Verify site was updated
        updated_site = test_db.get_site_by_name(team_id, "site1.frappe.cloud")
        assert updated_site.status == "Suspended"
        assert updated_site.bench == "new-bench"


class TestBackupSite:
    """Tests for backup_site method."""

    def test_backup_site_skips_existing(self, test_settings, test_db, mock_credentials):
        """Test that backup skips already downloaded backups."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Setup team, site, and existing backup
        team = Team(id=None, name="test-team", enabled=True)
        team_id = test_db.add_team(team)
        team.id = team_id
        
        site = Site(id=None, team_id=team_id, name="site.frappe.cloud", status="Active")
        site_id = test_db.upsert_site(site)
        site.id = site_id
        
        existing_backup = Backup(
            id=None, site_id=site_id, backup_id="20241215_120000",
            creation=datetime.now(), status="completed"
        )
        test_db.add_backup(existing_backup)
        
        # Mock client returns same backup
        with patch.object(service, "get_client_for_team") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_backups.return_value = [
                FrappeBackupInfo(
                    backup_id="20241215_120000",
                    creation=datetime.now(),
                    offsite=True,
                    with_files=True,
                ),
            ]
            # Mock size check to return no download needed
            mock_client.get_remote_file_size.return_value = None
            mock_get_client.return_value = mock_client
            
            downloaded = service.backup_site(team, site)
        
        # Should not download anything
        assert len(downloaded) == 0

    def test_backup_site_prefers_offsite(self, test_settings, test_db, mock_credentials):
        """Test that backup prefers offsite backups."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Setup
        team = Team(id=None, name="test-team", enabled=True)
        team_id = test_db.add_team(team)
        team.id = team_id
        
        site = Site(id=None, team_id=team_id, name="site.frappe.cloud", status="Active")
        site_id = test_db.upsert_site(site)
        site.id = site_id
        
        with patch.object(service, "get_client_for_team") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_backups.return_value = [
                FrappeBackupInfo(
                    backup_id="20241215_120000",
                    creation=datetime(2024, 12, 15, 12, 0),
                    offsite=False,  # Onsite - newer
                    with_files=True,
                ),
                FrappeBackupInfo(
                    backup_id="20241214_120000",
                    creation=datetime(2024, 12, 14, 12, 0),
                    offsite=True,  # Offsite - older but preferred
                    with_files=True,
                ),
            ]
            mock_get_client.return_value = mock_client
            
            with patch.object(service, "download_backup") as mock_download:
                mock_download.return_value = MagicMock()
                service.backup_site(team, site)
                
                # Verify offsite backup was chosen
                call_args = mock_download.call_args[0]
                assert call_args[2].backup_id == "20241214_120000"
                assert call_args[2].offsite == True


class TestCleanupOldBackups:
    """Tests for cleanup_old_backups method."""

    def test_cleanup_removes_old_backups(self, test_settings, test_db, mock_credentials):
        """Test that cleanup removes backups beyond retention limit."""
        test_settings.max_backups_per_site = 2
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Setup
        team = Team(id=None, name="test-team", enabled=True)
        team_id = test_db.add_team(team)
        
        site = Site(id=None, team_id=team_id, name="site.frappe.cloud", status="Active")
        site_id = test_db.upsert_site(site)
        
        # Add 5 backups
        for i in range(5):
            backup = Backup(
                id=None, site_id=site_id, backup_id=f"2024121{i}_120000",
                creation=datetime.now(), status="completed"
            )
            test_db.add_backup(backup)
        
        # Run cleanup
        deleted_count = service.cleanup_old_backups(max_backups=2)
        
        # Should have deleted 3 backups
        assert deleted_count == 3
        
        # Should have 2 remaining
        remaining = test_db.get_backups_by_site(site_id)
        assert len(remaining) == 2


class TestShouldDownloadFile:
    """Tests for _should_download_file method."""

    def test_should_download_if_not_exists(self, test_settings, test_db, mock_credentials, temp_dir):
        """Test returns True if local file doesn't exist."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        mock_client = MagicMock()
        local_path = temp_dir / "nonexistent.sql.gz"
        
        result = service._should_download_file(
            mock_client, "https://example.com/file.sql.gz",
            local_path, "site.frappe.cloud", False, False
        )
        
        assert result == True

    def test_should_download_if_size_mismatch(self, test_settings, test_db, mock_credentials, temp_dir):
        """Test returns True if local file size differs from remote."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Create local file with specific size
        local_path = temp_dir / "file.sql.gz"
        local_path.write_bytes(b"x" * 1000)  # 1000 bytes
        
        mock_client = MagicMock()
        mock_client.get_remote_file_size.return_value = 2000  # Different size
        
        result = service._should_download_file(
            mock_client, "https://example.com/file.sql.gz",
            local_path, "site.frappe.cloud", False, False
        )
        
        assert result == True

    def test_should_not_download_if_size_matches(self, test_settings, test_db, mock_credentials, temp_dir):
        """Test returns False if local file size matches remote."""
        service = BackupService(test_settings, test_db, mock_credentials)
        
        # Create local file
        local_path = temp_dir / "file.sql.gz"
        local_path.write_bytes(b"x" * 1000)
        
        mock_client = MagicMock()
        mock_client.get_remote_file_size.return_value = 1000  # Same size
        
        result = service._should_download_file(
            mock_client, "https://example.com/file.sql.gz",
            local_path, "site.frappe.cloud", False, False
        )
        
        assert result == False
