#!/usr/bin/env python3
"""Version bump script for frappe-local-backup.

Usage:
    python scripts/bump_version.py patch  # 1.0.0 -> 1.0.1
    python scripts/bump_version.py minor  # 1.0.0 -> 1.1.0
    python scripts/bump_version.py major  # 1.0.0 -> 2.0.0
    python scripts/bump_version.py 1.2.3  # Set specific version
"""

import re
import sys
from pathlib import Path


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if match:
        return match.group(1)
    raise ValueError("Could not find version in pyproject.toml")


def set_version(new_version: str) -> None:
    """Set version in pyproject.toml and __init__.py."""
    # Update pyproject.toml
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    content = re.sub(
        r'^version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE,
    )
    pyproject.write_text(content)
    
    # Update __init__.py
    init_file = Path("frappe_local_backup/__init__.py")
    init_content = init_file.read_text()
    init_content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        init_content,
    )
    init_file.write_text(init_content)

     # Update __init__.py
    init_file = Path("__init__.py")
    init_content = init_file.read_text()
    init_content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        init_content,
    )
    init_file.write_text(init_content)


def bump_version(current: str, bump_type: str) -> str:
    """Calculate new version based on bump type."""
    parts = current.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current}")
    
    major, minor, patch = map(int, parts)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        # Assume it's a specific version
        if re.match(r"^\d+\.\d+\.\d+$", bump_type):
            return bump_type
        raise ValueError(f"Invalid bump type or version: {bump_type}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    bump_type = sys.argv[1]
    
    try:
        current = get_current_version()
        new_version = bump_version(current, bump_type)
        
        print(f"Current version: {current}")
        print(f"New version: {new_version}")
        
        confirm = input("Proceed? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted")
            sys.exit(1)
        
        set_version(new_version)
        print(f"✓ Updated version to {new_version}")
        print(f"\nNext steps:")
        print(f"  git add pyproject.toml frappe_local_backup/__init__.py")
        print(f"  git commit -m 'Bump version to {new_version}'")
        print(f"  git tag v{new_version}")
        print(f"  git push origin main --tags")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
