"""Command-line interface for the backup service."""

import getpass
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from . import __version__
from .api import app as fastapi_app
from .backup_service import BackupService
from .config import Settings, get_settings
from .credentials import get_credential_manager, CredentialManager
from .database import Database, Team
from .frappe_client import FrappeCloudClient

# Force encrypted keyring backend
os.environ["PYTHON_KEYRING_BACKEND"] = "keyrings.alt.file.EncryptedKeyring"

console = Console()


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Show INFO level logs
        debug: Show DEBUG level logs including HTTP request/response details
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=debug)],
    )
    
    http_logger = logging.getLogger("frappe_local_backup.frappe_client.http")
    http_logger.setLevel(logging.DEBUG if debug else logging.WARNING)


def get_service(
    settings: Optional[Settings] = None,
    cred_manager: Optional[CredentialManager] = None,
) -> BackupService:
    """Get backup service instance."""
    if settings is None:
        settings = get_settings()
    settings.ensure_directories()
    db = Database(settings.db_path)
    return BackupService(settings, db, cred_manager)


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-d", "--debug", is_flag=True, help="Enable debug output (includes API request/response details)")
@click.version_option(version=__version__, prog_name="frappe-backup")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool) -> None:
    """Frappe Local Backup Service - Backup your Frappe Cloud sites locally."""
    setup_logging(verbose, debug)
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug


# Team commands
@cli.group()
def team():
    """Manage Frappe Cloud teams."""
    pass


@team.command("add")
@click.option("--name", "-n", required=True, help="Team name (as shown in Frappe Cloud)")
@click.option("--api-key", "-k", required=True, help="API key")
@click.option("--api-secret", "-s", required=True, help="API secret")
def team_add(name: str, api_key: str, api_secret: str) -> None:
    """Add a new Frappe Cloud team."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)

    existing = service.db.get_team_by_name(name)
    if existing:
        console.print(f"[red]Team '{name}' already exists[/red]")
        sys.exit(1)

    console.print(f"Testing connection to team '{name}'...")
    client = FrappeCloudClient(api_key, api_secret, name)
    if not client.test_connection():
        console.print("[red]Failed to connect to Frappe Cloud. Check your credentials.[/red]")
        sys.exit(1)

    console.print("Storing credentials securely in system keyring...")
    cred_manager.store_credentials(name, api_key, api_secret)

    team_obj = Team(id=None, name=name, enabled=True)
    team_id = service.db.add_team(team_obj)
    console.print(f"[green]Team '{name}' added successfully (ID: {team_id})[/green]")
    console.print("[dim]Credentials stored securely in OS keyring[/dim]")


@team.command("list")
def team_list() -> None:
    """List all teams."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)
    teams = service.db.get_all_teams(enabled_only=False)

    if not teams:
        console.print("[yellow]No teams configured[/yellow]")
        return

    table = Table(title="Frappe Cloud Teams")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Enabled", style="yellow")
    table.add_column("Credentials", style="blue")
    table.add_column("Sites", style="magenta")

    for t in teams:
        sites = service.db.get_sites_by_team(t.id)
        has_creds = cred_manager.credentials_exist(t.name)
        table.add_row(
            str(t.id),
            t.name,
            "✓" if t.enabled else "✗",
            "✓ Secure" if has_creds else "✗ Missing",
            str(len(sites)),
        )

    console.print(table)


