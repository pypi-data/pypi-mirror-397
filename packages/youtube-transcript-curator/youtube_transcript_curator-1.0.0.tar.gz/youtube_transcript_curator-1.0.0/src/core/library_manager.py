"""Manage and query the library of transcribed videos."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class LibraryManager:
    """Load and query transcribed videos from metadata files."""

    def __init__(self, metadata_dir: Path):
        """
        Initialize library manager.

        Args:
            metadata_dir: Path to directory containing metadata JSON files
        """
        self.metadata_dir = Path(metadata_dir)
        self.videos: List[Dict[str, Any]] = []
        self._load_all_metadata()

    def _load_all_metadata(self) -> None:
        """Load all metadata files from the metadata directory."""
        self.videos = []

        if not self.metadata_dir.exists():
            logger.warning(f"Metadata directory not found: {self.metadata_dir}")
            return

        try:
            for metadata_file in sorted(self.metadata_dir.glob("metadata_*.json")):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        self.videos.append(metadata)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {metadata_file}: {e}")
                except Exception as e:
                    logger.error(f"Error loading {metadata_file}: {e}")

            logger.info(f"Loaded metadata for {len(self.videos)} videos")

        except Exception as e:
            logger.error(f"Error scanning metadata directory: {e}")

    def _fix_transcript_path(self, transcript_file: str) -> str:
        """
        Fix transcript file paths that reference old project locations.

        Handles migration scenarios:
        - youtube-transcriber → youtube-transcript-curator
        - Different parent directories (e.g., repo moved to new location)

        Args:
            transcript_file: Path from metadata (may reference old project location)

        Returns:
            Corrected path if file exists, original path otherwise
        """
        if not transcript_file:
            return transcript_file

        path = Path(transcript_file)

        # If path exists, return as-is
        if path.exists():
            return str(path)

        # Strategy 1: Try replacing old project name with new one
        old_name = "youtube-transcriber"
        new_name = "youtube-transcript-curator"

        path_str = str(transcript_file)
        if old_name in path_str:
            corrected = path_str.replace(old_name, new_name)
            corrected_path = Path(corrected)
            if corrected_path.exists():
                logger.debug(f"Auto-corrected path: {transcript_file} -> {corrected}")
                return corrected

        # Strategy 2: Extract filename and look relative to metadata_dir
        # This handles cases where the project was moved to a different parent directory
        filename = path.name
        if filename:
            # metadata_dir is data/output/metadata, transcripts are in data/output/transcripts
            transcripts_dir = self.metadata_dir.parent / 'transcripts'
            candidate = transcripts_dir / filename
            if candidate.exists():
                logger.debug(f"Auto-resolved path: {transcript_file} -> {candidate}")
                return str(candidate)

        # Return original if correction didn't work
        return str(path)

    def get_all_videos(self) -> List[Dict[str, Any]]:
        """Get all videos."""
        return self.videos

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific video by ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Video metadata dict or None if not found
        """
        for video in self.videos:
            if video.get('video_id') == video_id:
                return video
        return None

    def filter_by_type(self, video_type: str) -> List[Dict[str, Any]]:
        """
        Filter videos by type with fuzzy matching support.

        Supports exact matches and fuzzy matching:
        - 'regular' or 'reg' → regular
        - 'livestream', 'live', 'ls' → matches any livestream type (livestream or livestream_recording)
        - 'livestream_recording', 'rec', 'recording' → livestream_recording
        - Substring matching: 'lis' → livestream_recording, 'reg' → regular, etc.

        Args:
            video_type: Type to filter by (supports exact or fuzzy matching)

        Returns:
            List of matching videos

        Raises:
            ValueError: If type doesn't match any supported type
        """
        # Normalize input
        search_type = video_type.lower().strip()

        # Get unique types in library
        unique_types = set(v.get('video_type') for v in self.videos if v.get('video_type'))

        # Try exact match first
        if search_type in unique_types:
            return [v for v in self.videos if v.get('video_type') == search_type]

        # Fuzzy matching - map shortcuts to patterns that match available types
        fuzzy_map = {
            # Regular
            'reg': 'regular',
            'regular': 'regular',
            # Livestream (any variant)
            'live': 'live',  # Will match any type containing 'live'
            'livestream': 'live',  # Will match any type containing 'live'
            'ls': 'live',  # Will match any type containing 'live'
            # Livestream Recording (specific)
            'rec': 'livestream_recording',
            'recording': 'livestream_recording',
            'livestream_recording': 'livestream_recording',
            'live_rec': 'livestream_recording',
            'liverecording': 'livestream_recording',
        }

        if search_type in fuzzy_map:
            matched_pattern = fuzzy_map[search_type]

            # Special handling for 'live' which should match any livestream type
            if matched_pattern == 'live':
                matching_videos = [v for v in self.videos if 'live' in v.get('video_type', '').lower()]
                if matching_videos:
                    return matching_videos
            else:
                # Exact match for specific types
                matching_videos = [v for v in self.videos if v.get('video_type') == matched_pattern]
                if matching_videos:
                    return matching_videos

        # Fuzzy substring matching (similar to fzf)
        # Check if search_type characters appear in order in any type name
        def fuzzy_match(pattern: str, text: str) -> bool:
            """Check if pattern characters appear in order in text."""
            pattern = pattern.lower()
            text = text.lower()
            pattern_idx = 0

            for char in text:
                if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                    pattern_idx += 1

            return pattern_idx == len(pattern)

        matching_types = [t for t in unique_types if fuzzy_match(search_type, t)]
        if matching_types:
            # If we found matching types, return videos of those types
            matching_videos = [v for v in self.videos if v.get('video_type', '').lower() in [t.lower() for t in matching_types]]
            if matching_videos:
                return matching_videos

        # If no match, raise error with helpful message
        raise ValueError(f"Unknown type '{video_type}'. Supported types: {', '.join(sorted(unique_types))}")

    def get_supported_types(self) -> List[str]:
        """
        Get list of supported video types in the library.

        Returns:
            Sorted list of unique video types
        """
        unique_types = set(v.get('video_type') for v in self.videos if v.get('video_type'))
        return sorted(list(unique_types))

    def filter_by_channel(self, channel: str) -> List[Dict[str, Any]]:
        """
        Filter videos by channel name.

        Args:
            channel: Channel name (case-insensitive)

        Returns:
            List of matching videos
        """
        channel_lower = channel.lower()
        return [v for v in self.videos if channel_lower in v.get('channel', '').lower()]

    def sort_by(self, videos: List[Dict[str, Any]], sort_key: str = 'date', reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort videos by specified key.

        Args:
            videos: List of videos to sort
            sort_key: Key to sort by (date, published, title, channel, duration, views)
            reverse: Reverse sort order

        Returns:
            Sorted list of videos
        """
        if sort_key == 'date':
            # Sort by processed_at timestamp (when transcribed), newest first by default
            return sorted(
                videos,
                key=lambda v: v.get('processed_at', ''),
                reverse=not reverse  # Default is newest first
            )
        elif sort_key == 'published':
            # Sort by upload_date (YouTube publish date), newest first by default
            return sorted(
                videos,
                key=lambda v: v.get('upload_date', ''),
                reverse=not reverse  # Default is newest first
            )
        elif sort_key == 'title':
            return sorted(videos, key=lambda v: v.get('title', '').lower(), reverse=reverse)
        elif sort_key == 'channel':
            return sorted(videos, key=lambda v: v.get('channel', '').lower(), reverse=reverse)
        elif sort_key == 'duration':
            return sorted(videos, key=lambda v: v.get('duration', 0), reverse=reverse)
        elif sort_key == 'views':
            # Sort by view count, most viewed first by default
            return sorted(
                videos,
                key=lambda v: v.get('view_count', 0),
                reverse=not reverse  # Default is most viewed first
            )
        else:
            return videos

    def search_transcripts(self, keyword: str, context_lines: int = 0) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for keyword in all transcripts.

        Args:
            keyword: Keyword to search for
            context_lines: Number of lines before/after to include

        Returns:
            Dictionary mapping video_id to list of matches with context
        """
        results = {}
        keyword_lower = keyword.lower()

        for video in self.videos:
            video_id = video.get('video_id')
            transcript_file = self._fix_transcript_path(video.get('transcript_file', ''))

            if not transcript_file or not Path(transcript_file).exists():
                continue

            try:
                with open(transcript_file, 'r') as f:
                    lines = f.readlines()

                matches = []
                for idx, line in enumerate(lines):
                    if keyword_lower in line.lower():
                        match_obj = {
                            'line_number': idx + 1,
                            'text': line.strip(),
                            'context': []
                        }

                        # Add context if requested
                        if context_lines > 0:
                            start = max(0, idx - context_lines)
                            end = min(len(lines), idx + context_lines + 1)
                            match_obj['context'] = [
                                lines[i].strip() for i in range(start, end) if i != idx
                            ]

                        matches.append(match_obj)

                if matches:
                    results[video_id] = {
                        'title': video.get('title'),
                        'channel': video.get('channel'),
                        'matches': matches,
                        'match_count': len(matches)
                    }

            except Exception as e:
                logger.error(f"Error searching transcript {transcript_file}: {e}")

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the library.

        Returns:
            Dictionary with various statistics
        """
        if not self.videos:
            return {
                'total_videos': 0,
                'total_duration_seconds': 0,
                'total_duration_formatted': '0h 0m',
                'by_type': {},
                'by_channel': {}
            }

        # Calculate totals
        total_duration = sum(v.get('duration', 0) for v in self.videos)
        total_minutes = total_duration // 60
        total_hours = total_minutes // 60
        remaining_minutes = total_minutes % 60

        # Count by type
        type_counts = {}
        for video in self.videos:
            vtype = video.get('video_type', 'unknown')
            if vtype not in type_counts:
                type_counts[vtype] = {'count': 0, 'duration': 0}
            type_counts[vtype]['count'] += 1
            type_counts[vtype]['duration'] += video.get('duration', 0)

        # Count by channel
        channel_counts = {}
        for video in self.videos:
            channel = video.get('channel', 'Unknown')
            if channel not in channel_counts:
                channel_counts[channel] = {'count': 0, 'duration': 0}
            channel_counts[channel]['count'] += 1
            channel_counts[channel]['duration'] += video.get('duration', 0)

        # Sort channels by count
        sorted_channels = sorted(
            channel_counts.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )

        return {
            'total_videos': len(self.videos),
            'total_duration_seconds': total_duration,
            'total_duration_formatted': f'{total_hours}h {remaining_minutes}m',
            'average_duration_minutes': total_minutes // len(self.videos) if self.videos else 0,
            'by_type': type_counts,
            'by_channel': dict(sorted_channels[:10])  # Top 10 channels
        }

    def delete_video(self, video_id: str) -> bool:
        """
        Remove a video from the library (reload metadata).

        Args:
            video_id: YouTube video ID to remove

        Returns:
            True if video was found and removed, False otherwise
        """
        # Find and remove the video from the in-memory list
        for i, video in enumerate(self.videos):
            if video.get('video_id') == video_id:
                self.videos.pop(i)
                logger.info(f"Removed video {video_id} from library")
                return True

        logger.warning(f"Video {video_id} not found in library")
        return False
