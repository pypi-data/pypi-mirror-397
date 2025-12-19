"""Tests for database module."""

from datetime import datetime

import pytest

from frappe_local_backup.database import Database, Team, Site, Backup


class TestDatabase:
    """Tests for Database class."""

    def test_database_initialization(self, test_db):
        """Test database is properly initialized."""
        assert test_db.db_path.exists()

    def test_tables_created(self, test_db):
        """Test that all required tables are created."""
        with test_db.get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row["name"] for row in cursor.fetchall()}
        
        assert "teams" in tables
        assert "sites" in tables
        assert "backups" in tables


class TestTeamOperations:
    """Tests for team CRUD operations."""

    def test_add_team(self, test_db, sample_team):
        """Test adding a new team."""
        team_id = test_db.add_team(sample_team)
        
        assert team_id is not None
        assert team_id > 0

    def test_get_team(self, test_db, sample_team):
        """Test retrieving a team by ID."""
        team_id = test_db.add_team(sample_team)
        
        retrieved = test_db.get_team(team_id)
        
        assert retrieved is not None
        assert retrieved.id == team_id
        assert retrieved.name == sample_team.name
        assert retrieved.enabled == sample_team.enabled

    def test_get_team_by_name(self, test_db, sample_team):
        """Test retrieving a team by name."""
        test_db.add_team(sample_team)
        
        retrieved = test_db.get_team_by_name(sample_team.name)
        
        assert retrieved is not None
        assert retrieved.name == sample_team.name

    def test_get_nonexistent_team(self, test_db):
        """Test retrieving a nonexistent team."""
        retrieved = test_db.get_team(9999)
        
        assert retrieved is None

    def test_get_all_teams(self, test_db):
        """Test retrieving all teams."""
        team1 = Team(id=None, name="team1", enabled=True)
        team2 = Team(id=None, name="team2", enabled=True)
        team3 = Team(id=None, name="team3", enabled=False)
        
        test_db.add_team(team1)
        test_db.add_team(team2)
        test_db.add_team(team3)
        
        # Get only enabled teams
        enabled_teams = test_db.get_all_teams(enabled_only=True)
        assert len(enabled_teams) == 2
        
        # Get all teams
        all_teams = test_db.get_all_teams(enabled_only=False)
        assert len(all_teams) == 3

    def test_update_team(self, test_db, sample_team):
        """Test updating a team."""
        team_id = test_db.add_team(sample_team)
        
        team = test_db.get_team(team_id)
        team.enabled = False
        test_db.update_team(team)
        
        updated = test_db.get_team(team_id)
        assert updated.enabled == False

    def test_delete_team(self, test_db, sample_team):
        """Test deleting a team."""
        team_id = test_db.add_team(sample_team)
        
        test_db.delete_team(team_id)
        
        deleted = test_db.get_team(team_id)
        assert deleted is None


