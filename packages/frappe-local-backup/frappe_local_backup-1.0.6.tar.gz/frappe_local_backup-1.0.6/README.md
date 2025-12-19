# Frappe Local Backup Service

A backup service for downloading and managing backups from Frappe Cloud sites locally. Supports multiple teams, automatic scheduled backups, parallel downloads, and provides a REST API for remote access.

## Features

- **Multi-team support**: Connect multiple Frappe Cloud teams with auto-detection
- **Automatic backups**: Scheduled backup downloads (configurable interval)
- **Parallel downloads**: Download multiple sites simultaneously
- **Backup retention**: Automatically cleanup old backups (configurable)
- **Integrity verification**: Automatic size verification to detect incomplete downloads
- **REST API**: Secure API for remote backup management and downloads
- **Secure credentials**: Stored in OS keyring (GNOME Keyring on Linux)
- **SQLite database**: Track all backups and their metadata
- **CLI interface**: Full command-line management
- **Systemd service**: Run as a background service

## Installation

### Quick Install (Recommended)

```bash
# One-liner install script
curl -fsSL https://raw.githubusercontent.com/hawre1987/frappe-local-backup/main/install.sh | bash
```

### Install with pip

```bash
# Install from PyPI
pip install frappe-local-backup

# Or install with pipx (isolated environment)
pipx install frappe-local-backup
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/hawre1987/frappe-local-backup.git
cd frappe-local-backup

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

### System Dependencies

On Debian/Ubuntu:
```bash
sudo apt install gnome-keyring libsecret-1-0 libsecret-1-dev
```

On Fedora:
```bash
sudo dnf install gnome-keyring libsecret libsecret-devel
```

On Arch Linux:
```bash
sudo pacman -S gnome-keyring libsecret
```

## Quick Start

### Interactive Setup (Recommended)

```bash
frappe-backup setup
```

This wizard will guide you through:
1. Configuring backup folder path
2. Setting retention and schedule options
3. Adding Frappe Cloud teams (with auto-detection)
4. Syncing sites

### Manual Setup

#### 1. Initialize the service

```bash
frappe-backup init
```

#### 2. Add a Frappe Cloud team

Get your API credentials from Frappe Cloud Dashboard → Settings → API Access.

```bash
frappe-backup team add \
  --name "your-team-name" \
  --api-key "your-api-key" \
  --api-secret "your-api-secret"
```

#### 3. Sync sites

```bash
frappe-backup site sync
```

#### 4. Run a backup

```bash
# Backup all sites
frappe-backup backup run

# Backup specific site
frappe-backup backup run -n mysite.frappe.cloud

# Backup with parallel downloads (5 sites at once)
frappe-backup backup run -p 5

# Force re-download (verify and replace if sizes differ)
frappe-backup backup run -f
```

## CLI Commands

### Team Management

```bash
# Add team (credentials stored in OS keyring)
frappe-backup team add -n <team-name> -k <api-key> -s <api-secret>

# List teams
frappe-backup team list

# Remove team
frappe-backup team remove <team-id>

# Enable/disable team
frappe-backup team enable <team-id>
frappe-backup team disable <team-id>

# Update credentials
frappe-backup team update-credentials <team-id> -k <new-key> -s <new-secret>
```

### Site Management

```bash
# List all sites
frappe-backup site list

# Sync sites from Frappe Cloud
frappe-backup site sync
```

### Backup Operations

```bash
# Run backup for all sites
frappe-backup backup run

# Backup specific site by name
frappe-backup backup run -n mysite.frappe.cloud

# Backup specific site by ID
frappe-backup backup run -s 5

# Backup all sites in a team (by ID)
frappe-backup backup run -t 1

# Backup all sites in a team (by name)
frappe-backup backup run -T 62f025c2e1

# Parallel downloads
frappe-backup backup run -p 5

# Force re-download (verify sizes and replace if different)
frappe-backup backup run -f

# Combine options
frappe-backup backup run -T myteam -p 5 -f

# List backups
frappe-backup backup list

