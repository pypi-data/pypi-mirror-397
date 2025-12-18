"""Fetch YouTube video metadata using yt-dlp."""

import yt_dlp
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataFetcher:
    """Fetch metadata from YouTube videos."""

    def __init__(self):
        """Initialize metadata fetcher with yt-dlp options."""
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,  # We only want metadata, not the video
        }

    def fetch(self, video_id: str, url: str) -> Dict[str, Any]:
        """
        Fetch metadata for a YouTube video.

        Args:
            video_id: YouTube video ID
            url: Full YouTube URL (tracking params will be stripped)

        Returns:
            Dictionary containing video metadata

        Raises:
            Exception: If metadata cannot be fetched
        """
        logger.info(f"Fetching metadata for video: {video_id}")

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Build clean URL without tracking parameters (shortest format)
                clean_url = f"https://youtu.be/{video_id}"

                # Determine video type
                video_type = self._determine_video_type(info)

                # Build metadata dictionary
                metadata = {
                    'video_id': video_id,
                    'url': clean_url,
                    'video_type': video_type,
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('channel', info.get('uploader', 'Unknown Channel')),
                    'channel_id': info.get('channel_id', ''),
                    'channel_url': info.get('channel_url', ''),
                    'channel_subscribers': info.get('channel_follower_count', 0),
                    'duration': info.get('duration', 0),  # in seconds
                    'duration_string': self._format_duration(info.get('duration', 0)),
                    'view_count': info.get('view_count', 0),
                    'upload_date': self._parse_upload_date(info.get('upload_date')),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'categories': info.get('categories', []),
                    'tags': info.get('tags', []),
                    'language': info.get('language', 'en'),
                    'subtitles': list(info.get('subtitles', {}).keys()),
                    'has_captions': self._has_captions(info),
                    'processed_at': datetime.utcnow().isoformat() + 'Z',
                    'transcript_file': None,  # Will be set by output manager
                    'formatted_file': None,  # Will be set in Phase 2+
                }

                logger.info(f"Successfully fetched metadata for: {metadata['title']}")
                return metadata

        except yt_dlp.utils.DownloadError as e:
            logger.error(f"Failed to fetch metadata for {video_id}: {e}")
            raise Exception(f"Could not fetch video metadata. Video may be private, deleted, or unavailable: {e}")

        except Exception as e:
            logger.error(f"Unexpected error fetching metadata for {video_id}: {e}")
            raise Exception(f"Failed to fetch metadata: {e}")

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """
        Format duration in seconds to HH:MM:SS or MM:SS.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if not seconds:
            return "0:00"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    @staticmethod
    def _parse_upload_date(upload_date: Optional[str]) -> Optional[str]:
        """
        Parse yt-dlp upload date format (YYYYMMDD) to ISO format.

        Args:
            upload_date: Date string in YYYYMMDD format

        Returns:
            ISO formatted date string or None
        """
        if not upload_date:
            return None

        try:
            # yt-dlp returns dates as YYYYMMDD
            date_obj = datetime.strptime(upload_date, '%Y%m%d')
            return date_obj.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _determine_video_type(info: Dict[str, Any]) -> str:
        """
        Determine the type of video (regular, livestream, or recording).

        Args:
            info: yt-dlp info dictionary

        Returns:
            Video type: 'livestream', 'livestream_recording', or 'regular'
        """
        is_live = info.get('is_live', False)
        was_live = info.get('was_live', False)

        if is_live:
            return 'livestream'
        elif was_live:
            return 'livestream_recording'
        else:
            return 'regular'

    @staticmethod
    def _has_captions(info: Dict[str, Any]) -> bool:
        """
        Check if video has captions (manual or automatic).

        Args:
            info: yt-dlp info dictionary

        Returns:
            True if captions are available
        """
        has_subtitles = bool(info.get('subtitles'))
        has_auto_captions = bool(info.get('automatic_captions'))
        return has_subtitles or has_auto_captions
