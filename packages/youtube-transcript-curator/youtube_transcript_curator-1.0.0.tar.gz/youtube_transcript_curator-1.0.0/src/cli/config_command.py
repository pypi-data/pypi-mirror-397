"""Configuration management commands for YTC.

Provides the `ytc config` command group for managing user configuration.
"""

import os
import subprocess
import sys
from pathlib import Path

import click

from src.utils.user_config import user_config, UserConfig
from src.utils.setup_wizard import run_setup_wizard


@click.group()
def config():
    """Manage YTC configuration.

    View and modify YTC settings, including data storage location.

    Examples:

        ytc config show          # View current configuration

        ytc config path          # Show data storage path

        ytc config set data.path ~/Dropbox/YTC

        ytc config edit          # Open config in editor
    """
    pass


@config.command()
def show():
    """Show current configuration."""
    if not user_config.exists():
        click.echo("No user configuration found.")
        click.echo(f"Config file location: {user_config.CONFIG_FILE}")
        click.echo()
        click.echo("Run 'ytc config init' to create configuration,")
        click.echo("or run any command to trigger the setup wizard.")
        return

    click.echo(f"Config file: {user_config.CONFIG_FILE}")
    click.echo()

    config_str = user_config.show()
    if config_str:
        click.echo(config_str)
    else:
        click.echo("(empty configuration)")


@config.command()
@click.argument('key')
def get(key: str):
    """Get a configuration value.

    KEY: Dot-notation key (e.g., 'data.path', 'logging.level')
    """
    value = user_config.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found", err=True)
        sys.exit(1)
    else:
        click.echo(value)


@config.command('set')
@click.argument('key')
@click.argument('value')
def set_value(key: str, value: str):
    """Set a configuration value.

    KEY: Dot-notation key (e.g., 'data.path')
    VALUE: Value to set
    """
    # Handle special case for data.path - expand and validate
    if key == 'data.path':
        path = Path(value).expanduser().resolve()
        if not path.exists():
            if click.confirm(f"Directory '{path}' does not exist. Create it?"):
                path.mkdir(parents=True, exist_ok=True)
                (path / 'metadata').mkdir(exist_ok=True)
                (path / 'transcripts').mkdir(exist_ok=True)
                (path / 'logs').mkdir(exist_ok=True)
            else:
                click.echo("Aborted.", err=True)
                sys.exit(1)
        user_config.set_data_path(path)
        click.echo(f"Set {key} = {user_config.get(key)}")
    else:
        user_config.set(key, value)
        click.echo(f"Set {key} = {value}")