# Cleanup old backups
frappe-backup backup cleanup
```

### Debug Mode

```bash
# Show detailed API request/response logs
frappe-backup -d backup run -n mysite.frappe.cloud

# Verbose output
frappe-backup -v site sync
```

### Server & Scheduler

```bash
# Start API server with scheduler
frappe-backup serve

# Generate systemd service file
frappe-backup install-service

# With custom schedule (every 12 hours)
frappe-backup install-service -s 12
```

### Configuration

```bash
# Show current configuration
frappe-backup config

# View statistics
frappe-backup stats
```

## Configuration

Configuration is stored in `.env` file:

```bash
# Paths
BACKUP_ROOT=/path/to/backups
DB_PATH=./data/backups.db

# Backup retention
MAX_BACKUPS_PER_SITE=3

# Parallel downloads
PARALLEL_DOWNLOADS=3

# API settings (for REST API)
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-api-key

# Scheduler
BACKUP_SCHEDULE_HOURS=6

# Frappe Cloud
FRAPPE_CLOUD_URL=https://frappecloud.com
```

## Backup Storage Structure

```
backups/
├── team-name/
│   ├── site1.frappe.cloud/
│   │   ├── 20241215_120000/
│   │   │   ├── database.sql.gz
│   │   │   ├── private-files.tar
│   │   │   ├── public-files.tar
│   │   │   └── site_config.json
│   │   └── 20241214_120000/
│   └── site2.frappe.cloud/
```

## REST API

When running `frappe-backup serve`, the following endpoints are available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/teams` | List all teams |
| POST | `/api/teams` | Create team |
| DELETE | `/api/teams/{id}` | Delete team |
| GET | `/api/sites` | List all sites |
| POST | `/api/sites/sync` | Sync sites from Frappe Cloud |
| GET | `/api/backups` | List all backups |
| GET | `/api/backups/{id}` | Get backup details |
| POST | `/api/backups/run` | Trigger backup |
| POST | `/api/backups/cleanup` | Cleanup old backups |
| GET | `/api/backups/{id}/download/{type}` | Download backup file |
| GET | `/api/stats` | Get statistics |
| GET | `/health` | Health check |

Authentication: Include `X-API-Key` header with your API key.

## Running as a Service

### Using systemd

```bash
# Generate service file
frappe-backup install-service

# Install (requires sudo)
sudo cp frappe-backup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable frappe-backup
sudo systemctl start frappe-backup

# Check status
sudo systemctl status frappe-backup
sudo journalctl -u frappe-backup -f
```

### Using Docker (coming soon)

```bash
docker run -d \
  -v /path/to/backups:/backups \
  -v /path/to/data:/data \
  -e BACKUP_SCHEDULE_HOURS=6 \
  frappe-local-backup
```

## Security

- **Credentials**: Stored in OS keyring (GNOME Keyring), encrypted with your user password
- **API Key**: Auto-generated secure key for REST API authentication
- **Backup Files**: Stored with appropriate file permissions

## Troubleshooting

### Keyring not available

On headless servers, you may need to unlock the keyring:

```bash
# Create a keyring if needed
dbus-run-session -- bash -c 'echo -n "" | gnome-keyring-daemon --unlock'
```

Or use environment variable for credentials (less secure):
```bash
export FRAPPE_BACKUP_TEAM_CREDENTIALS='{"team1": {"key": "...", "secret": "..."}}'
```

### Debug API requests

```bash
frappe-backup -d site sync
frappe-backup -d backup run -n mysite.frappe.cloud
```

### Connection issues

1. Verify API credentials in Frappe Cloud Dashboard
2. Check team name matches exactly (case-sensitive)
3. Ensure network access to frappecloud.com

## Development

```bash
# Install with dev dependencies
make dev

# Run tests
make test

# Format code
make format

# Build package
make build

# Publish to PyPI
make publish
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

- GitHub Issues: [Report a bug](https://github.com/hawre1987/frappe-local-backup/issues)
- Documentation: [Wiki](https://github.com/hawre1987/frappe-local-backup)
