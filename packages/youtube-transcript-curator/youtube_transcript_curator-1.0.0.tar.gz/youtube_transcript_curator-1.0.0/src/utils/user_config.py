"""User configuration management for YTC.

Manages user-specific configuration stored in ~/.ytc/config.yaml.
This allows pip install users to configure their data storage location
without needing a git clone of the repository.
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml


class UserConfig:
    """Manages user-specific configuration.

    Configuration priority (highest to lowest):
    1. Environment variable YTC_DATA_PATH
    2. User config ~/.ytc/config.yaml
    3. Repo config ./config/settings.yaml
    4. Setup wizard (if no config found)
    """

    CONFIG_DIR = Path.home() / ".ytc"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    CONFIG_VERSION = 1

    def __init__(self):
        self._config: dict = {}
        self._loaded = False

    @classmethod
    def get_default_data_path(cls) -> Path:
        """Get platform-appropriate default data path."""
        if sys.platform == 'darwin':  # macOS
            return Path.home() / 'Documents' / 'YTC-Library'
        elif sys.platform == 'win32':  # Windows
            return Path.home() / 'Documents' / 'YTC-Library'
        else:  # Linux
            return Path.home() / 'YTC-Library'

    def exists(self) -> bool:
        """Check if user config file exists."""
        return self.CONFIG_FILE.exists()

    def load(self) -> dict:
        """Load user configuration from file.

        Returns:
            Configuration dictionary (empty if file doesn't exist)
        """
        if not self.exists():
            self._config = {}
            self._loaded = True
            return self._config

        try:
            with open(self.CONFIG_FILE, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError):
            # If config is corrupted, start fresh
            self._config = {}

        self._loaded = True
        return self._config

    def save(self) -> None:
        """Save user configuration to file."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure version is set
        self._config['version'] = self.CONFIG_VERSION

        with open(self.CONFIG_FILE, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation.

        Args:
            key: Dot-notation key (e.g., 'data.path')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load()

        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a config value using dot notation.

        Args:
            key: Dot-notation key (e.g., 'data.path')
            value: Value to set
        """
        if not self._loaded:
            self.load()

        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save()

    def delete(self, key: str) -> bool:
        """Delete a config key.

        Args:
            key: Dot-notation key to delete

        Returns:
            True if key was deleted, False if not found
        """
        if not self._loaded:
            self.load()

        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return False

        if isinstance(config, dict) and keys[-1] in config:
            del config[keys[-1]]
            self.save()
            return True
        return False

    def get_data_path(self) -> Optional[Path]:
        """Get configured data path, expanding ~ and env vars.

        Returns:
            Expanded path or None if not configured
        """
        path_str = self.get('data.path')
        if path_str:
            return Path(os.path.expanduser(os.path.expandvars(path_str)))
        return None

    def set_data_path(self, path: Path) -> None:
        """Set the data storage path.

        Stores path with ~ for home directory to make config portable.

        Args:
            path: Path to data directory
        """
        path_str = str(path.resolve())
        home = str(Path.home())
        # Use ~ for home directory (portable)
        if path_str.startswith(home):
            path_str = '~' + path_str[len(home):]
        self.set('data.path', path_str)

    def show(self) -> str:
        """Return formatted config for display.

        Returns:
            YAML-formatted configuration string
        """
        if not self._loaded:
            self.load()
        if not self._config:
            return ""
        return yaml.dump(self._config, default_flow_style=False, sort_keys=False)

    def reset(self) -> None:
        """Reset configuration by deleting the config file."""
        if self.CONFIG_FILE.exists():
            self.CONFIG_FILE.unlink()
        self._config = {}
        self._loaded = False

    def get_all(self) -> dict:
        """Get full configuration dictionary.

        Returns:
            Configuration dictionary
        """
        if not self._loaded:
            self.load()
        return self._config.copy()


# Singleton instance for convenience
user_config = UserConfig()