@team.command("remove")
@click.argument("team_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this team?")
def team_remove(team_id: int) -> None:
    """Remove a team."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)
    team_obj = service.db.get_team(team_id)

    if not team_obj:
        console.print(f"[red]Team with ID {team_id} not found[/red]")
        sys.exit(1)

    cred_manager.delete_credentials(team_obj.name)
    service.db.delete_team(team_id)
    console.print(f"[green]Team '{team_obj.name}' deleted (including credentials)[/green]")


@team.command("enable")
@click.argument("team_id", type=int)
def team_enable(team_id: int) -> None:
    """Enable a team."""
    service = get_service()
    team_obj = service.db.get_team(team_id)

    if not team_obj:
        console.print(f"[red]Team with ID {team_id} not found[/red]")
        sys.exit(1)

    team_obj.enabled = True
    service.db.update_team(team_obj)
    console.print(f"[green]Team '{team_obj.name}' enabled[/green]")


@team.command("disable")
@click.argument("team_id", type=int)
def team_disable(team_id: int) -> None:
    """Disable a team."""
    service = get_service()
    team_obj = service.db.get_team(team_id)

    if not team_obj:
        console.print(f"[red]Team with ID {team_id} not found[/red]")
        sys.exit(1)

    team_obj.enabled = False
    service.db.update_team(team_obj)
    console.print(f"[yellow]Team '{team_obj.name}' disabled[/yellow]")


@team.command("update-credentials")
@click.argument("team_id", type=int)
@click.option("--api-key", "-k", required=True, help="New API key")
@click.option("--api-secret", "-s", required=True, help="New API secret")
def team_update_credentials(team_id: int, api_key: str, api_secret: str) -> None:
    """Update credentials for a team."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)
    team_obj = service.db.get_team(team_id)

    if not team_obj:
        console.print(f"[red]Team with ID {team_id} not found[/red]")
        sys.exit(1)

    console.print(f"Testing new credentials for team '{team_obj.name}'...")
    client = FrappeCloudClient(api_key, api_secret, team_obj.name)
    if not client.test_connection():
        console.print("[red]Failed to connect with new credentials.[/red]")
        sys.exit(1)

    cred_manager.store_credentials(team_obj.name, api_key, api_secret)
    console.print(f"[green]Credentials updated for team '{team_obj.name}'[/green]")


# --- Site commands ---
@cli.group()
def site():
    """Manage sites."""
    pass


