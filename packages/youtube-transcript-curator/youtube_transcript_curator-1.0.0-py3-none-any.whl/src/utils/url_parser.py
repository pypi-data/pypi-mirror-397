"""URL parsing and validation for YouTube videos."""

import re
from typing import Optional


class YouTubeURLParser:
    """Parser and validator for YouTube URLs."""

    # Supported YouTube URL patterns
    PATTERNS = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:m\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})',
    ]

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Automatically strips tracking parameters (si=..., t=..., etc.)
        that YouTube adds to shared links.

        Args:
            url: YouTube URL in any supported format
                 (with or without tracking parameters)

        Returns:
            11-character video ID if valid, None otherwise

        Examples:
            >>> YouTubeURLParser.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
            'dQw4w9WgXcQ'
            >>> YouTubeURLParser.extract_video_id('https://youtu.be/dQw4w9WgXcQ?si=xyz123')
            'dQw4w9WgXcQ'
            >>> YouTubeURLParser.extract_video_id('https://youtu.be/dQw4w9WgXcQ')
            'dQw4w9WgXcQ'
        """
        if not url or not isinstance(url, str):
            return None

        # Clean whitespace
        url = url.strip()

        # Try each pattern
        for pattern in cls.PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # If no pattern matches, check if it's just a video ID
        if cls._is_valid_video_id(url):
            return url

        return None

    @staticmethod
    def _is_valid_video_id(video_id: str) -> bool:
        """
        Check if string is a valid YouTube video ID.

        Args:
            video_id: String to validate

        Returns:
            True if valid 11-character video ID, False otherwise
        """
        if not video_id or not isinstance(video_id, str):
            return False

        # YouTube video IDs are exactly 11 characters: letters, numbers, dash, underscore
        pattern = r'^[a-zA-Z0-9_-]{11}$'
        return bool(re.match(pattern, video_id))

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """
        Validate if URL is a supported YouTube URL.

        Args:
            url: URL to validate

        Returns:
            True if valid YouTube URL, False otherwise
        """
        return cls.extract_video_id(url) is not None

    @classmethod
    def build_standard_url(cls, video_id: str) -> str:
        """
        Build standard YouTube URL from video ID (shortest clean format).

        Args:
            video_id: YouTube video ID

        Returns:
            Standard YouTube short URL without tracking parameters

        Example:
            >>> YouTubeURLParser.build_standard_url('dQw4w9WgXcQ')
            'https://youtu.be/dQw4w9WgXcQ'
        """
        return f"https://youtu.be/{video_id}"