class TestSiteOperations:
    """Tests for site CRUD operations."""

    def test_upsert_site_insert(self, test_db, sample_team, sample_site):
        """Test inserting a new site."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        
        site_id = test_db.upsert_site(sample_site)
        
        assert site_id is not None
        assert site_id > 0

    def test_upsert_site_update(self, test_db, sample_team, sample_site):
        """Test updating an existing site."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        
        site_id = test_db.upsert_site(sample_site)
        
        # Update the site
        sample_site.status = "Suspended"
        updated_id = test_db.upsert_site(sample_site)
        
        assert updated_id == site_id
        
        retrieved = test_db.get_site(site_id)
        assert retrieved.status == "Suspended"

    def test_get_site(self, test_db, sample_team, sample_site):
        """Test retrieving a site by ID."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        retrieved = test_db.get_site(site_id)
        
        assert retrieved is not None
        assert retrieved.name == sample_site.name

    def test_get_site_by_name(self, test_db, sample_team, sample_site):
        """Test retrieving a site by team and name."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        test_db.upsert_site(sample_site)
        
        retrieved = test_db.get_site_by_name(team_id, sample_site.name)
        
        assert retrieved is not None
        assert retrieved.name == sample_site.name

    def test_get_site_by_name_any_team(self, test_db, sample_team, sample_site):
        """Test retrieving a site by name across all teams."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        test_db.upsert_site(sample_site)
        
        retrieved = test_db.get_site_by_name_any_team(sample_site.name)
        
        assert retrieved is not None
        assert retrieved.name == sample_site.name

    def test_get_sites_by_team(self, test_db, sample_team):
        """Test retrieving all sites for a team."""
        team_id = test_db.add_team(sample_team)
        
        site1 = Site(id=None, team_id=team_id, name="site1.frappe.cloud", status="Active")
        site2 = Site(id=None, team_id=team_id, name="site2.frappe.cloud", status="Active")
        
        test_db.upsert_site(site1)
        test_db.upsert_site(site2)
        
        sites = test_db.get_sites_by_team(team_id)
        
        assert len(sites) == 2

    def test_get_all_sites(self, test_db, sample_team):
        """Test retrieving all sites."""
        team_id = test_db.add_team(sample_team)
        
        site1 = Site(id=None, team_id=team_id, name="site1.frappe.cloud", status="Active")
        site2 = Site(id=None, team_id=team_id, name="site2.frappe.cloud", status="Active")
        
        test_db.upsert_site(site1)
        test_db.upsert_site(site2)
        
        sites = test_db.get_all_sites()
        
        assert len(sites) == 2


class TestBackupOperations:
    """Tests for backup CRUD operations."""

    def test_add_backup(self, test_db, sample_team, sample_site):
        """Test adding a new backup."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        backup = Backup(
            id=None,
            site_id=site_id,
            backup_id="20241215_120000",
            creation=datetime.now(),
            status="completed",
        )
        
        backup_id = test_db.add_backup(backup)
        
        assert backup_id is not None
        assert backup_id > 0

    def test_get_backup(self, test_db, sample_team, sample_site):
        """Test retrieving a backup by ID."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        backup = Backup(
            id=None,
            site_id=site_id,
            backup_id="20241215_120000",
            creation=datetime.now(),
            status="completed",
            size_bytes=1024000,
        )
        backup_id = test_db.add_backup(backup)
        
        retrieved = test_db.get_backup(backup_id)
        
        assert retrieved is not None
        assert retrieved.backup_id == "20241215_120000"
        assert retrieved.size_bytes == 1024000

    def test_get_backup_by_backup_id(self, test_db, sample_team, sample_site):
        """Test retrieving a backup by site and backup_id."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        backup = Backup(
            id=None,
            site_id=site_id,
            backup_id="20241215_120000",
            creation=datetime.now(),
            status="completed",
        )
        test_db.add_backup(backup)
        
        retrieved = test_db.get_backup_by_backup_id(site_id, "20241215_120000")
        
        assert retrieved is not None
        assert retrieved.backup_id == "20241215_120000"

    def test_get_backups_by_site(self, test_db, sample_team, sample_site):
        """Test retrieving all backups for a site."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        for i in range(5):
            backup = Backup(
                id=None,
                site_id=site_id,
                backup_id=f"2024121{i}_120000",
                creation=datetime.now(),
                status="completed",
            )
            test_db.add_backup(backup)
        
        backups = test_db.get_backups_by_site(site_id, limit=3)
        
        assert len(backups) == 3

    def test_update_backup(self, test_db, sample_team, sample_site):
        """Test updating a backup."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        backup = Backup(
            id=None,
            site_id=site_id,
            backup_id="20241215_120000",
            creation=datetime.now(),
            status="downloading",
        )
        backup_id = test_db.add_backup(backup)
        
        backup.id = backup_id
        backup.status = "completed"
        backup.size_bytes = 2048000
        test_db.update_backup(backup)
        
        updated = test_db.get_backup(backup_id)
        assert updated.status == "completed"
        assert updated.size_bytes == 2048000

    def test_delete_backup(self, test_db, sample_team, sample_site):
        """Test deleting a backup."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        backup = Backup(
            id=None,
            site_id=site_id,
            backup_id="20241215_120000",
            creation=datetime.now(),
            status="completed",
        )
        backup_id = test_db.add_backup(backup)
        
        test_db.delete_backup(backup_id)
        
        deleted = test_db.get_backup(backup_id)
        assert deleted is None

    def test_get_old_backups(self, test_db, sample_team, sample_site):
        """Test retrieving old backups beyond retention limit."""
        team_id = test_db.add_team(sample_team)
        sample_site.team_id = team_id
        site_id = test_db.upsert_site(sample_site)
        
        # Add 5 backups
        for i in range(5):
            backup = Backup(
                id=None,
                site_id=site_id,
                backup_id=f"2024121{i}_120000",
                creation=datetime.now(),
                status="completed",
            )
            test_db.add_backup(backup)
        
        # Get backups beyond keeping 3
        old_backups = test_db.get_old_backups(site_id, keep_count=3)
        
        assert len(old_backups) == 2