@site.command("list")
@click.option("--team-id", "-t", type=int, help="Filter by team ID")
def site_list(team_id: Optional[int]) -> None:
    """List all sites."""
    service = get_service()

    if team_id:
        sites = service.db.get_sites_by_team(team_id)
    else:
        sites = service.db.get_all_sites()

    if not sites:
        console.print("[yellow]No sites found[/yellow]")
        return

    table = Table(title="Sites")
    table.add_column("ID", style="cyan")
    table.add_column("Site Name", style="green")
    table.add_column("Team ID", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Backups", style="magenta")

    for s in sites:
        backups = service.db.get_backups_by_site(s.id)
        table.add_row(
            str(s.id),
            s.name,
            str(s.team_id),
            s.status or "Unknown",
            str(len(backups)),
        )

    console.print(table)


@site.command("sync")
@click.option("--team-id", "-t", type=int, help="Sync specific team")
def site_sync(team_id: Optional[int]) -> None:
    """Sync sites from Frappe Cloud."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)

    if team_id:
        team_obj = service.db.get_team(team_id)
        if not team_obj:
            console.print(f"[red]Team with ID {team_id} not found[/red]")
            sys.exit(1)
        console.print(f"Syncing sites for team '{team_obj.name}'...")
        sites = service.sync_sites(team_obj)
        console.print(f"[green]Synced {len(sites)} sites[/green]")
    else:
        console.print("Syncing sites for all teams...")
        result = service.sync_all_teams()
        total = sum(len(sites) for sites in result.values())
        console.print(f"[green]Synced {total} sites across {len(result)} teams[/green]")


# --- Backup commands ---
@cli.group()
def backup():
    """Manage backups."""
    pass


@backup.command("run")
@click.option("--team-id", "-t", type=int, help="Backup specific team by ID")
@click.option("--team-name", "-T", type=str, help="Backup specific team by name")
@click.option("--site-id", "-s", type=int, help="Backup specific site by ID")
@click.option("--site-name", "-n", type=str, help="Backup specific site by name (e.g., mysite.frappe.cloud)")
@click.option("--parallel", "-p", type=int, default=None, help="Number of parallel downloads (default: 3)")
@click.option("--force", "-f", is_flag=True, help="Force re-download, replacing files if sizes differ")
def backup_run(team_id: Optional[int], team_name: Optional[str], site_id: Optional[int], site_name: Optional[str], parallel: Optional[int], force: bool) -> None:
    """Run backup for sites."""
    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    service = get_service(cred_manager=cred_manager)
    
    if force:
        console.print("[yellow]Force mode: will re-download files if sizes differ[/yellow]")

    if site_name:
        site_obj = service.db.get_site_by_name_any_team(site_name)
        if not site_obj:
            console.print(f"[red]Site '{site_name}' not found. Did you sync sites?[/red]")
            sys.exit(1)
        team_obj = service.db.get_team(site_obj.team_id)
        console.print(f"Backing up site '{site_obj.name}'...")
        backups = service.backup_site(team_obj, site_obj, force=force)
        console.print(f"[green]Downloaded {len(backups)} backup(s)[/green]")
    elif site_id:
        site_obj = service.db.get_site(site_id)
        if not site_obj:
            console.print(f"[red]Site with ID {site_id} not found[/red]")
            sys.exit(1)
        team_obj = service.db.get_team(site_obj.team_id)
        console.print(f"Backing up site '{site_obj.name}'...")
        backups = service.backup_site(team_obj, site_obj, force=force)
        console.print(f"[green]Downloaded {len(backups)} backup(s)[/green]")
    elif team_name:
        team_obj = service.db.get_team_by_name(team_name)
        if not team_obj:
            console.print(f"[red]Team '{team_name}' not found[/red]")
            sys.exit(1)
        console.print(f"Backing up all sites in team '{team_obj.name}'...")
        result = service.backup_team(team_obj, parallel=parallel, force=force)
        total = sum(len(backups) for backups in result.values())
        console.print(f"[green]Downloaded {total} backup(s) for {len(result)} sites[/green]")
    elif team_id:
        team_obj = service.db.get_team(team_id)
        if not team_obj:
            console.print(f"[red]Team with ID {team_id} not found[/red]")
            sys.exit(1)
        console.print(f"Backing up all sites in team '{team_obj.name}'...")
        result = service.backup_team(team_obj, parallel=parallel, force=force)
        total = sum(len(backups) for backups in result.values())
        console.print(f"[green]Downloaded {total} backup(s) for {len(result)} sites[/green]")
    else:
        console.print("Backing up all teams...")
        result = service.backup_all(parallel=parallel, force=force)
        total = sum(
            len(backups)
            for team_result in result.values()
            for backups in team_result.values()
        )
        console.print(f"[green]Downloaded {total} backup(s)[/green]")

    deleted = service.cleanup_old_backups()
    if deleted:
        console.print(f"[yellow]Cleaned up {deleted} old backup(s)[/yellow]")


# --- Backup list and cleanup ---
@backup.command("list")
@click.option("--site-id", "-s", type=int, help="Filter by site ID")
@click.option("--limit", "-l", type=int, default=20, help="Limit results")
def backup_list(site_id: Optional[int], limit: int) -> None:
    """List backups."""
    service = get_service()

    if site_id:
        backups = service.db.get_backups_by_site(site_id, limit=limit)
    else:
        backups = service.db.get_all_backups()[:limit]

    if not backups:
        console.print("[yellow]No backups found[/yellow]")
        return

    table = Table(title="Backups")
    table.add_column("ID", style="cyan")
    table.add_column("Site ID", style="blue")
    table.add_column("Backup ID", style="green")
    table.add_column("Creation", style="yellow")
    table.add_column("Size", style="magenta")
    table.add_column("Status", style="red")

    for b in backups:
        size_mb = b.size_bytes / 1024 / 1024
        table.add_row(
            str(b.id),
            str(b.site_id),
            b.backup_id,
            str(b.creation)[:19],
            f"{size_mb:.2f} MB",
            b.status,
        )

    console.print(table)


@backup.command("cleanup")
@click.option("--max-backups", "-m", type=int, help="Override max backups to keep")
def backup_cleanup(max_backups: Optional[int]) -> None:
    """Clean up old backups."""
    service = get_service()
    deleted = service.cleanup_old_backups(max_backups)
    console.print(f"[green]Deleted {deleted} old backup(s)[/green]")


# Server commands
@cli.command()
@click.option("--host", "-h", default=None, help="API server host")
@click.option("--port", "-p", type=int, default=None, help="API server port")
def serve(host: Optional[str], port: Optional[int]) -> None:
    """Start the API server."""
    import uvicorn
    from apscheduler.schedulers.background import BackgroundScheduler

    try:
        cred_manager = get_credential_manager()
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    settings = get_settings()
    settings.ensure_directories()

    host = host or settings.api_host
    port = port or settings.api_port

    # Setup scheduler for automatic backups
    scheduler = BackgroundScheduler()
    service = get_service(settings, cred_manager)

    def scheduled_backup():
        console.print("[blue]Running scheduled backup...[/blue]")
        try:
            service.backup_all()
            service.cleanup_old_backups()
            console.print("[green]Scheduled backup complete[/green]")
        except Exception as e:
            console.print(f"[red]Scheduled backup failed: {e}[/red]")

    scheduler.add_job(
        scheduled_backup,
        "interval",
        hours=settings.backup_schedule_hours,
        id="backup_job",
    )
    scheduler.start()

    console.print(f"[green]Starting API server on {host}:{port}[/green]")
    console.print(f"[yellow]API Key: {settings.api_key}[/yellow]")
    console.print(f"[blue]Backup schedule: Every {settings.backup_schedule_hours} hours[/blue]")
    console.print("[dim]Credentials stored securely in OS keyring[/dim]")

    try:
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
    finally:
        scheduler.shutdown()


# Stats command
@cli.command()
def stats() -> None:
    """Show backup statistics."""
    service = get_service()
    stats_data = service.get_backup_stats()

    console.print("\n[bold]Backup Statistics[/bold]\n")
    console.print(f"Teams: {stats_data['teams']}")
    console.print(f"Sites: {stats_data['sites']}")
    console.print(f"Total Backups: {stats_data['backups']}")

    size_gb = stats_data["total_size_bytes"] / 1024 / 1024 / 1024
    console.print(f"Total Size: {size_gb:.2f} GB")

    if stats_data["team_details"]:
        console.print("\n[bold]Per Team:[/bold]")
        table = Table()
        table.add_column("Team", style="green")
        table.add_column("Enabled", style="yellow")
        table.add_column("Sites", style="blue")
        table.add_column("Backups", style="cyan")
        table.add_column("Size", style="magenta")

        for team_stat in stats_data["team_details"]:
            size_mb = team_stat["size_bytes"] / 1024 / 1024
            table.add_row(
                team_stat["name"],
                "✓" if team_stat["enabled"] else "✗",
                str(team_stat["sites"]),
                str(team_stat["backups"]),
                f"{size_mb:.2f} MB",
            )

        console.print(table)


# Config command
@cli.command()
def config() -> None:
    """Show current configuration."""
    settings = get_settings()

    console.print("\n[bold]Current Configuration[/bold]\n")
    console.print(f"Backup Root: {settings.backup_root.absolute()}")
    console.print(f"Database Path: {settings.db_path.absolute()}")
    console.print(f"Max Backups per Site: {settings.max_backups_per_site}")
    console.print(f"API Host: {settings.api_host}")
    console.print(f"API Port: {settings.api_port}")
    console.print(f"Backup Schedule: Every {settings.backup_schedule_hours} hours")
    console.print(f"Frappe Cloud URL: {settings.frappe_cloud_url}")
    console.print(f"\n[yellow]API Key: {settings.api_key}[/yellow]")
    console.print("\n[dim]Team credentials are stored securely in OS keyring[/dim]")


# Init command
@cli.command()
def init() -> None:
    """Initialize the backup service."""
    settings = get_settings()
    settings.ensure_directories()

    # Verify keyring is available
    try:
        get_credential_manager()
        console.print("[green]✓ OS keyring available for secure credential storage[/green]")
    except RuntimeError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print(
            "\n[yellow]If secure storage fails, you can set an explicit backend:[/yellow]\n"
            "  export PYTHON_KEYRING_BACKEND=keyrings.alt.file.EncryptedKeyring\n"
        )
        sys.exit(1)

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = f"""# Frappe Local Backup Configuration

# Paths
BACKUP_ROOT=./backups
DB_PATH=./data/backups.db

# Backup retention
MAX_BACKUPS_PER_SITE=3

# Parallel downloads
PARALLEL_DOWNLOADS=3

# API settings
API_HOST=0.0.0.0
API_PORT=8000
API_KEY={settings.api_key}

# Scheduler settings
BACKUP_SCHEDULE_HOURS=6

# Frappe Cloud API
FRAPPE_CLOUD_URL=https://frappecloud.com
"""
        env_file.write_text(env_content)
        console.print("[green]✓ Created .env file[/green]")

    console.print("\n[green]Directories created:[/green]")
    console.print(f"  - Backups: {settings.backup_root.absolute()}")
    console.print(f"  - Database: {settings.db_path.parent.absolute()}")
    console.print(f"\n[yellow]API Key: {settings.api_key}[/yellow]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Run interactive setup: frappe-backup setup")
    console.print("  2. Or add a team manually: frappe-backup team add -n <team> -k <api-key> -s <api-secret>")
    console.print("  3. Sync sites: frappe-backup site sync")
    console.print("  4. Run backup: frappe-backup backup run")
    console.print("  5. Start server: frappe-backup serve")
    console.print("\n[dim]Credentials will be stored securely in your OS keyring[/dim]")


# Interactive setup command
@cli.command()
def setup() -> None:
    """Interactive setup wizard - configure teams and credentials."""
    console.print("\n[bold cyan]═══ Frappe Local Backup Setup Wizard ═══[/bold cyan]\n")
    
    # Verify keyring first
    try:
        cred_manager = get_credential_manager()
        console.print("[green]✓ OS keyring available[/green]")
    except RuntimeError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print(
            "\n[yellow]If secure storage fails, you can set an explicit backend:[/yellow]\n"
            "  export PYTHON_KEYRING_BACKEND=keyrings.alt.file.EncryptedKeyring\n"
        )
        sys.exit(1)
    
    # Step 0: Configure paths
    console.print("\n[bold]Step 0: Configure Storage[/bold]")
    
    env_file = Path(".env")
    current_backup_root = "./backups"
    current_db_path = "./data/backups.db"
    current_max_backups = 3
    current_parallel = 3
    current_schedule = 6
    
    # Load existing .env values if present
    if env_file.exists():
        console.print("[dim]Found existing .env file, loading current values...[/dim]")
        env_content = env_file.read_text()
        for line in env_content.splitlines():
            if line.startswith("BACKUP_ROOT="):
                current_backup_root = line.split("=", 1)[1].strip()
            elif line.startswith("DB_PATH="):
                current_db_path = line.split("=", 1)[1].strip()
            elif line.startswith("MAX_BACKUPS_PER_SITE="):
                try:
                    current_max_backups = int(line.split("=", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("PARALLEL_DOWNLOADS="):
                try:
                    current_parallel = int(line.split("=", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("BACKUP_SCHEDULE_HOURS="):
                try:
                    current_schedule = int(line.split("=", 1)[1].strip())
                except ValueError:
                    pass
    
    # Ask for backup folder path
    console.print("\n[dim]Where should backups be stored?[/dim]")
    console.print("[dim]You can use absolute paths (e.g., /mnt/backups) or relative paths (e.g., ./backups)[/dim]")
    backup_root = click.prompt("Backup folder path", default=current_backup_root)
    
    # Expand and validate the path
    backup_path = Path(backup_root).expanduser()
    if not backup_path.is_absolute():
        backup_path = Path.cwd() / backup_path
    
    # Create directory if it doesn't exist
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Backup folder: {backup_path.absolute()}[/green]")
    except PermissionError:
        console.print(f"[red]✗ Cannot create directory: {backup_path} (Permission denied)[/red]")
        console.print("[yellow]Please choose a different path or create the directory manually.[/yellow]")
        sys.exit(1)
    
    # Ask for database path
    console.print("\n[dim]Where should the database file be stored?[/dim]")
    db_path = click.prompt("Database file path", default=current_db_path)
    
    db_file_path = Path(db_path).expanduser()
    if not db_file_path.is_absolute():
        db_file_path = Path.cwd() / db_file_path
    
    try:
        db_file_path.parent.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Database path: {db_file_path.absolute()}[/green]")
    except PermissionError:
        console.print(f"[red]✗ Cannot create directory: {db_file_path.parent} (Permission denied)[/red]")
        sys.exit(1)
    
    # Ask for max backups per site
    console.print("\n[dim]How many backups should be kept per site?[/dim]")
    max_backups = click.prompt("Max backups per site", default=current_max_backups, type=int)
    
    # Ask for parallel downloads
    console.print("\n[dim]How many sites should be backed up in parallel?[/dim]")
    parallel_downloads = click.prompt("Parallel downloads", default=current_parallel, type=int)
    
    # Ask for schedule
    console.print("\n[dim]How often should automatic backups run (in hours)?[/dim]")
    schedule_hours = click.prompt("Backup schedule (hours)", default=current_schedule, type=int)
    
    # Generate API key if not exists
    settings = get_settings()
    api_key = settings.api_key
    
    # Write .env file
    env_content = f"""# Frappe Local Backup Configuration

# Paths
BACKUP_ROOT={backup_root}
DB_PATH={db_path}

# Backup retention
MAX_BACKUPS_PER_SITE={max_backups}

# Parallel downloads
PARALLEL_DOWNLOADS={parallel_downloads}

# API settings (for REST API access)
API_HOST=0.0.0.0
API_PORT=8000
API_KEY={api_key}

# Scheduler settings
BACKUP_SCHEDULE_HOURS={schedule_hours}

# Frappe Cloud API
FRAPPE_CLOUD_URL=https://frappecloud.com
"""
    env_file.write_text(env_content)
    console.print("[green]✓ Configuration saved to .env[/green]")
    
    # Reload settings with new values
    settings = get_settings()
    settings.ensure_directories()
    service = get_service(cred_manager=cred_manager)
    
    # Ask for number of teams
    console.print("\n[bold]Step 1: Configure Teams[/bold]")
    console.print("[dim]You can get API credentials from Frappe Cloud → Settings → API Access[/dim]\n")
    
    num_teams = click.prompt("How many Frappe Cloud teams do you want to configure?", type=int, default=1)
    
    teams_added = 0
    for i in range(num_teams):
        console.print(f"\n[bold]── Team {i + 1} of {num_teams} ──[/bold]")
        
        team_api_key = click.prompt("API Key", hide_input=False)
        team_api_secret = click.prompt("API Secret", hide_input=True)
        
        # Auto-detect team info
        console.print("[dim]Detecting team information...[/dim]")
        team_info = FrappeCloudClient.detect_team_from_credentials(team_api_key, team_api_secret)
        
        if team_info:
            team_name = team_info.get("name")
            team_title = team_info.get("title") or team_name
            user_email = team_info.get("user", "unknown")
            
            console.print(f"[green]✓ Detected team: {team_title} ({team_name})[/green]")
            console.print(f"[dim]  User: {user_email}[/dim]")
            
            # Check if multiple teams available
            all_teams = team_info.get("all_teams", [])
            if len(all_teams) > 1:
                console.print(f"\n[yellow]Multiple teams found ({len(all_teams)}):[/yellow]")
                for idx, t in enumerate(all_teams, 1):
                    t_name = t.get("name")
                    t_title = t.get("title") or t.get("team_title") or t_name
                    console.print(f"  {idx}. {t_title} ({t_name})")
                
                selection = click.prompt(
                    "Select team number (or 0 for all teams)", 
                    type=int, 
                    default=1
                )
                
                if selection == 0:
                    # Add all teams
                    for t in all_teams:
                        t_name = t.get("name")
                        if not service.db.get_team_by_name(t_name):
                            team_obj = Team(id=None, name=t_name, enabled=True)
                            service.db.add_team(team_obj)
                            cred_manager.store_credentials(t_name, team_api_key, team_api_secret)
                            teams_added += 1
                            console.print(f"[green]✓ Added team: {t_name}[/green]")
                        else:
                            console.print(f"[yellow]Team '{t_name}' already exists, skipping[/yellow]")
                    continue
                elif 1 <= selection <= len(all_teams):
                    team_name = all_teams[selection - 1].get("name")
            
            # Add selected team
            if service.db.get_team_by_name(team_name):
                console.print(f"[yellow]Team '{team_name}' already exists[/yellow]")
                if click.confirm("Update credentials?", default=False):
                    cred_manager.store_credentials(team_name, team_api_key, team_api_secret)
                    console.print(f"[green]✓ Credentials updated for {team_name}[/green]")
            else:
                # Verify connection with team header
                client = FrappeCloudClient(team_api_key, team_api_secret, team_name)
                if client.test_connection():
                    team_obj = Team(id=None, name=team_name, enabled=True)
                    service.db.add_team(team_obj)
                    cred_manager.store_credentials(team_name, team_api_key, team_api_secret)
                    teams_added += 1
                    console.print(f"[green]✓ Team '{team_name}' added successfully[/green]")
                else:
                    console.print(f"[red]✗ Failed to connect with team '{team_name}'[/red]")
        else:
            console.print("[red]✗ Could not detect team from credentials[/red]")
            team_name = click.prompt("Enter team name manually")
            
            client = FrappeCloudClient(team_api_key, team_api_secret, team_name)
            if client.test_connection():
                if not service.db.get_team_by_name(team_name):
                    team_obj = Team(id=None, name=team_name, enabled=True)
                    service.db.add_team(team_obj)
                    cred_manager.store_credentials(team_name, team_api_key, team_api_secret)
                    teams_added += 1
                    console.print(f"[green]✓ Team '{team_name}' added[/green]")
                else:
                    console.print("[yellow]Team already exists[/yellow]")
            else:
                console.print("[red]✗ Connection failed. Please verify credentials.[/red]")
    
    console.print("\n[bold]Step 2: Sync Sites[/bold]")
    if teams_added > 0 or service.db.get_all_teams():
        if click.confirm("Sync sites from Frappe Cloud now?", default=True):
            result = service.sync_all_teams()
            total_sites = sum(len(sites) for sites in result.values())
            console.print(f"[green]✓ Synced {total_sites} sites across {len(result)} teams[/green]")
    
    # Summary
    console.print("\n[bold cyan]═══ Setup Complete ═══[/bold cyan]")
    console.print(f"\n[green]✓ {teams_added} team(s) configured[/green]")
    console.print("[green]✓ Credentials stored in OS keyring[/green]")
    console.print("\n[bold]Quick commands:[/bold]")
    console.print("  frappe-backup backup run      # Run backup now")
    console.print("  frappe-backup backup run -p 5 # Parallel backup (5 sites)")
    console.print("  frappe-backup site list       # List all sites")
    console.print("  frappe-backup serve           # Start API server with scheduler")
    console.print("  frappe-backup install-service # Install as systemd service")


# Install systemd service command
@cli.command("install-service")
@click.option("--user", "-u", default=None, help="User to run service as (default: current user)")
@click.option("--schedule", "-s", default=6, type=int, help="Backup schedule in hours (default: 6)")
def install_service(user: Optional[str], schedule: int) -> None:
    """Generate and optionally install systemd service file."""
    current_user = user or getpass.getuser()
    working_dir = Path.cwd().absolute()
    venv_path = Path(sys.executable).parent.parent
    exec_path = Path(sys.executable).parent / "frappe-backup"
    
    service_content = f"""[Unit]
Description=Frappe Local Backup Service
After=network.target

[Service]
Type=simple
User={current_user}
WorkingDirectory={working_dir}
Environment=PATH={venv_path}/bin:/usr/bin:/bin
Environment=BACKUP_SCHEDULE_HOURS={schedule}
ExecStart={exec_path} serve
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("frappe-backup.service")
    service_file.write_text(service_content)
    console.print(f"[green]✓ Generated service file: {service_file.absolute()}[/green]")
    
    console.print("\n[bold]Service Configuration:[/bold]")
    console.print(f"  User: {current_user}")
    console.print(f"  Working Directory: {working_dir}")
    console.print(f"  Backup Schedule: Every {schedule} hours")
    console.print(f"  Executable: {exec_path}")
    
    console.print("\n[bold]To install as system service:[/bold]")
    console.print(f"  sudo cp {service_file.absolute()} /etc/systemd/system/")
    console.print("  sudo systemctl daemon-reload")
    console.print("  sudo systemctl enable frappe-backup")
    console.print("  sudo systemctl start frappe-backup")
    
    console.print("\n[bold]To check status:[/bold]")
    console.print("  sudo systemctl status frappe-backup")
    console.print("  sudo journalctl -u frappe-backup -f")
    
    if os.geteuid() == 0:
        console.print("\n[green]Running as root - you can install directly:[/green]")
        console.print(f"  cp {service_file.absolute()} /etc/systemd/system/")
        console.print("  systemctl daemon-reload && systemctl enable frappe-backup && systemctl start frappe-backup")


if __name__ == "__main__":
    cli()