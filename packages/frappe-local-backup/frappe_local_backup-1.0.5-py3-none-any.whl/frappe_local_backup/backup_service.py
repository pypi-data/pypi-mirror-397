"""Main backup service logic."""

import json
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import Settings
from .credentials import get_credential_manager, CredentialManager
from .database import Backup, Database, Site, Team
from .frappe_client import FrappeCloudClient, FrappeBackupInfo

logger = logging.getLogger(__name__)


class BackupService:
    """Main backup service orchestrator."""

    def __init__(
        self,
        settings: Settings,
        db: Database,
        cred_manager: Optional[CredentialManager] = None,
    ):
        self.settings = settings
        self.db = db
        self.cred_manager = cred_manager or get_credential_manager()

    def get_client_for_team(self, team: Team) -> FrappeCloudClient:
        """Create API client for a team."""
        creds = self.cred_manager.get_credentials(team.name)
        if not creds:
            raise RuntimeError(
                f"No credentials found for team '{team.name}'. "
                f"Add them with: frappe-backup team add -n {team.name} -k <api-key> -s <api-secret>"
            )

        return FrappeCloudClient(
            api_key=creds.api_key,
            api_secret=creds.api_secret,
            team=team.name,
            base_url=self.settings.frappe_cloud_url,
        )

    def get_site_backup_dir(self, team: Team, site: Site) -> Path:
        """Get the backup directory for a site."""
        return self.settings.backup_root / team.name / site.name

    def sync_sites(self, team: Team) -> list[Site]:
        """Sync sites from Frappe Cloud for a team."""
        logger.info(f"Syncing sites for team: {team.name}")
        client = self.get_client_for_team(team)

        try:
            frappe_sites = client.get_sites()
        except Exception as e:
            logger.error(f"Failed to fetch sites for team {team.name}: {e}")
            return []

        sites = []
        for fs in frappe_sites:
            site = Site(
                id=None,
                team_id=team.id,
                name=fs.name,
                bench=fs.bench,
                status=fs.status,
            )
            site.id = self.db.upsert_site(site)
            sites.append(site)
            logger.debug(f"Synced site: {fs.name}")

        logger.info(f"Synced {len(sites)} sites for team {team.name}")
        return sites

    def sync_all_teams(self) -> dict[str, list[Site]]:
        """Sync sites for all enabled teams."""
        result = {}
        for team in self.db.get_all_teams(enabled_only=True):
            result[team.name] = self.sync_sites(team)
        return result

    def download_backup(
        self,
        team: Team,
        site: Site,
        backup_info: FrappeBackupInfo,
        force: bool = False,
    ) -> Optional[Backup]:
        """Download a backup for a site.

        Args:
            team: Team object
            site: Site object
            backup_info: Backup info from Frappe Cloud
            force: If True, re-download even if can't verify remote size

        Note: Size verification is always performed. If local file size differs
        from remote, the file will be re-downloaded regardless of force flag.
        """
        logger.info(f"Downloading backup {backup_info.backup_id} for {site.name}")

        # Check if already downloaded
        existing = self.db.get_backup_by_backup_id(site.id, backup_info.backup_id)

        # Create backup directory
        backup_dir = self.get_site_backup_dir(team, site) / backup_info.backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        client = self.get_client_for_team(team)

        # Check if we need to download anything (size verification)
        needs_download = False
        if not existing or existing.status != "completed":
            needs_download = True
        else:
            # Existing completed backup - verify file integrity via size check
            files_to_check = [
                (backup_info.database_url, backup_dir / "database.sql.gz"),
                (backup_info.private_url, backup_dir / "private-files.tar"),
                (backup_info.public_url, backup_dir / "public-files.tar"),
            ]
            for url, local_path in files_to_check:
                if url and self._should_download_file(
                    client, url, local_path, site.name, not backup_info.offsite, force
                ):
                    needs_download = True
                    break

        if not needs_download:
            logger.info(f"Backup {backup_info.backup_id} already downloaded and verified")
            return existing

        # Create or update backup record
        backup = Backup(
            id=existing.id if existing else None,
            site_id=site.id,
            backup_id=backup_info.backup_id,
            creation=backup_info.creation,
            status="downloading",
        )

        if not existing:
            backup.id = self.db.add_backup(backup)
        else:
            backup.id = existing.id
            self.db.update_backup(backup)

        total_size = 0
        success = True

        # Download database
        if backup_info.database_url:
            db_file = backup_dir / "database.sql.gz"
            if self._should_download_file(
                client, backup_info.database_url, db_file, site.name, True, force
            ):
                if client.download_file(
                    backup_info.database_url,
                    db_file,
                    site_name=site.name,
                    use_auth=True,  # Always use authentication for backup downloads
                ):
                    backup.database_file = str(db_file.relative_to(self.settings.backup_root))
                    total_size += db_file.stat().st_size
                    logger.debug(f"Downloaded database: {db_file}")
                else:
                    success = False
                    logger.error(f"Failed to download database for {site.name}")
            elif db_file.exists():
                backup.database_file = str(db_file.relative_to(self.settings.backup_root))
                total_size += db_file.stat().st_size
                logger.info(f"Skipped database (same size): {db_file.name}")

        # Download private files
        if backup_info.private_url:
            private_file = backup_dir / "private-files.tar"
            if self._should_download_file(
                client,
                backup_info.private_url,
                private_file,
                site.name,
                True,
                force,
            ):
                if client.download_file(
                    backup_info.private_url,
                    private_file,
                    site_name=site.name,
                    use_auth=True,  # Always use authentication for backup downloads
                ):
                    backup.private_files = str(private_file.relative_to(self.settings.backup_root))
                    total_size += private_file.stat().st_size
                    logger.debug(f"Downloaded private files: {private_file}")
                else:
                    logger.warning(f"Failed to download private files for {site.name}")
            elif private_file.exists():
                backup.private_files = str(private_file.relative_to(self.settings.backup_root))
                total_size += private_file.stat().st_size
                logger.info(f"Skipped private files (same size): {private_file.name}")

        # Download public files
        if backup_info.public_url:
            public_file = backup_dir / "public-files.tar"
            if self._should_download_file(
                client,
                backup_info.public_url,
                public_file,
                site.name,
                True,
                force,
            ):
                if client.download_file(
                    backup_info.public_url,
                    public_file,
                    site_name=site.name,
                    use_auth=True,  # Always use authentication for backup downloads
                ):
                    backup.public_files = str(public_file.relative_to(self.settings.backup_root))
                    total_size += public_file.stat().st_size
                    logger.debug(f"Downloaded public files: {public_file}")
                else:
                    logger.warning(f"Failed to download public files for {site.name}")
            elif public_file.exists():
                backup.public_files = str(public_file.relative_to(self.settings.backup_root))
                total_size += public_file.stat().st_size
                logger.info(f"Skipped public files (same size): {public_file.name}")

        # Get and save site config
        site_config = client.get_site_config(site.name)
        if site_config:
            config_file = backup_dir / "site_config.json"
            with open(config_file, "w") as f:
                json.dump(site_config, f, indent=2)
            backup.site_config = str(config_file.relative_to(self.settings.backup_root))
            total_size += config_file.stat().st_size
            logger.debug(f"Saved site config: {config_file}")

        # Update backup record
        backup.size_bytes = total_size
        backup.downloaded_at = datetime.now()
        backup.status = "completed" if success else "failed"
        self.db.update_backup(backup)

        if success:
            logger.info(
                f"Completed backup {backup_info.backup_id} for {site.name} "
                f"({total_size / 1024 / 1024:.2f} MB)"
            )
        else:
            logger.error(f"Backup {backup_info.backup_id} for {site.name} failed")

        return backup

    def _should_download_file(
        self,
        client: FrappeCloudClient,
        url: str,
        local_path: Path,
        site_name: str,
        use_auth: bool,
        force: bool,
    ) -> bool:
        """Check if file should be downloaded based on size comparison.

        Returns True if:
        - Local file doesn't exist
        - Local file size differs from remote (incomplete/corrupted download)
        - Force mode is enabled and can't determine remote size
        """
        if not local_path.exists():
            return True

        # Always check size comparison for safety (catches incomplete downloads)
        remote_size = client.get_remote_file_size(url, site_name, use_auth)
        local_size = local_path.stat().st_size

        if remote_size is None:
            # Can't determine remote size
            if force:
                # In force mode, download anyway
                logger.debug(
                    f"Can't determine remote size for {local_path.name}, will re-download (force mode)"
                )
                return True
            else:
                # Without force, trust the existing file
                logger.debug(
                    f"Can't determine remote size for {local_path.name}, keeping existing file"
                )
                return False

        if remote_size != local_size:
            logger.info(
                f"Size mismatch for {local_path.name}: local={local_size}, remote={remote_size} - will re-download"
            )
            return True

        # Sizes match - file is complete
        return False

    def backup_site(self, team: Team, site: Site, force: bool = False) -> list[Backup]:
        """Download latest backups for a site.

        Args:
            team: Team object
            site: Site object
            force: If True, re-download files if sizes differ from remote
        """
        logger.info(f"Backing up site: {site.name}")
        client = self.get_client_for_team(team)

        try:
            frappe_backups = client.get_backups(site.name)
        except Exception as e:
            logger.error(f"Failed to fetch backups for {site.name}: {e}")
            return []

        if not frappe_backups:
            logger.warning(f"No backups found for {site.name}")
            return []

        # Sort all backups by creation (newest first)
        frappe_backups.sort(key=lambda x: x.creation, reverse=True)

        # Prefer offsite backups, fall back to onsite if none available
        offsite_backups = [b for b in frappe_backups if b.offsite]
        onsite_backups = [b for b in frappe_backups if not b.offsite]

        if offsite_backups:
            latest_backup = offsite_backups[0]
            logger.info(f"Using offsite backup for {site.name}")
        elif onsite_backups:
            latest_backup = onsite_backups[0]
            logger.info(f"No offsite backups for {site.name}, falling back to onsite backup")
        else:
            logger.warning(f"No downloadable backups found for {site.name}")
            return []

        # Download the latest backup if not already downloaded (or force re-download)
        downloaded = []
        existing = self.db.get_backup_by_backup_id(site.id, latest_backup.backup_id)
        if not existing or existing.status != "completed" or force:
            backup = self.download_backup(team, site, latest_backup, force=force)
            if backup:
                downloaded.append(backup)

        return downloaded

    def backup_team(
        self, team: Team, parallel: Optional[int] = None, force: bool = False
    ) -> dict[str, list[Backup]]:
        """Backup all sites for a team (with parallel downloads).

        Args:
            team: Team object
            parallel: Number of parallel downloads
            force: If True, re-download files if sizes differ from remote
        """
        logger.info(f"Backing up team: {team.name}")
        result = {}

        # First sync sites
        sites = self.sync_sites(team)

        # Filter active sites
        active_sites = [s for s in sites if s.status == "Active"]
        inactive_count = len(sites) - len(active_sites)

        if inactive_count:
            logger.info(f"Skipping {inactive_count} inactive site(s)")

        if not active_sites:
            return result

        # Determine parallelism
        max_workers = parallel or self.settings.parallel_downloads
        max_workers = min(max_workers, len(active_sites))  # Don't exceed site count

        if max_workers > 1:
            logger.info(f"Backing up {len(active_sites)} sites with {max_workers} parallel workers")

            def backup_site_wrapper(site: Site) -> tuple[str, list[Backup]]:
                return site.name, self.backup_site(team, site, force=force)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(backup_site_wrapper, site): site for site in active_sites
                }

                for future in as_completed(futures):
                    site = futures[future]
                    try:
                        site_name, backups = future.result()
                        result[site_name] = backups
                    except Exception as e:
                        logger.error(f"Failed to backup site {site.name}: {e}")
                        result[site.name] = []
        else:
            # Sequential fallback
            for site in active_sites:
                result[site.name] = self.backup_site(team, site, force=force)

        return result

    def backup_all(
        self, parallel: Optional[int] = None, force: bool = False
    ) -> dict[str, dict[str, list[Backup]]]:
        """Backup all sites for all enabled teams.

        Args:
            parallel: Number of parallel downloads
            force: If True, re-download files if sizes differ from remote
        """
        logger.info("Starting backup for all teams")
        result = {}

        for team in self.db.get_all_teams(enabled_only=True):
            result[team.name] = self.backup_team(team, parallel=parallel, force=force)

        logger.info("Completed backup for all teams")
        return result

    def cleanup_old_backups(self, max_backups: Optional[int] = None) -> int:
        """Remove old backups exceeding retention limit."""
        if max_backups is None:
            max_backups = self.settings.max_backups_per_site

        logger.info(f"Cleaning up old backups (keeping {max_backups} per site)")
        deleted_count = 0

        for team in self.db.get_all_teams(enabled_only=False):
            for site in self.db.get_sites_by_team(team.id):
                old_backups = self.db.get_old_backups(site.id, max_backups)

                for backup in old_backups:
                    # Delete files
                    backup_dir = self.get_site_backup_dir(team, site) / backup.backup_id
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                        logger.debug(f"Deleted backup directory: {backup_dir}")

                    # Delete record
                    self.db.delete_backup(backup.id)
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup.backup_id} for {site.name}")

        logger.info(f"Cleanup complete. Deleted {deleted_count} old backups")
        return deleted_count

    def get_backup_stats(self) -> dict:
        """Get backup statistics."""
        teams = self.db.get_all_teams(enabled_only=False)
        total_sites = 0
        total_backups = 0
        total_size = 0

        team_stats = []
        for team in teams:
            sites = self.db.get_sites_by_team(team.id)
            team_size = 0
            team_backup_count = 0

            for site in sites:
                backups = self.db.get_backups_by_site(site.id)
                team_backup_count += len(backups)
                for backup in backups:
                    team_size += backup.size_bytes

            team_stats.append(
                {
                    "name": team.name,
                    "enabled": team.enabled,
                    "sites": len(sites),
                    "backups": team_backup_count,
                    "size_bytes": team_size,
                }
            )

            total_sites += len(sites)
            total_backups += team_backup_count
            total_size += team_size

        return {
            "teams": len(teams),
            "sites": total_sites,
            "backups": total_backups,
            "total_size_bytes": total_size,
            "team_details": team_stats,
        }
