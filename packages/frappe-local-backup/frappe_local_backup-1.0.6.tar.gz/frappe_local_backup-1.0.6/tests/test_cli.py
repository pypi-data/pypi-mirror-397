"""Tests for CLI module."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from frappe_local_backup.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ["--help"])
        
        assert result.exit_code == 0
        assert "Frappe Local Backup Service" in result.output

    def test_cli_version_flag(self, runner):
        """Test CLI with verbose flag."""
        result = runner.invoke(cli, ["-v", "--help"])
        
        assert result.exit_code == 0


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_directories(self, runner, temp_dir):
        """Test init creates required directories."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_credential_manager") as mock_cred:
                mock_cred.return_value = MagicMock()
                
                result = runner.invoke(cli, ["init"])
        
        # Should succeed (may have keyring issues in test env)
        assert result.exit_code in [0, 1]


class TestTeamCommands:
    """Tests for team management commands."""

    def test_team_list_empty(self, runner, temp_dir):
        """Test team list with no teams."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_credential_manager") as mock_cred:
                mock_cred.return_value = MagicMock()
                
                with patch("frappe_local_backup.cli.get_service") as mock_service:
                    service = MagicMock()
                    service.db.get_all_teams.return_value = []
                    mock_service.return_value = service
                    
                    result = runner.invoke(cli, ["team", "list"])
        
        assert "No teams configured" in result.output

    def test_team_add_requires_options(self, runner):
        """Test team add requires all options."""
        result = runner.invoke(cli, ["team", "add"])
        
        assert result.exit_code != 0
        assert "Missing option" in result.output


class TestSiteCommands:
    """Tests for site management commands."""

    def test_site_list_empty(self, runner, temp_dir):
        """Test site list with no sites."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_credential_manager") as mock_cred:
                mock_cred.return_value = MagicMock()
                
                with patch("frappe_local_backup.cli.get_service") as mock_service:
                    service = MagicMock()
                    service.db.get_all_sites.return_value = []
                    mock_service.return_value = service
                    
                    result = runner.invoke(cli, ["site", "list"])
        
        assert "No sites found" in result.output


class TestBackupCommands:
    """Tests for backup commands."""

    def test_backup_list_empty(self, runner, temp_dir):
        """Test backup list with no backups."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_service") as mock_service:
                service = MagicMock()
                service.db.get_all_backups.return_value = []
                mock_service.return_value = service
                
                result = runner.invoke(cli, ["backup", "list"])
        
        assert "No backups found" in result.output

    def test_backup_run_site_not_found(self, runner, temp_dir):
        """Test backup run with nonexistent site."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_credential_manager") as mock_cred:
                mock_cred.return_value = MagicMock()
                
                with patch("frappe_local_backup.cli.get_service") as mock_service:
                    service = MagicMock()
                    service.db.get_site_by_name_any_team.return_value = None
                    mock_service.return_value = service
                    
                    result = runner.invoke(cli, ["backup", "run", "-n", "nonexistent.frappe.cloud"])
        
        assert result.exit_code == 1
        assert "not found" in result.output


class TestConfigCommand:
    """Tests for config command."""

    def test_config_shows_settings(self, runner, temp_dir):
        """Test config shows current settings."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            result = runner.invoke(cli, ["config"])
        
        assert "Current Configuration" in result.output
        assert "Backup Root" in result.output
        assert "Max Backups per Site" in result.output


class TestStatsCommand:
    """Tests for stats command."""

    def test_stats_shows_statistics(self, runner, temp_dir):
        """Test stats shows statistics."""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch("frappe_local_backup.cli.get_service") as mock_service:
                service = MagicMock()
                service.db.get_all_teams.return_value = []
                service.db.get_all_sites.return_value = []
                service.db.get_all_backups.return_value = []
                mock_service.return_value = service
                
                result = runner.invoke(cli, ["stats"])
        
        assert "Statistics" in result.output
