"""Frappe Cloud API client."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

# Separate logger for HTTP details
http_logger = logging.getLogger(__name__ + ".http")


@dataclass
class FrappeBackupInfo:
    """Backup information from Frappe Cloud."""

    backup_id: str
    creation: datetime
    database_url: Optional[str] = None
    private_url: Optional[str] = None
    public_url: Optional[str] = None
    config_url: Optional[str] = None
    offsite: bool = False
    with_files: bool = False


@dataclass
class FrappeSiteInfo:
    """Site information from Frappe Cloud."""

    name: str
    status: str
    bench: Optional[str] = None


class FrappeCloudClient:
    """Client for Frappe Cloud API."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        team: str,
        base_url: str = "https://frappecloud.com",
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.team = team
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Token {api_key}:{api_secret}",
                "X-Press-Team": team,
                "Content-Type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Make API request."""
        url = f"{self.base_url}/api/method/{endpoint}"

        # Log request details
        http_logger.debug(f"{'='*60}")
        http_logger.debug(f"REQUEST: {method} {url}")
        http_logger.debug(f"Headers: Authorization=Token ***:***, X-Press-Team={self.team}")
        if data:
            http_logger.debug(f"Body: {json.dumps(data, indent=2)}")
        if params:
            http_logger.debug(f"Params: {params}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30,
            )

            # Log response details
            http_logger.debug(f"RESPONSE: {response.status_code}")
            try:
                response_json = response.json()
                http_logger.debug(f"Body: {json.dumps(response_json, indent=2)}")
            except Exception:
                http_logger.debug(f"Body (text): {response.text[:500]}")
            http_logger.debug(f"{'='*60}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            http_logger.debug(f"ERROR: {e}")
            raise

    def get_sites(self) -> list[FrappeSiteInfo]:
        """Get all sites for the team."""
        response = self._request("GET", "press.api.site.all")
        sites = []

        message = response.get("message", [])

        # Handle both response formats:
        # 1. Direct list of sites: [{"name": "site1.frappe.cloud", ...}, ...]
        # 2. Grouped format: [{"sites": [...]}, ...]

        if message and isinstance(message, list):
            # Check if first item has 'sites' key (grouped format)
            if message and isinstance(message[0], dict) and "sites" in message[0]:
                # Grouped format
                for group in message:
                    for site_data in group.get("sites", []):
                        sites.append(
                            FrappeSiteInfo(
                                name=site_data["name"],
                                status=site_data.get("status", "Unknown"),
                                bench=site_data.get("bench"),
                            )
                        )
            else:
                # Direct list format
                for site_data in message:
                    if isinstance(site_data, dict) and "name" in site_data:
                        sites.append(
                            FrappeSiteInfo(
                                name=site_data["name"],
                                status=site_data.get("status", "Unknown"),
                                bench=site_data.get("bench"),
                            )
                        )

        return sites

    def get_site(self, site_name: str) -> Optional[dict]:
        """Get site details."""
        response = self._request("POST", "press.api.site.get", data={"name": site_name})
        return response.get("message")

    def get_backups(self, site_name: str) -> list[FrappeBackupInfo]:
        """Get backups for a site."""
        response = self._request("POST", "press.api.site.backups", data={"name": site_name})
        backups = []

        for backup_data in response.get("message", []):
            # Generate backup ID from creation timestamp
            creation_str = backup_data.get("creation", "")
            try:
                creation = datetime.fromisoformat(creation_str.replace(" ", "T"))
                backup_id = creation.strftime("%Y%m%d_%H%M%S")
            except (ValueError, AttributeError):
                backup_id = creation_str.replace(" ", "_").replace(":", "").replace("-", "")
                creation = datetime.now()

            backups.append(
                FrappeBackupInfo(
                    backup_id=backup_id,
                    creation=creation,
                    database_url=backup_data.get("database_url"),
                    private_url=backup_data.get("private_url"),
                    public_url=backup_data.get("public_url"),
                    config_url=backup_data.get("config_url"),
                    offsite=bool(backup_data.get("offsite", False)),
                    with_files=bool(backup_data.get("with_files", False)),
                )
            )

        return backups

    def get_site_config(self, site_name: str) -> Optional[dict]:
        """Get site configuration."""
        try:
            response = self._request("POST", "press.api.site.get_config", data={"name": site_name})
            return response.get("message")
        except Exception as e:
            logger.warning(f"Could not fetch site config for {site_name}: {e}")
            return None

    def get_login_sid(self, site_name: str) -> Optional[str]:
        """Get login SID for administrator access."""
        try:
            response = self._request("POST", "press.api.site.login", data={"name": site_name})
            message = response.get("message")

            # Handle different response formats
            if isinstance(message, str):
                # Direct SID string
                return message
            elif isinstance(message, dict):
                # Dict with sid key or redirect URL
                if "sid" in message:
                    return message["sid"]
                # Sometimes returns a redirect URL like https://site.frappe.cloud/desk?sid=xxx
                if "redirect" in message:
                    redirect_url = message["redirect"]
                    if "sid=" in redirect_url:
                        return redirect_url.split("sid=")[1].split("&")[0]
                # Log unexpected dict format
                http_logger.debug(f"Login response dict: {message}")

            logger.warning(f"Unexpected login response format for {site_name}: {type(message)}")
            return None
        except Exception as e:
            logger.warning(f"Could not get login SID for {site_name}: {e}")
            return None

    def get_remote_file_size(
        self,
        url: str,
        site_name: Optional[str] = None,
        use_auth: bool = False,
    ) -> Optional[int]:
        """Get file size from remote URL via HEAD request."""
        try:
            headers = {}
            cookies = {}

            if use_auth and site_name:
                sid = self.get_login_sid(site_name)
                if sid:
                    cookies["sid"] = sid

            response = requests.head(
                url,
                headers=headers,
                cookies=cookies,
                timeout=30,
                allow_redirects=True,
            )

            if response.status_code == 200:
                content_length = response.headers.get("content-length")
                if content_length:
                    return int(content_length)

            return None
        except Exception as e:
            logger.debug(f"Could not get remote file size for {url}: {e}")
            return None

    def download_file(
        self,
        url: str,
        destination: Path,
        site_name: Optional[str] = None,
        use_auth: bool = False,
        show_progress: bool = True,
        max_retries: int = 3,
    ) -> bool:
        """Download a file from URL to destination with progress indicator and retry logic."""

        for attempt in range(1, max_retries + 1):
            try:
                headers = {}
                cookies = {}

                # For onsite backups, we might need to authenticate via SID
                if use_auth and site_name:
                    sid = self.get_login_sid(site_name)
                    if sid:
                        cookies["sid"] = sid

                response = requests.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    stream=True,
                    timeout=300,  # 5 minutes timeout for large files
                )
                response.raise_for_status()

                destination.parent.mkdir(parents=True, exist_ok=True)

                # Get total file size if available
                total_size = int(response.headers.get("content-length", 0))
                filename = destination.name

                if show_progress and total_size > 0:
                    from rich.progress import (
                        Progress,
                        BarColumn,
                        DownloadColumn,
                        TransferSpeedColumn,
                        TimeRemainingColumn,
                        TextColumn,
                    )

                    with Progress(
                        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                        BarColumn(bar_width=30),
                        "[progress.percentage]{task.percentage:>3.1f}%",
                        "•",
                        DownloadColumn(),
                        "•",
                        TransferSpeedColumn(),
                        "•",
                        TimeRemainingColumn(),
                        transient=True,
                    ) as progress:
                        task = progress.add_task("download", filename=filename, total=total_size)

                        with open(destination, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                progress.update(task, advance=len(chunk))
                else:
                    # No progress bar (unknown size or disabled)
                    with open(destination, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                # Verify downloaded size matches expected
                if total_size > 0:
                    actual_size = destination.stat().st_size
                    if actual_size != total_size:
                        raise IOError(
                            f"Incomplete download: got {actual_size} bytes, expected {total_size}"
                        )

                return True

            except Exception as e:
                logger.warning(f"Download attempt {attempt}/{max_retries} failed for {url}: {e}")

                # Clean up partial download
                if destination.exists():
                    destination.unlink()

                if attempt < max_retries:
                    import time

                    wait_time = attempt * 5  # Exponential backoff: 5s, 10s, 15s
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to download {url} after {max_retries} attempts: {e}")
                    return False

        return False

    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            self._request("GET", "press.api.account.me")
            return True
        except Exception:
            return False

    def get_account_info(self) -> Optional[dict]:
        """Get account information including team details."""
        try:
            response = self._request("GET", "press.api.account.me")
            return response.get("message")
        except Exception as e:
            logger.warning(f"Could not get account info: {e}")
            return None

    def get_teams(self) -> list[dict]:
        """Get all teams the user has access to."""
        try:
            response = self._request("GET", "press.api.account.teams")
            return response.get("message", [])
        except Exception as e:
            logger.warning(f"Could not get teams: {e}")
            return []

    @classmethod
    def detect_team_from_credentials(
        cls,
        api_key: str,
        api_secret: str,
        base_url: str = "https://frappecloud.com",
    ) -> Optional[dict]:
        """Detect team information from API credentials.

        Returns dict with team info or None if detection fails.
        """
        try:
            # Create a temporary client without team header
            session = requests.Session()
            session.headers.update(
                {
                    "Authorization": f"Token {api_key}:{api_secret}",
                    "Content-Type": "application/json",
                }
            )

            # Try to get account info
            response = session.get(
                f"{base_url}/api/method/press.api.account.me",
                timeout=30,
            )
            response.raise_for_status()
            account_info = response.json().get("message", {})

            # Get team from account info
            team_name = account_info.get("team", {}).get("name")
            team_title = account_info.get("team", {}).get("title") or account_info.get(
                "team", {}
            ).get("team_title")

            if team_name:
                return {
                    "name": team_name,
                    "title": team_title,
                    "user": account_info.get("user", {}).get("email"),
                }

            # Try to get teams list
            response = session.get(
                f"{base_url}/api/method/press.api.account.teams",
                timeout=30,
            )
            if response.status_code == 200:
                teams = response.json().get("message", [])
                if teams:
                    # Return the first/default team
                    first_team = teams[0]
                    return {
                        "name": first_team.get("name"),
                        "title": first_team.get("title") or first_team.get("team_title"),
                        "user": account_info.get("user", {}).get("email"),
                        "all_teams": teams,
                    }

            return None
        except Exception as e:
            logger.warning(f"Could not detect team from credentials: {e}")
            return None
