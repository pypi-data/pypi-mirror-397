"""SQLite database models and operations."""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional


@dataclass
class Team:
    """Frappe Cloud team configuration."""

    id: Optional[int]
    name: str
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Site:
    """Frappe Cloud site."""

    id: Optional[int]
    team_id: int
    name: str
    bench: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Backup:
    """Backup record."""

    id: Optional[int]
    site_id: int
    backup_id: str  # Unique ID from Frappe Cloud
    creation: datetime
    database_file: Optional[str] = None
    private_files: Optional[str] = None
    public_files: Optional[str] = None
    site_config: Optional[str] = None
    size_bytes: int = 0
    downloaded_at: Optional[datetime] = None
    status: str = "pending"  # pending, downloading, completed, failed


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    bench TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    UNIQUE(team_id, name)
                );

                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id INTEGER NOT NULL,
                    backup_id TEXT NOT NULL,
                    creation TIMESTAMP NOT NULL,
                    database_file TEXT,
                    private_files TEXT,
                    public_files TEXT,
                    site_config TEXT,
                    size_bytes INTEGER DEFAULT 0,
                    downloaded_at TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE,
                    UNIQUE(site_id, backup_id)
                );

                CREATE INDEX IF NOT EXISTS idx_sites_team ON sites(team_id);
                CREATE INDEX IF NOT EXISTS idx_backups_site ON backups(site_id);
                CREATE INDEX IF NOT EXISTS idx_backups_creation ON backups(creation);
            """
            )

            # Migration: remove api_key and api_secret columns if they exist
            cursor = conn.execute("PRAGMA table_info(teams)")
            columns = [row[1] for row in cursor.fetchall()]

            if "api_key" in columns or "api_secret" in columns:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS teams_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        enabled INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    INSERT INTO teams_new (id, name, enabled, created_at, updated_at)
                    SELECT id, name, enabled, created_at, updated_at FROM teams;
                    
                    DROP TABLE teams;
                    
                    ALTER TABLE teams_new RENAME TO teams;
                """
                )

    # Team operations
    def add_team(self, team: Team) -> int:
        """Add a new team."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO teams (name, enabled)
                   VALUES (?, ?)""",
                (team.name, team.enabled),
            )
            return cursor.lastrowid

    def get_team(self, team_id: int) -> Optional[Team]:
        """Get team by ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM teams WHERE id = ?", (team_id,)).fetchone()
            return self._row_to_team(row) if row else None

    def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get team by name."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM teams WHERE name = ?", (name,)).fetchone()
            return self._row_to_team(row) if row else None

    def get_all_teams(self, enabled_only: bool = True) -> list[Team]:
        """Get all teams."""
        with self.get_connection() as conn:
            query = "SELECT * FROM teams"
            if enabled_only:
                query += " WHERE enabled = 1"
            rows = conn.execute(query).fetchall()
            return [self._row_to_team(row) for row in rows]

    def update_team(self, team: Team) -> None:
        """Update team."""
        with self.get_connection() as conn:
            conn.execute(
                """UPDATE teams SET name = ?, enabled = ?, 
                   updated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (team.name, team.enabled, team.id),
            )

    def delete_team(self, team_id: int) -> None:
        """Delete team and all associated data."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))

    # Site operations
    def upsert_site(self, site: Site) -> int:
        """Insert or update a site."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO sites (team_id, name, bench, status)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(team_id, name) DO UPDATE SET
                   bench = excluded.bench,
                   status = excluded.status,
                   updated_at = CURRENT_TIMESTAMP""",
                (site.team_id, site.name, site.bench, site.status),
            )
            if cursor.lastrowid:
                return cursor.lastrowid
            row = conn.execute(
                "SELECT id FROM sites WHERE team_id = ? AND name = ?",
                (site.team_id, site.name),
            ).fetchone()
            return row["id"]

    def get_site(self, site_id: int) -> Optional[Site]:
        """Get site by ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
            return self._row_to_site(row) if row else None

    def get_site_by_name(self, team_id: int, name: str) -> Optional[Site]:
        """Get site by team and name."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM sites WHERE team_id = ? AND name = ?",
                (team_id, name),
            ).fetchone()
            return self._row_to_site(row) if row else None

    def get_site_by_name_any_team(self, name: str) -> Optional[Site]:
        """Get site by name (search across all teams)."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM sites WHERE name = ?",
                (name,),
            ).fetchone()
            return self._row_to_site(row) if row else None

    def get_sites_by_team(self, team_id: int) -> list[Site]:
        """Get all sites for a team."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM sites WHERE team_id = ?", (team_id,)).fetchall()
            return [self._row_to_site(row) for row in rows]

    def get_all_sites(self) -> list[Site]:
        """Get all sites."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM sites").fetchall()
            return [self._row_to_site(row) for row in rows]

    # Backup operations
    def add_backup(self, backup: Backup) -> int:
        """Add a new backup record."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT OR IGNORE INTO backups
                   (site_id, backup_id, creation, database_file, private_files,
                    public_files, site_config, size_bytes, downloaded_at, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    backup.site_id,
                    backup.backup_id,
                    backup.creation,
                    backup.database_file,
                    backup.private_files,
                    backup.public_files,
                    backup.site_config,
                    backup.size_bytes,
                    backup.downloaded_at,
                    backup.status,
                ),
            )
            return cursor.lastrowid

    def update_backup(self, backup: Backup) -> None:
        """Update backup record."""
        with self.get_connection() as conn:
            conn.execute(
                """UPDATE backups SET
                   database_file = ?, private_files = ?, public_files = ?,
                   site_config = ?, size_bytes = ?, downloaded_at = ?, status = ?
                   WHERE id = ?""",
                (
                    backup.database_file,
                    backup.private_files,
                    backup.public_files,
                    backup.site_config,
                    backup.size_bytes,
                    backup.downloaded_at,
                    backup.status,
                    backup.id,
                ),
            )

    def get_backup(self, backup_id: int) -> Optional[Backup]:
        """Get backup by ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM backups WHERE id = ?", (backup_id,)).fetchone()
            return self._row_to_backup(row) if row else None

    def get_backup_by_backup_id(self, site_id: int, backup_id: str) -> Optional[Backup]:
        """Get backup by site and backup_id."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM backups WHERE site_id = ? AND backup_id = ?",
                (site_id, backup_id),
            ).fetchone()
            return self._row_to_backup(row) if row else None

    def get_backups_by_site(self, site_id: int, limit: Optional[int] = None) -> list[Backup]:
        """Get backups for a site, ordered by creation date (newest first)."""
        with self.get_connection() as conn:
            query = """SELECT * FROM backups WHERE site_id = ?
                       ORDER BY creation DESC"""
            if limit:
                query += f" LIMIT {limit}"
            rows = conn.execute(query, (site_id,)).fetchall()
            return [self._row_to_backup(row) for row in rows]

    def get_old_backups(self, site_id: int, keep_count: int) -> list[Backup]:
        """Get backups older than the newest `keep_count` for a site."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM backups WHERE site_id = ?
                   ORDER BY creation DESC LIMIT -1 OFFSET ?""",
                (site_id, keep_count),
            ).fetchall()
            return [self._row_to_backup(row) for row in rows]

    def delete_backup(self, backup_id: int) -> None:
        """Delete a backup record."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM backups WHERE id = ?", (backup_id,))

    def get_all_backups(self) -> list[Backup]:
        """Get all backups."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM backups ORDER BY creation DESC").fetchall()
            return [self._row_to_backup(row) for row in rows]

    # Helper methods
    def _row_to_team(self, row: sqlite3.Row) -> Team:
        return Team(
            id=row["id"],
            name=row["name"],
            enabled=bool(row["enabled"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_site(self, row: sqlite3.Row) -> Site:
        return Site(
            id=row["id"],
            team_id=row["team_id"],
            name=row["name"],
            bench=row["bench"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_backup(self, row: sqlite3.Row) -> Backup:
        return Backup(
            id=row["id"],
            site_id=row["site_id"],
            backup_id=row["backup_id"],
            creation=row["creation"],
            database_file=row["database_file"],
            private_files=row["private_files"],
            public_files=row["public_files"],
            site_config=row["site_config"],
            size_bytes=row["size_bytes"],
            downloaded_at=row["downloaded_at"],
            status=row["status"],
        )
