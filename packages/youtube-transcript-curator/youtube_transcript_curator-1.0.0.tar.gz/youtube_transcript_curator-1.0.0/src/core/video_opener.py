"""Open YouTube videos in browser with optional timestamp navigation."""

import subprocess
import platform
import logging
import re
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoOpener:
    """Handle opening YouTube videos in various browsers."""

    @staticmethod
    def _get_youtube_url(video_id: str, time_seconds: Optional[int] = None) -> str:
        """
        Build YouTube URL with optional timestamp.

        Args:
            video_id: YouTube video ID
            time_seconds: Optional timestamp in seconds to jump to

        Returns:
            Full YouTube URL
        """
        url = f"https://youtu.be/{video_id}"
        if time_seconds and time_seconds > 0:
            url += f"?t={time_seconds}"
        return url

    @staticmethod
    def _parse_time_format(time_str: str) -> Optional[int]:
        """
        Parse various time formats to seconds.

        Supported formats:
        - "90" or "90s" → 90 seconds
        - "1:30" → 90 seconds
        - "1m30s" → 90 seconds
        - "1:30:45" → 5445 seconds

        Args:
            time_str: Time in any supported format

        Returns:
            Time in seconds, or None if invalid
        """
        time_str = time_str.strip().lower()

        # Handle seconds only (e.g., "90" or "90s")
        if time_str.isdigit():
            return int(time_str)
        if time_str.endswith('s') and time_str[:-1].isdigit():
            return int(time_str[:-1])

        # Handle MM:SS or HH:MM:SS format
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:
                try:
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
                except ValueError:
                    return None
            elif len(parts) == 3:
                try:
                    hours, minutes, seconds = map(int, parts)
                    return hours * 3600 + minutes * 60 + seconds
                except ValueError:
                    return None

        # Handle "1m30s" format
        if 'm' in time_str:
            try:
                parts = time_str.replace('m', ' ').replace('s', ' ').split()
                total_seconds = 0
                i = 0
                while i < len(parts):
                    if parts[i].isdigit():
                        num = int(parts[i])
                        # Check what unit this is
                        if i + 1 < len(parts):
                            if 'm' in time_str[time_str.find(parts[i]):]:
                                # This is minutes
                                total_seconds += num * 60
                            elif 's' in time_str[time_str.find(parts[i]):]:
                                # This is seconds
                                total_seconds += num
                        else:
                            # Last number without unit specified
                            total_seconds += num
                    i += 1
                return total_seconds if total_seconds > 0 else None
            except (ValueError, IndexError):
                return None

        return None

    @staticmethod
    def _extract_timestamp(line: str) -> Optional[Tuple[int, str]]:
        """
        Extract timestamp from transcript line.

        Format expected: "[MM:SS] text" or "[HH:MM:SS] text"

        Args:
            line: Transcript line

        Returns:
            Tuple of (seconds, timestamp_string) or None if not found
        """
        match = re.match(r'\[(\d{1,2}):(\d{2}):?(\d{2})?\]', line.strip())
        if not match:
            return None

        groups = match.groups()
        if groups[2]:  # HH:MM:SS format
            hours, minutes, seconds = int(groups[0]), int(groups[1]), int(groups[2])
            total_seconds = hours * 3600 + minutes * 60 + seconds
            timestamp_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:  # MM:SS format
            minutes, seconds = int(groups[0]), int(groups[1])
            total_seconds = minutes * 60 + seconds
            timestamp_str = f"{minutes}:{seconds:02d}"

        return (total_seconds, timestamp_str)

    def search_transcript_for_keyword(
        self,
        video_id: str,
        keyword: str,
        transcript_file: str,
        max_results: int = 5
    ) -> Dict:
        """
        Search transcript for keyword and return matching lines with timestamps.

        Args:
            video_id: YouTube video ID
            keyword: Search keyword
            transcript_file: Path to transcript file
            max_results: Maximum number of results to return

        Returns:
            Dictionary with 'matches' (list of dicts) and 'total_found' (int)
            Each match contains: line_number, timestamp_seconds, timestamp_str, excerpt
        """
        matches = []
        total_found = 0

        try:
            transcript_path = Path(transcript_file)
            if not transcript_path.exists():
                logger.error(f"Transcript file not found: {transcript_file}")
                return {'matches': [], 'total_found': 0, 'error': 'File not found'}

            with open(transcript_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            keyword_lower = keyword.lower()

            for line_num, line in enumerate(lines, 1):
                if keyword_lower in line.lower():
                    total_found += 1

                    # Extract timestamp
                    timestamp_info = self._extract_timestamp(line)
                    if not timestamp_info:
                        continue  # Skip lines without timestamps

                    timestamp_seconds, timestamp_str = timestamp_info

                    # Extract excerpt (max 80 chars)
                    # Remove timestamp prefix and clean up
                    excerpt = re.sub(r'^\s*\[\d{1,2}:\d{2}:?(\d{2})?\]\s*', '', line.strip())
                    if len(excerpt) > 80:
                        excerpt = excerpt[:77] + "..."

                    if len(matches) < max_results:
                        matches.append({
                            'line_number': line_num,
                            'timestamp_seconds': timestamp_seconds,
                            'timestamp_str': timestamp_str,
                            'excerpt': excerpt
                        })

            return {
                'matches': matches,
                'total_found': total_found,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error searching transcript: {e}")
            return {'matches': [], 'total_found': 0, 'error': str(e)}

    @staticmethod
    def open_in_browser(url: str) -> bool:
        """
        Open URL in Chrome browser.

        Args:
            url: URL to open

        Returns:
            True if successful, False otherwise
        """
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                subprocess.run(
                    ["open", "-a", "Google Chrome", url],
                    check=True,
                    capture_output=True
                )
                return True
            elif system == "Linux":
                # Try google-chrome first, then chromium, then fallback to xdg-open
                for browser in ["google-chrome", "chromium", "chromium-browser"]:
                    try:
                        subprocess.run(
                            [browser, url],
                            check=True,
                            capture_output=True
                        )
                        return True
                    except FileNotFoundError:
                        continue
                # Fallback to system default
                subprocess.run(
                    ["xdg-open", url],
                    check=True,
                    capture_output=True
                )
                return True
            elif system == "Windows":
                subprocess.run(
                    ["start", "chrome", url],
                    shell=True,
                    check=True,
                    capture_output=True
                )
                return True
            else:
                logger.warning(f"Unsupported system: {system}")
                return False

        except FileNotFoundError:
            logger.error("Chrome not found. Please install Google Chrome.")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to open browser: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error opening browser: {e}")
            return False

    def open_youtube(
        self,
        video_id: str,
        time_seconds: Optional[int] = None,
        time_str: Optional[str] = None
    ) -> bool:
        """
        Open YouTube video in Chrome browser.

        Args:
            video_id: YouTube video ID
            time_seconds: Optional timestamp in seconds
            time_str: Optional timestamp as string (e.g., "1:30")

        Returns:
            True if successful, False otherwise
        """
        # Parse time if provided as string
        if time_str and not time_seconds:
            time_seconds = self._parse_time_format(time_str)
            if time_seconds is None:
                logger.error(f"Invalid time format: {time_str}")
                return False

        # Build URL
        url = self._get_youtube_url(video_id, time_seconds)

        # Open in browser
        return self.open_in_browser(url)
