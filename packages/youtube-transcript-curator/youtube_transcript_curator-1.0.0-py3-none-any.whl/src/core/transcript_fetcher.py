"""Fetch YouTube video transcripts using youtube-transcript-api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    YouTubeRequestFailed,
)
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """Fetch transcripts from YouTube videos."""

    def __init__(self, preferred_languages: Optional[List[str]] = None):
        """
        Initialize transcript fetcher.

        Args:
            preferred_languages: List of preferred language codes (e.g., ['en', 'es'])
        """
        self.preferred_languages = preferred_languages or ['en']

    def fetch(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Fetch transcript for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            List of transcript segments with text, start time, and duration

        Raises:
            Exception: If transcript cannot be fetched
        """
        logger.info(f"Fetching transcript for video: {video_id}")

        try:
            # Use the new API (v1.2+) which requires an instance
            api = YouTubeTranscriptApi()
            transcript_snippets = api.fetch(video_id, languages=self.preferred_languages)

            # Convert FetchedTranscriptSnippet objects to dictionaries for compatibility
            transcript_data = [
                {
                    'text': snippet.text,
                    'start': snippet.start,
                    'duration': snippet.duration
                }
                for snippet in transcript_snippets
            ]

            logger.info(f"Successfully fetched {len(transcript_data)} transcript segments")
            return transcript_data

        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video: {video_id}")
            raise Exception(
                "Transcripts are disabled for this video.\n"
                "The video owner has disabled captions."
            )

        except NoTranscriptFound:
            logger.error(f"No transcript found for video: {video_id}")
            raise Exception(
                "No transcript found for this video.\n"
                "The video may not have captions enabled in any language."
            )

        except VideoUnavailable:
            logger.error(f"Video unavailable: {video_id}")
            raise Exception(
                "Video is unavailable.\n"
                "It may be private, deleted, or region-restricted."
            )

        except YouTubeRequestFailed as e:
            logger.error(f"YouTube request failed for: {video_id}")
            raise Exception(
                f"YouTube request failed.\n"
                f"This may be due to rate limiting or temporary YouTube issues.\n"
                f"Please wait a few minutes and try again.\n"
                f"Technical error: {e}"
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching transcript for {video_id}: {e}")
            raise Exception(f"Failed to fetch transcript: {e}")

    def format_transcript(
        self,
        transcript_data: List[Dict[str, Any]],
        include_timestamps: bool = True
    ) -> str:
        """
        Format transcript data into readable text.

        Args:
            transcript_data: List of transcript segments from fetch()
            include_timestamps: Whether to include timestamps in output

        Returns:
            Formatted transcript text
        """
        lines = []

        for segment in transcript_data:
            text = segment['text'].strip()
            start = segment['start']

            if include_timestamps:
                # Format timestamp as MM:SS or HH:MM:SS
                timestamp = self._format_timestamp(start)
                lines.append(f"[{timestamp}] {text}")
            else:
                lines.append(text)

        return '\n'.join(lines)

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """
        Format seconds into timestamp string (HH:MM:SS or MM:SS).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def get_available_languages(self, video_id: str) -> List[str]:
        """
        Get list of available transcript languages for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            List of available language codes
        """
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            return [t.language_code for t in transcript_list]
        except Exception as e:
            logger.error(f"Failed to get available languages for {video_id}: {e}")
            return []