@config.command()
def edit():
    """Open config file in default editor."""
    if not user_config.exists():
        click.echo("No config file exists yet. Creating default...")
        user_config.set_data_path(UserConfig.get_default_data_path())
        click.echo(f"Created config at: {user_config.CONFIG_FILE}")
        click.echo()

    # Try common editors
    editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
    if not editor:
        # Platform-specific defaults
        if sys.platform == 'darwin':
            editor = 'open -t'  # Opens in default text editor on macOS
        elif sys.platform == 'win32':
            editor = 'notepad'
        else:
            editor = 'nano'

    click.echo(f"Opening {user_config.CONFIG_FILE} in editor...")

    try:
        if editor == 'open -t':
            subprocess.run(['open', '-t', str(user_config.CONFIG_FILE)], check=True)
        else:
            subprocess.run([editor, str(user_config.CONFIG_FILE)], check=True)
    except FileNotFoundError:
        click.echo(f"Editor '{editor}' not found. Please open manually:", err=True)
        click.echo(f"  {user_config.CONFIG_FILE}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"Failed to open editor: {e}", err=True)
        sys.exit(1)


@config.command()
def path():
    """Show the current data storage path and library info."""
    # Check environment variable first
    env_path = os.environ.get('YTC_DATA_PATH')
    if env_path:
        data_path = Path(os.path.expanduser(env_path))
        click.echo(f"Data path: {data_path}")
        click.echo("  (from YTC_DATA_PATH environment variable)")
    else:
        data_path = user_config.get_data_path()
        if data_path:
            click.echo(f"Data path: {data_path}")
            click.echo(f"  (from {user_config.CONFIG_FILE})")
        else:
            # Check for repo-style path
            repo_data = Path.cwd() / 'data' / 'output'
            if repo_data.exists():
                click.echo(f"Data path: {repo_data}")
                click.echo("  (repo-style installation)")
                data_path = repo_data
            else:
                click.echo("No data path configured")
                click.echo(f"Default would be: {UserConfig.get_default_data_path()}")
                click.echo()
                click.echo("Run 'ytc config init' to set up your library.")
                return

    # Show library statistics if path exists
    if data_path and data_path.exists():
        metadata_dir = data_path / 'metadata'
        if metadata_dir.exists():
            metadata_count = len(list(metadata_dir.glob('*.json')))
            click.echo(f"Videos in library: {metadata_count}")
        else:
            click.echo("Videos in library: 0 (metadata directory not found)")
    else:
        click.secho(f"Warning: Path does not exist: {data_path}", fg='yellow')


@config.command()
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def reset(force: bool):
    """Reset configuration to defaults.

    This removes your configuration file (~/.ytc/config.yaml).
    Your transcript library data is NOT deleted - only the config file.

    After reset, the next time you run any YTC command, you'll be
    prompted to run the setup wizard to reconfigure your data path.
    """
    if not user_config.exists():
        click.echo("No configuration to reset.")
        return

    data_path = user_config.get_data_path()

    if not force:
        click.echo()
        click.secho("Reset Configuration", bold=True)
        click.echo()
        click.echo(f"This will delete: {user_config.CONFIG_FILE}")
        click.echo()
        click.secho("What happens after reset:", fg='yellow')
        click.echo("  - Your transcript library data will NOT be deleted")
        if data_path:
            click.echo(f"    (data remains at: {data_path})")
        click.echo("  - Next YTC command will trigger the setup wizard")
        click.echo("  - You'll need to reconfigure your data storage path")
        click.echo()
        if not click.confirm("Are you sure you want to reset configuration?"):
            click.echo("Aborted.")
            return

    user_config.reset()
    click.echo()
    click.secho("Configuration reset.", fg='green')
    click.echo("Run any YTC command to start the setup wizard.")


@config.command()
@click.option('--quiet', '-q', is_flag=True, help='Use defaults without prompting')
def init(quiet: bool):
    """Initialize configuration (run setup wizard)."""
    if user_config.exists():
        data_path = user_config.get_data_path()
        if data_path and data_path.exists():
            click.echo("Configuration already exists:")
            click.echo(f"  Config: {user_config.CONFIG_FILE}")
            click.echo(f"  Data: {data_path}")
            click.echo()
            if not click.confirm("Re-run setup wizard?"):
                return

    run_setup_wizard(quiet=quiet)


@config.command()
def where():
    """Show locations of all config files."""
    click.echo("Configuration locations:")
    click.echo()

    # User config
    click.echo(f"User config: {user_config.CONFIG_FILE}")
    if user_config.exists():
        click.echo("  Status: exists")
    else:
        click.echo("  Status: not created")

    # Repo config
    package_root = Path(__file__).parent.parent.parent
    repo_config = package_root / 'config' / 'settings.yaml'
    click.echo()
    click.echo(f"Repo config: {repo_config}")
    if repo_config.exists():
        click.echo("  Status: exists")
    else:
        click.echo("  Status: not found")

    # Environment variable
    click.echo()
    env_path = os.environ.get('YTC_DATA_PATH')
    click.echo(f"YTC_DATA_PATH: {env_path or '(not set)'}")


@config.command()
@click.argument('destination', type=click.Path())
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def move(destination: str, force: bool):
    """Move library to a new location (copies files safely).

    DESTINATION: New path for the transcript library

    This command:
    1. Copies all files to the new location
    2. Verifies the copy is complete and not corrupted
    3. Updates your configuration to point to the new location
    4. Only then removes the original files

    The process is designed to be safe - your data is never at risk.
    If anything fails, your original library remains intact.

    Example:

        ytc config move ~/Dropbox/YTC-Library

        ytc config move /Volumes/External/YTC-Library
    """
    import filecmp
    import shutil

    # Get current data path
    current_path = user_config.get_data_path()
    if not current_path:
        click.echo("No data path configured. Run 'ytc config init' first.", err=True)
        sys.exit(1)

    if not current_path.exists():
        click.echo(f"Current data path does not exist: {current_path}", err=True)
        sys.exit(1)

    dest_path = Path(destination).expanduser().resolve()

    if dest_path == current_path:
        click.echo("Destination is the same as current path.", err=True)
        sys.exit(1)

    if dest_path.exists() and any(dest_path.iterdir()):
        click.echo(f"Destination already exists and is not empty: {dest_path}", err=True)
        click.echo("Please choose an empty or non-existent directory.")
        sys.exit(1)

    # Count files to move
    metadata_count = len(list((current_path / 'metadata').glob('*.json'))) if (current_path / 'metadata').exists() else 0
    transcript_count = len(list((current_path / 'transcripts').glob('*'))) if (current_path / 'transcripts').exists() else 0

    if not force:
        click.echo()
        click.secho("Move Library", bold=True)
        click.echo()
        click.echo(f"From: {current_path}")
        click.echo(f"To:   {dest_path}")
        click.echo()
        click.echo("Files to move:")
        click.echo(f"  - {metadata_count} metadata files")
        click.echo(f"  - {transcript_count} transcript files")
        click.echo()
        click.secho("Process:", fg='cyan')
        click.echo("  1. Copy all files to new location")
        click.echo("  2. Verify copy integrity")
        click.echo("  3. Update configuration")
        click.echo("  4. Remove original files")
        click.echo()
        click.secho("Your data is safe - originals are only removed after", fg='yellow')
        click.secho("successful copy and verification.", fg='yellow')
        click.echo()
        if not click.confirm("Proceed with move?"):
            click.echo("Aborted.")
            return

    click.echo()
    click.echo("Step 1/4: Copying files to new location...")

    try:
        # Create destination and copy
        shutil.copytree(current_path, dest_path, dirs_exist_ok=True)
        click.secho("  Done.", fg='green')
    except Exception as e:
        click.secho(f"  Failed to copy: {e}", fg='red', err=True)
        click.echo("Original library unchanged.")
        sys.exit(1)

    click.echo("Step 2/4: Verifying copy integrity...")

    # Verify the copy
    try:
        comparison = filecmp.dircmp(current_path, dest_path)

        def verify_dir(dcmp, path=""):
            """Recursively verify directory comparison."""
            errors = []
            # Check for files only in source (missing in dest)
            if dcmp.left_only:
                errors.append(f"Missing in destination: {dcmp.left_only}")
            # Check for different files
            if dcmp.diff_files:
                errors.append(f"Files differ: {dcmp.diff_files}")
            # Recurse into subdirectories
            for sub_name, sub_dcmp in dcmp.subdirs.items():
                errors.extend(verify_dir(sub_dcmp, f"{path}/{sub_name}"))
            return errors

        errors = verify_dir(comparison)
        if errors:
            click.secho("  Verification failed!", fg='red', err=True)
            for error in errors:
                click.echo(f"    {error}", err=True)
            click.echo()
            click.echo("Original library unchanged. Removing incomplete copy...")
            shutil.rmtree(dest_path)
            sys.exit(1)

        click.secho("  Done. All files verified.", fg='green')
    except Exception as e:
        click.secho(f"  Verification error: {e}", fg='red', err=True)
        click.echo("Original library unchanged.")
        sys.exit(1)

    click.echo("Step 3/4: Updating configuration...")

    try:
        user_config.set_data_path(dest_path)
        click.secho("  Done.", fg='green')
    except Exception as e:
        click.secho(f"  Failed to update config: {e}", fg='red', err=True)
        click.echo("Files copied but config not updated. Manual cleanup may be needed.")
        sys.exit(1)

    click.echo("Step 4/4: Removing original files...")

    try:
        shutil.rmtree(current_path)
        click.secho("  Done.", fg='green')
    except Exception as e:
        click.secho(f"  Warning: Could not remove original: {e}", fg='yellow')
        click.echo("  Library moved successfully, but original files remain.")
        click.echo(f"  You may want to manually remove: {current_path}")

    click.echo()
    click.secho("Library moved successfully!", fg='green', bold=True)
    click.echo(f"New location: {dest_path}")
