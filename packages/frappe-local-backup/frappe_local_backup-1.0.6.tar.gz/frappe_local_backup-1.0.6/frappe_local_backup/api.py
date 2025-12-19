"""FastAPI REST API for backup service."""

import logging
from datetime import datetime
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader

from .backup_service import BackupService
from .config import Settings, get_settings
from .database import Database, Team
from pydantic import BaseModel


logger = logging.getLogger(__name__)

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_db(settings: Annotated[Settings, Depends(get_settings)]) -> Database:
    """Get database instance."""
    settings.ensure_directories()
    return Database(settings.db_path)


def get_backup_service(
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Database, Depends(get_db)],
) -> BackupService:
    """Get backup service instance."""
    return BackupService(settings, db)


async def verify_api_key(
    api_key: Annotated[str | None, Depends(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> str:
    """Verify API key."""
    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key


# Pydantic models
class TeamCreate(BaseModel):
    name: str
    api_key: str
    api_secret: str
    enabled: bool = True


class TeamResponse(BaseModel):
    id: int
    name: str
    enabled: bool
    created_at: Optional[str] = None


class SiteResponse(BaseModel):
    id: int
    team_id: int
    name: str
    bench: Optional[str] = None
    status: Optional[str] = None


class BackupResponse(BaseModel):
    id: int
    site_id: int
    backup_id: str
    creation: str
    database_file: Optional[str] = None
    private_files: Optional[str] = None
    public_files: Optional[str] = None
    site_config: Optional[str] = None
    size_bytes: int
    status: str
    downloaded_at: Optional[str] = None


class StatsResponse(BaseModel):
    teams: int
    sites: int
    backups: int
    total_size_bytes: int
    total_size_human: str
    team_details: list[dict]


class MessageResponse(BaseModel):
    message: str


# Create FastAPI app
app = FastAPI(
    title="Frappe Local Backup API",
    description="API for managing Frappe Cloud backups",
    version="1.0.0",
)


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


# Health check (no auth required)
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Team endpoints
@app.get(
    "/api/teams",
    response_model=list[TeamResponse],
    tags=["Teams"],
    dependencies=[Depends(verify_api_key)],
)
async def list_teams(db: Annotated[Database, Depends(get_db)]):
    """List all teams."""
    teams = db.get_all_teams(enabled_only=False)
    return [
        TeamResponse(
            id=t.id,
            name=t.name,
            enabled=t.enabled,
            created_at=str(t.created_at) if t.created_at else None,
        )
        for t in teams
    ]


@app.post(
    "/api/teams",
    response_model=TeamResponse,
    tags=["Teams"],
    dependencies=[Depends(verify_api_key)],
)
async def create_team(team: TeamCreate, db: Annotated[Database, Depends(get_db)]):
    """Create a new team."""
    existing = db.get_team_by_name(team.name)
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")

    team_obj = Team(
        id=None,
        name=team.name,
        api_key=team.api_key,
        api_secret=team.api_secret,
        enabled=team.enabled,
    )
    team_id = db.add_team(team_obj)
    team_obj.id = team_id

    return TeamResponse(id=team_id, name=team.name, enabled=team.enabled)


@app.delete(
    "/api/teams/{team_id}",
    response_model=MessageResponse,
    tags=["Teams"],
    dependencies=[Depends(verify_api_key)],
)
async def delete_team(team_id: int, db: Annotated[Database, Depends(get_db)]):
    """Delete a team."""
    team = db.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete_team(team_id)
    return MessageResponse(message=f"Team {team.name} deleted")


# Site endpoints
@app.get(
    "/api/sites",
    response_model=list[SiteResponse],
    tags=["Sites"],
    dependencies=[Depends(verify_api_key)],
)
async def list_sites(
    db: Annotated[Database, Depends(get_db)],
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
):
    """List all sites."""
    if team_id:
        sites = db.get_sites_by_team(team_id)
    else:
        sites = db.get_all_sites()

    return [
        SiteResponse(
            id=s.id,
            team_id=s.team_id,
            name=s.name,
            bench=s.bench,
            status=s.status,
        )
        for s in sites
    ]


@app.post(
    "/api/sites/sync",
    response_model=MessageResponse,
    tags=["Sites"],
    dependencies=[Depends(verify_api_key)],
)
async def sync_sites(
    background_tasks: BackgroundTasks,
    service: Annotated[BackupService, Depends(get_backup_service)],
    team_id: Optional[int] = Query(None, description="Sync specific team"),
):
    """Sync sites from Frappe Cloud."""
    if team_id:
        team = service.db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        background_tasks.add_task(service.sync_sites, team)
        return MessageResponse(message=f"Syncing sites for team {team.name}")
    else:
        background_tasks.add_task(service.sync_all_teams)
        return MessageResponse(message="Syncing sites for all teams")


# Backup endpoints
@app.get(
    "/api/backups",
    response_model=list[BackupResponse],
    tags=["Backups"],
    dependencies=[Depends(verify_api_key)],
)
async def list_backups(
    db: Annotated[Database, Depends(get_db)],
    site_id: Optional[int] = Query(None, description="Filter by site ID"),
):
    """List all backups."""
    if site_id:
        backups = db.get_backups_by_site(site_id)
    else:
        backups = db.get_all_backups()

    return [
        BackupResponse(
            id=b.id,
            site_id=b.site_id,
            backup_id=b.backup_id,
            creation=str(b.creation),
            database_file=b.database_file,
            private_files=b.private_files,
            public_files=b.public_files,
            site_config=b.site_config,
            size_bytes=b.size_bytes,
            status=b.status,
            downloaded_at=str(b.downloaded_at) if b.downloaded_at else None,
        )
        for b in backups
    ]


@app.get(
    "/api/backups/{backup_id}",
    response_model=BackupResponse,
    tags=["Backups"],
    dependencies=[Depends(verify_api_key)],
)
async def get_backup(backup_id: int, db: Annotated[Database, Depends(get_db)]):
    """Get backup details."""
    backup = db.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")

    return BackupResponse(
        id=backup.id,
        site_id=backup.site_id,
        backup_id=backup.backup_id,
        creation=str(backup.creation),
        database_file=backup.database_file,
        private_files=backup.private_files,
        public_files=backup.public_files,
        site_config=backup.site_config,
        size_bytes=backup.size_bytes,
        status=backup.status,
        downloaded_at=str(backup.downloaded_at) if backup.downloaded_at else None,
    )


@app.post(
    "/api/backups/run",
    response_model=MessageResponse,
    tags=["Backups"],
    dependencies=[Depends(verify_api_key)],
)
async def run_backup(
    background_tasks: BackgroundTasks,
    service: Annotated[BackupService, Depends(get_backup_service)],
    team_id: Optional[int] = Query(None, description="Backup specific team"),
    site_id: Optional[int] = Query(None, description="Backup specific site"),
):
    """Trigger a backup run."""
    if site_id:
        site = service.db.get_site(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        team = service.db.get_team(site.team_id)
        background_tasks.add_task(service.backup_site, team, site)
        return MessageResponse(message=f"Backup started for site {site.name}")
    elif team_id:
        team = service.db.get_team(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        background_tasks.add_task(service.backup_team, team)
        return MessageResponse(message=f"Backup started for team {team.name}")
    else:
        background_tasks.add_task(service.backup_all)
        return MessageResponse(message="Backup started for all teams")


@app.post(
    "/api/backups/cleanup",
    response_model=MessageResponse,
    tags=["Backups"],
    dependencies=[Depends(verify_api_key)],
)
async def cleanup_backups(
    service: Annotated[BackupService, Depends(get_backup_service)],
    max_backups: Optional[int] = Query(None, description="Override max backups to keep"),
):
    """Clean up old backups."""
    deleted = service.cleanup_old_backups(max_backups)
    return MessageResponse(message=f"Deleted {deleted} old backups")


# Download endpoints
@app.get(
    "/api/backups/{backup_id}/download/{file_type}",
    tags=["Downloads"],
    dependencies=[Depends(verify_api_key)],
)
async def download_backup_file(
    backup_id: int,
    file_type: str,
    db: Annotated[Database, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """Download a backup file.

    file_type can be: database, private, public, config
    """
    backup = db.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")

    file_map = {
        "database": backup.database_file,
        "private": backup.private_files,
        "public": backup.public_files,
        "config": backup.site_config,
    }

    if file_type not in file_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Must be one of: {list(file_map.keys())}",
        )

    relative_path = file_map[file_type]
    if not relative_path:
        raise HTTPException(status_code=404, detail=f"No {file_type} file in this backup")

    file_path = settings.backup_root / relative_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


# Stats endpoint
@app.get(
    "/api/stats",
    response_model=StatsResponse,
    tags=["Stats"],
    dependencies=[Depends(verify_api_key)],
)
async def get_stats(service: Annotated[BackupService, Depends(get_backup_service)]):
    """Get backup statistics."""
    stats = service.get_backup_stats()
    return StatsResponse(
        teams=stats["teams"],
        sites=stats["sites"],
        backups=stats["backups"],
        total_size_bytes=stats["total_size_bytes"],
        total_size_human=format_size(stats["total_size_bytes"]),
        team_details=stats["team_details"],
    )


# Settings endpoint
@app.get(
    "/api/settings",
    tags=["Settings"],
    dependencies=[Depends(verify_api_key)],
)
async def get_current_settings(settings: Annotated[Settings, Depends(get_settings)]):
    """Get current settings (excluding secrets)."""
    return {
        "backup_root": str(settings.backup_root),
        "db_path": str(settings.db_path),
        "max_backups_per_site": settings.max_backups_per_site,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "backup_schedule_hours": settings.backup_schedule_hours,
        "frappe_cloud_url": settings.frappe_cloud_url,
    }
