"""Log library changes (fetches, deletions) for auditing and recovery."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Literal

logger = logging.getLogger(__name__)


class LibraryLogger:
    """Track all library modifications (fetch/delete) with timestamps and metadata."""

    def __init__(self, log_dir: Path):
        """
        Initialize library logger.

        Args:
            log_dir: Directory to store library change logs
        """
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / 'library_changes.jsonl'
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Create log directory and file if they don't exist."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.touch()
            logger.info(f"Created library change log: {self.log_file}")

    def log_fetch(self, video_id: str, title: str, channel: str, url: str) -> None:
        """
        Log a video fetch.

        Args:
            video_id: YouTube video ID
            title: Video title
            channel: Channel name
            url: YouTube URL
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'fetch',
            'video_id': video_id,
            'title': title,
            'channel': channel,
            'url': url,
        }
        self._write_entry(entry)
        logger.info(f"Logged fetch: {video_id} - {title}")

    def log_delete(self, video_id: str, title: str, channel: str) -> None:
        """
        Log a video deletion.

        Args:
            video_id: YouTube video ID
            title: Video title
            channel: Channel name
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'delete',
            'video_id': video_id,
            'title': title,
            'channel': channel,
        }
        self._write_entry(entry)
        logger.info(f"Logged delete: {video_id} - {title}")

    def _write_entry(self, entry: Dict[str, Any]) -> None:
        """
        Write entry to log file (JSONL format - one JSON object per line).

        Args:
            entry: Entry dictionary to log
        """
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to library log: {e}")

    def get_recent_changes(self, limit: int = 50) -> list:
        """
        Get recent library changes.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of change entries (most recent first)
        """
        try:
            entries = []
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))

            # Reverse to get most recent first
            return entries[-limit:][::-1]
        except Exception as e:
            logger.error(f"Failed to read library log: {e}")
            return []

    def get_changes_by_action(self, action: Literal['fetch', 'delete']) -> list:
        """
        Get all changes of a specific action type.

        Args:
            action: 'fetch' or 'delete'

        Returns:
            List of entries matching the action
        """
        try:
            entries = []
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get('action') == action:
                            entries.append(entry)
            return entries
        except Exception as e:
            logger.error(f"Failed to read library log: {e}")
            return []

    def get_deleted_videos(self) -> list:
        """Get all deleted videos for recovery purposes."""
        return self.get_changes_by_action('delete')

    def export_log(self, output_file: Path) -> bool:
        """
        Export library change log to file.

        Args:
            output_file: Path to export log to

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.log_file, 'r') as f_in:
                with open(output_file, 'w') as f_out:
                    f_out.write(f_in.read())
            logger.info(f"Exported library log to: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export library log: {e}")
            return False
