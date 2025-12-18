"""First-time setup wizard for new YTC users.

This module provides an interactive setup experience for pip install users
who don't have a pre-configured data directory.
"""

import os
from pathlib import Path
from typing import Optional

import click

from .user_config import UserConfig, user_config


def needs_setup() -> bool:
    """Check if first-time setup is needed.

    Setup is needed when:
    1. No user config exists AND no repo-style data directory exists
    2. User config exists but data path is invalid/missing

    Returns:
        True if setup wizard should run
    """
    # Check for environment variable override
    if os.environ.get('YTC_DATA_PATH'):
        env_path = Path(os.path.expanduser(os.environ['YTC_DATA_PATH']))
        if env_path.exists():
            return False

    # Check if user config exists with valid data path
    if user_config.exists():
        data_path = user_config.get_data_path()
        if data_path and data_path.exists():
            return False

    # Check for repo-style installation (data/output exists relative to package)
    # This handles git clone users
    repo_data = Path.cwd() / 'data' / 'output'
    if repo_data.exists():
        return False

    # Also check relative to the package location (for when running from anywhere)
    package_root = Path(__file__).parent.parent.parent
    package_data = package_root / 'data' / 'output'
    if package_data.exists():
        return False

    return True


def create_data_directory(path: Path) -> None:
    """Create the data directory structure.

    Args:
        path: Base path for data storage
    """
    path.mkdir(parents=True, exist_ok=True)
    (path / 'metadata').mkdir(exist_ok=True)
    (path / 'transcripts').mkdir(exist_ok=True)
    (path / 'logs').mkdir(exist_ok=True)


def run_setup_wizard(quiet: bool = False) -> Path:
    """Run interactive setup wizard.

    Args:
        quiet: If True, use defaults without prompting

    Returns:
        Path to the configured data directory
    """
    default_path = UserConfig.get_default_data_path()

    if quiet:
        # Non-interactive mode - use default
        data_path = default_path
    else:
        click.echo()
        click.secho("Welcome to YouTube Transcript Curator (YTC)!", fg='cyan', bold=True)
        click.echo()
        click.echo("YTC stores YouTube transcripts locally for fast searching and reference.")
        click.echo("You need to choose where to store your transcript library.")
        click.echo()

        click.echo(f"Recommended: {default_path}")
        click.echo()
        click.echo("[1] Use recommended location")
        click.echo("[2] Enter custom path")
        click.echo("[3] Use current directory (./ytc-data)")
        click.echo()

        choice = click.prompt(
            "Your choice",
            type=click.Choice(['1', '2', '3']),
            default='1',
            show_default=True
        )

        if choice == '1':
            data_path = default_path
        elif choice == '2':
            custom = click.prompt("Enter path", type=str)
            data_path = Path(custom).expanduser().resolve()
        else:
            data_path = Path.cwd() / 'ytc-data'

    # Create directory structure
    create_data_directory(data_path)

    # Save configuration
    user_config.set_data_path(data_path)

    if not quiet:
        click.echo()
        click.secho(f"Library created at: {data_path}", fg='green')
        click.secho(f"Config saved to: {user_config.CONFIG_FILE}", fg='green')
        click.echo()

    return data_path


def ensure_setup(quiet: bool = False) -> Optional[Path]:
    """Ensure data directory is configured, running wizard if needed.

    This is the main entry point for checking/running setup.

    Args:
        quiet: If True, use defaults without prompting

    Returns:
        Path to data directory, or None if using repo config
    """
    if not needs_setup():
        # Already configured - return existing path
        data_path = user_config.get_data_path()
        if data_path:
            return data_path
        # Using repo config
        return None

    # Run setup wizard
    return run_setup_wizard(quiet=quiet)
