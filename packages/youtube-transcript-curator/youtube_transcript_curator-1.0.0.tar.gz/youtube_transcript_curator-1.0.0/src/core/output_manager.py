"""Manage file output for transcripts and metadata."""

import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OutputManager:
    """Manage saving transcripts and metadata to files."""

    def __init__(self, base_output_dir: Path, overwrite: bool = False):
        """
        Initialize output manager.

        Args:
            base_output_dir: Base directory for all outputs
            overwrite: Whether to overwrite existing files
        """
        self.base_output_dir = Path(base_output_dir)
        self.overwrite = overwrite

        # Ensure output directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create output directories if they don't exist."""
        dirs = [
            self.base_output_dir / 'metadata',
            self.base_output_dir / 'transcripts',
            self.base_output_dir / 'formatted',
            self.base_output_dir / 'ai-processed',
            self.base_output_dir / 'logs',
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {dir_path}")

    def save_metadata(self, metadata: Dict[str, Any], video_id: str) -> Path:
        """
        Save video metadata as JSON file.

        Args:
            metadata: Metadata dictionary
            video_id: YouTube video ID

        Returns:
            Path to saved metadata file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        filename = f"metadata_{video_id}.json"
        filepath = self.base_output_dir / 'metadata' / filename

        if filepath.exists() and not self.overwrite:
            logger.warning(f"Metadata file already exists: {filepath}")
            raise FileExistsError(
                f"Metadata file already exists: {filepath}\n"
                f"Use --overwrite flag to replace existing files."
            )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved metadata to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save metadata to {filepath}: {e}")
            raise Exception(f"Failed to save metadata file: {e}")

    def save_transcript(
        self,
        transcript_text: str,
        video_id: str,
        prefix: str = "youtube"
    ) -> Path:
        """
        Save transcript as text file.

        Args:
            transcript_text: Formatted transcript text
            video_id: YouTube video ID
            prefix: File prefix (default: "youtube")

        Returns:
            Path to saved transcript file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        filename = f"{prefix}_{video_id}.txt"
        filepath = self.base_output_dir / 'transcripts' / filename

        if filepath.exists() and not self.overwrite:
            logger.warning(f"Transcript file already exists: {filepath}")
            raise FileExistsError(
                f"Transcript file already exists: {filepath}\n"
                f"Use --overwrite flag to replace existing files."
            )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript_text)

            logger.info(f"Saved transcript to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save transcript to {filepath}: {e}")
            raise Exception(f"Failed to save transcript file: {e}")

    def save_formatted_transcript(
        self,
        formatted_text: str,
        video_id: str
    ) -> Path:
        """
        Save formatted transcript with chapters (Phase 2+).

        Args:
            formatted_text: Formatted markdown text
            video_id: YouTube video ID

        Returns:
            Path to saved formatted file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        filename = f"formatted_{video_id}.md"
        filepath = self.base_output_dir / 'formatted' / filename

        if filepath.exists() and not self.overwrite:
            logger.warning(f"Formatted file already exists: {filepath}")
            raise FileExistsError(
                f"Formatted file already exists: {filepath}\n"
                f"Use --overwrite flag to replace existing files."
            )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_text)

            logger.info(f"Saved formatted transcript to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save formatted transcript to {filepath}: {e}")
            raise Exception(f"Failed to save formatted file: {e}")

    def check_file_exists(self, video_id: str, file_type: str = 'all') -> Dict[str, bool]:
        """
        Check if output files already exist for a video.

        Args:
            video_id: YouTube video ID
            file_type: Type to check ('metadata', 'transcript', 'formatted', or 'all')

        Returns:
            Dictionary with file type as key and existence as value
        """
        results = {}

        if file_type in ['metadata', 'all']:
            metadata_path = self.base_output_dir / 'metadata' / f"metadata_{video_id}.json"
            results['metadata'] = metadata_path.exists()

        if file_type in ['transcript', 'all']:
            transcript_path = self.base_output_dir / 'transcripts' / f"youtube_{video_id}.txt"
            results['transcript'] = transcript_path.exists()

        if file_type in ['formatted', 'all']:
            formatted_path = self.base_output_dir / 'formatted' / f"formatted_{video_id}.md"
            results['formatted'] = formatted_path.exists()

        return results

    def get_file_paths(self, video_id: str) -> Dict[str, Path]:
        """
        Get expected file paths for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with file type as key and path as value
        """
        return {
            'metadata': self.base_output_dir / 'metadata' / f"metadata_{video_id}.json",
            'transcript': self.base_output_dir / 'transcripts' / f"youtube_{video_id}.txt",
            'formatted': self.base_output_dir / 'formatted' / f"formatted_{video_id}.md",
        }

    def update_metadata_with_file_references(
        self,
        metadata: Dict[str, Any],
        transcript_path: Path,
        formatted_path: Path = None
    ) -> Dict[str, Any]:
        """
        Update metadata dictionary with file path references.

        Args:
            metadata: Original metadata dictionary
            transcript_path: Path to saved transcript file
            formatted_path: Optional path to formatted file

        Returns:
            Updated metadata dictionary
        """
        # Store absolute paths so they work regardless of current directory
        metadata['transcript_file'] = str(transcript_path.resolve())
        if formatted_path:
            metadata['formatted_file'] = str(formatted_path.resolve())

        return metadata

    def delete_video_files(self, video_id: str) -> Dict[str, bool]:
        """
        Delete all files for a video (metadata, transcript, formatted).

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with file type as key and deletion success as value

        Raises:
            FileNotFoundError: If no files found for the video
        """
        file_paths = self.get_file_paths(video_id)
        results = {}
        deleted_count = 0

        for file_type, filepath in file_paths.items():
            try:
                if filepath.exists():
                    filepath.unlink()
                    results[file_type] = True
                    deleted_count += 1
                    logger.info(f"Deleted {file_type}: {filepath}")
                else:
                    results[file_type] = False
                    logger.debug(f"File does not exist: {filepath}")
            except Exception as e:
                results[file_type] = False
                logger.error(f"Failed to delete {file_type} {filepath}: {e}")

        if deleted_count == 0:
            raise FileNotFoundError(f"No files found for video: {video_id}")

        return results
