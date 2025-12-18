"""Configuration loader for YouTube Transcript Curator.

Supports multiple configuration sources with priority:
1. Environment variables (YTC_DATA_PATH)
2. User config (~/.ytc/config.yaml)
3. Repo config (./config/settings.yaml)
4. Setup wizard (first-time users)
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from .user_config import user_config
from .setup_wizard import needs_setup, run_setup_wizard


class ConfigLoader:
    """Load and manage application configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to settings.yaml file. If None, uses default.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}

        # Load environment variables from .env
        load_dotenv()

        # Load YAML configuration
        self._load_config()

    @staticmethod
    def _get_default_config_path() -> Path:
        """Get default path to config/settings.yaml."""
        # Assume we're running from project root
        project_root = Path(__file__).parent.parent.parent
        return project_root / "config" / "settings.yaml"

    def _load_config(self) -> None:
        """Load configuration from YAML file.

        For pip install users without a repo config, uses sensible defaults.
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            # No repo config - use defaults (pip install scenario)
            self.config = self._get_default_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for pip install users."""
        return {
            'app': {
                'name': 'YouTube Transcript Curator',
                'version': '1.0.0',
            },
            'output': {
                'overwrite': False,
            },
            'transcript': {
                'languages': ['en'],
            },
            'logging': {
                'level': 'INFO',
                'console_output': False,
            },
            'rate_limiting': {
                'request_delay': 1,
                'retry_attempts': 3,
                'retry_delay': 5,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., 'app.version')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config = ConfigLoader()
            >>> config.get('app.version')
            '0.0.1'
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_env(self, key: str, default: Any = None) -> Any:
        """
        Get value from environment variables.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def get_output_dir(self, subdir: Optional[str] = None, run_wizard: bool = True) -> Path:
        """
        Get output directory path with priority resolution.

        Priority:
        1. YTC_DATA_PATH environment variable
        2. User config (~/.ytc/config.yaml)
        3. Repo config (./config/settings.yaml)
        4. Setup wizard (if run_wizard=True and interactive)

        Args:
            subdir: Optional subdirectory (e.g., 'metadata', 'transcripts')
            run_wizard: If True, run setup wizard when no config found

        Returns:
            Absolute path to output directory
        """
        base_path = self._resolve_data_path(run_wizard=run_wizard)

        if subdir:
            return base_path / subdir
        return base_path

    def _resolve_data_path(self, run_wizard: bool = True) -> Path:
        """Resolve data path using priority chain.

        Args:
            run_wizard: If True, run setup wizard when needed

        Returns:
            Resolved data path
        """
        # 1. Environment variable takes highest priority
        env_path = os.environ.get('YTC_DATA_PATH')
        if env_path:
            path = Path(os.path.expanduser(env_path))
            if path.exists():
                return path
            # Env var set but path doesn't exist - create it
            path.mkdir(parents=True, exist_ok=True)
            return path

        # 2. User config (~/.ytc/config.yaml)
        user_path = user_config.get_data_path()
        if user_path and user_path.exists():
            return user_path

        # 3. Repo config - check if we have a repo-style installation
        project_root = Path(__file__).parent.parent.parent
        repo_config_path = project_root / 'config' / 'settings.yaml'

        if repo_config_path.exists():
            # We have repo config - use its output directory
            base_dir = self.get('output.base_directory', 'data/output')
            base_path = Path(base_dir)
            if not base_path.is_absolute():
                base_path = project_root / base_path
            if base_path.exists():
                return base_path

        # 4. Setup wizard (for pip install users)
        if run_wizard and needs_setup():
            import sys
            # Only run wizard in interactive mode
            if sys.stdin.isatty():
                return run_setup_wizard()

        # 5. Fallback: user config path (even if not created yet)
        if user_path:
            return user_path

        # 6. Ultimate fallback: default path
        return user_config.get_default_data_path()

    def get_log_level(self) -> str:
        """Get logging level from env or config."""
        # Environment variable takes precedence
        return self.get_env('LOG_LEVEL', self.get('logging.level', 'INFO'))

    def get_version(self) -> str:
        """Get application version."""
        return self.get('app.version', '0.0.0')

    def get_app_name(self) -> str:
        """Get application name."""
        return self.get('app.name', 'YouTube Transcriber')

    def should_overwrite_files(self) -> bool:
        """Check if files should be overwritten."""
        return self.get('output.overwrite', False)

    def get_rate_limit_delay(self) -> int:
        """Get rate limiting delay in seconds."""
        return self.get('rate_limiting.request_delay', 1)

    def get_retry_attempts(self) -> int:
        """Get number of retry attempts."""
        return self.get('rate_limiting.retry_attempts', 3)

    def get_retry_delay(self) -> int:
        """Get delay between retries in seconds."""
        return self.get('rate_limiting.retry_delay', 5)
