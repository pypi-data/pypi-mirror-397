"""Manage AI-processed content storage and retrieval."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import logging

from src.ai.prompts import EXTRACTION_TYPES

logger = logging.getLogger(__name__)


class AIProcessedManager:
    """Manage saving and loading AI-processed content (summaries, extractions)."""

    def __init__(self, base_output_dir: Path):
        """
        Initialize AI processed content manager.

        Args:
            base_output_dir: Base directory for outputs (e.g., data/output)
        """
        self.base_output_dir = Path(base_output_dir)
        self.ai_processed_dir = self.base_output_dir / 'ai-processed'

        # Ensure base AI processed directory exists
        self._ensure_base_directory()

    def _ensure_base_directory(self) -> None:
        """Create ai-processed base directory if it doesn't exist."""
        self.ai_processed_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured AI processed directory exists: {self.ai_processed_dir}")

    def _ensure_video_directory(self, video_id: str) -> Path:
        """
        Create video-specific AI processed directory if it doesn't exist.

        Args:
            video_id: YouTube video ID

        Returns:
            Path to video's AI processed directory
        """
        video_dir = self.ai_processed_dir / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured video AI directory exists: {video_dir}")
        return video_dir

    def save_summary(
        self,
        video_id: str,
        summary_text: str,
        length: str,
        model: str,
        overwrite: bool = False
    ) -> Path:
        """
        Save AI-generated summary to markdown file.

        Args:
            video_id: YouTube video ID
            summary_text: Summary content
            length: Summary length (short, medium, long)
            model: AI model used (e.g., claude-3-5-haiku-20241022)
            overwrite: Whether to overwrite if file exists

        Returns:
            Path to saved summary file

        Raises:
            FileExistsError: If file exists and overwrite is False
        """
        video_dir = self._ensure_video_directory(video_id)
        filename = f"summary_{length}.md"
        filepath = video_dir / filename

        if filepath.exists() and not overwrite:
            logger.warning(f"Summary file already exists: {filepath}")
            raise FileExistsError(
                f"Summary already exists: {filepath}\n"
                f"Use --overwrite to regenerate."
            )

        try:
            # Add metadata header to summary
            timestamp = datetime.now().isoformat()
            content = f"""# Summary ({length.title()})

**Generated:** {timestamp}
**Model:** {model}
**Video ID:** {video_id}

---

{summary_text}
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Saved {length} summary to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save summary to {filepath}: {e}")
            raise Exception(f"Failed to save summary: {e}")

    def load_summary(self, video_id: str, length: str = 'medium') -> Optional[str]:
        """
        Load AI-generated summary from file.

        Args:
            video_id: YouTube video ID
            length: Summary length (short, medium, long)

        Returns:
            Summary content if exists, None otherwise
        """
        filepath = self.ai_processed_dir / video_id / f"summary_{length}.md"

        if not filepath.exists():
            logger.debug(f"Summary file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load summary from {filepath}: {e}")
            return None

    def check_summary_exists(self, video_id: str, length: str = 'medium') -> bool:
        """
        Check if a summary file exists for a video.

        Args:
            video_id: YouTube video ID
            length: Summary length (short, medium, long)

        Returns:
            True if summary exists, False otherwise
        """
        filepath = self.ai_processed_dir / video_id / f"summary_{length}.md"
        return filepath.exists()

    def get_summary_path(self, video_id: str, length: str = 'medium') -> Path:
        """
        Get path to summary file (whether it exists or not).

        Args:
            video_id: YouTube video ID
            length: Summary length (short, medium, long)

        Returns:
            Path to summary file
        """
        return self.ai_processed_dir / video_id / f"summary_{length}.md"

    def get_available_summaries(self, video_id: str) -> Dict[str, Path]:
        """
        Get all available summaries for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary mapping length to filepath for existing summaries
        """
        available = {}
        video_dir = self.ai_processed_dir / video_id

        if not video_dir.exists():
            return available

        for length in ['short', 'medium', 'long']:
            filepath = video_dir / f"summary_{length}.md"
            if filepath.exists():
                available[length] = filepath

        return available

    def get_video_ai_directory(self, video_id: str) -> Optional[Path]:
        """
        Get path to video's AI processed directory.

        Args:
            video_id: YouTube video ID

        Returns:
            Path to directory if it exists, None otherwise
        """
        video_dir = self.ai_processed_dir / video_id
        return video_dir if video_dir.exists() else None

    def delete_summary(self, video_id: str, length: str = 'medium') -> bool:
        """
        Delete a summary file.

        Args:
            video_id: YouTube video ID
            length: Summary length (short, medium, long)

        Returns:
            True if deleted successfully, False if file didn't exist
        """
        filepath = self.ai_processed_dir / video_id / f"summary_{length}.md"

        if not filepath.exists():
            logger.debug(f"Summary file not found: {filepath}")
            return False

        try:
            filepath.unlink()
            logger.info(f"Deleted summary: {filepath}")

            # Clean up empty directory
            video_dir = filepath.parent
            if video_dir.exists() and not any(video_dir.iterdir()):
                video_dir.rmdir()
                logger.debug(f"Removed empty directory: {video_dir}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete summary {filepath}: {e}")
            return False

    def get_summary_metadata(
        self,
        video_id: str,
        length: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Generate metadata entry for a summary.

        Args:
            video_id: YouTube video ID
            length: Summary length
            model: AI model used

        Returns:
            Metadata dictionary for storage in video metadata
        """
        filepath = self.get_summary_path(video_id, length)

        # Convert paths to absolute before creating relative path
        abs_filepath = filepath.resolve()
        abs_base = self.base_output_dir.resolve()

        relative_path = abs_filepath.relative_to(abs_base)

        metadata = {
            "created_at": datetime.now().isoformat(),
            "model": model,
            "file": str(relative_path)
        }

        # Add file size if it exists
        if filepath.exists():
            metadata["size_bytes"] = filepath.stat().st_size

        return metadata

    # =========================================================================
    # Extraction Methods (v0.9.0)
    # =========================================================================

    def save_extraction(
        self,
        video_id: str,
        extraction_type: str,
        items: List[Dict[str, Any]],
        model: str,
        video_title: str = "",
        overwrite: bool = False
    ) -> Tuple[Path, Path]:
        """
        Save extraction in dual format (JSON + Markdown).

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction ('books', 'tools', 'key_points')
            items: List of extracted items
            model: AI model used
            video_title: Title of the video (for display in markdown)
            overwrite: Whether to overwrite if files exist

        Returns:
            Tuple of (json_path, markdown_path)

        Raises:
            ValueError: If extraction_type is invalid
            FileExistsError: If files exist and overwrite is False
        """
        if extraction_type not in EXTRACTION_TYPES:
            raise ValueError(
                f"Invalid extraction type: {extraction_type}. "
                f"Must be one of: {EXTRACTION_TYPES}"
            )

        video_dir = self._ensure_video_directory(video_id)
        json_path = video_dir / f"{extraction_type}.json"
        md_path = video_dir / f"{extraction_type}.md"

        if (json_path.exists() or md_path.exists()) and not overwrite:
            raise FileExistsError(
                f"Extraction already exists: {json_path}\n"
                f"Use --overwrite to regenerate."
            )

        timestamp = datetime.now().isoformat()

        # Generate JSON content
        json_data = {
            "extracted_at": timestamp,
            "model": model,
            "video_id": video_id,
            "video_title": video_title,
            "count": len(items),
            "items": items
        }

        # Generate Markdown content
        md_content = self._generate_extraction_markdown(
            extraction_type, items, video_id, video_title, model, timestamp
        )

        try:
            # Save JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {extraction_type} JSON to: {json_path}")

            # Save Markdown
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"Saved {extraction_type} Markdown to: {md_path}")

            return json_path, md_path

        except Exception as e:
            logger.error(f"Failed to save extraction: {e}")
            raise Exception(f"Failed to save extraction: {e}")

    def _generate_extraction_markdown(
        self,
        extraction_type: str,
        items: List[Dict[str, Any]],
        video_id: str,
        video_title: str,
        model: str,
        timestamp: str
    ) -> str:
        """Generate human-readable markdown from extracted items."""
        # Header
        type_titles = {
            'books': 'Books & Papers Mentioned',
            'tools': 'Tools & Software Mentioned',
            'key_points': 'Key Points & Insights'
        }
        title = type_titles.get(extraction_type, extraction_type.replace('_', ' ').title())

        lines = [
            f"# {title}",
            "",
            f"**Video:** {video_title or video_id}",
            f"**Video ID:** {video_id}",
            f"**Extracted:** {timestamp}",
            f"**Model:** {model}",
            "",
            "---",
            ""
        ]

        if not items:
            lines.append("*No items found in this video.*")
            return '\n'.join(lines)

        # Generate items based on type
        if extraction_type == 'books':
            for i, item in enumerate(items, 1):
                author = item.get('author', 'Unknown')
                title_text = item.get('title', 'Untitled')
                mentioned_at = item.get('mentioned_at', '0:00')
                timestamp_seconds = item.get('timestamp_seconds', 0)
                context = item.get('context', '')
                item_type = item.get('type', 'book')

                lines.extend([
                    f"## {i}. \"{title_text}\" by {author}",
                    "",
                    f"**Type:** {item_type}",
                    f"**Mentioned at:** [{mentioned_at}](https://youtu.be/{video_id}?t={timestamp_seconds})",
                    ""
                ])
                if context:
                    lines.extend([f"> {context}", ""])
                lines.append("---")
                lines.append("")

        elif extraction_type == 'tools':
            for i, item in enumerate(items, 1):
                name = item.get('name', 'Unknown')
                mentioned_at = item.get('mentioned_at', '0:00')
                timestamp_seconds = item.get('timestamp_seconds', 0)
                context = item.get('context', '')
                category = item.get('category', 'tool')
                url = item.get('url')

                lines.extend([
                    f"## {i}. {name}",
                    "",
                    f"**Category:** {category}",
                    f"**Mentioned at:** [{mentioned_at}](https://youtu.be/{video_id}?t={timestamp_seconds})",
                ])
                if url:
                    lines.append(f"**URL:** {url}")
                lines.append("")
                if context:
                    lines.extend([f"> {context}", ""])
                lines.append("---")
                lines.append("")

        elif extraction_type == 'key_points':
            # Group by importance
            critical = [i for i in items if i.get('importance') == 'critical']
            important = [i for i in items if i.get('importance') == 'important']
            notable = [i for i in items if i.get('importance') not in ['critical', 'important']]

            def render_points(points: List[Dict], section_title: str, start_num: int) -> int:
                if not points:
                    return start_num
                lines.extend([f"## {section_title}", ""])
                for i, item in enumerate(points, start_num):
                    point = item.get('point', '')
                    mentioned_at = item.get('mentioned_at', '0:00')
                    timestamp_seconds = item.get('timestamp_seconds', 0)
                    context = item.get('context', '')

                    lines.extend([
                        f"### {i}. {point}",
                        "",
                        f"**Mentioned at:** [{mentioned_at}](https://youtu.be/{video_id}?t={timestamp_seconds})",
                        ""
                    ])
                    if context:
                        lines.extend([f"> {context}", ""])
                    lines.append("---")
                    lines.append("")
                return start_num + len(points)

            num = 1
            num = render_points(critical, "Critical Insights", num)
            num = render_points(important, "Important Points", num)
            render_points(notable, "Notable Observations", num)

        return '\n'.join(lines)

    def load_extraction(
        self,
        video_id: str,
        extraction_type: str,
        format: str = 'json'
    ) -> Optional[Union[Dict[str, Any], str]]:
        """
        Load extraction data.

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction
            format: 'json' returns dict, 'markdown' returns string

        Returns:
            Extraction data if exists, None otherwise
        """
        filepath = self.get_extraction_path(video_id, extraction_type, format)

        if not filepath.exists():
            logger.debug(f"Extraction file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if format == 'json':
                    return json.load(f)
                else:
                    return f.read()
        except Exception as e:
            logger.error(f"Failed to load extraction from {filepath}: {e}")
            return None

    def check_extraction_exists(self, video_id: str, extraction_type: str) -> bool:
        """
        Check if an extraction exists for a video.

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction

        Returns:
            True if extraction exists (checks JSON file)
        """
        filepath = self.get_extraction_path(video_id, extraction_type, 'json')
        return filepath.exists()

    def get_extraction_path(
        self,
        video_id: str,
        extraction_type: str,
        format: str = 'json'
    ) -> Path:
        """
        Get path to extraction file.

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction
            format: 'json' or 'markdown'

        Returns:
            Path to extraction file
        """
        ext = '.json' if format == 'json' else '.md'
        return self.ai_processed_dir / video_id / f"{extraction_type}{ext}"

    def delete_extraction(self, video_id: str, extraction_type: str) -> bool:
        """
        Delete both JSON and Markdown files for an extraction.

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction

        Returns:
            True if at least one file was deleted
        """
        json_path = self.get_extraction_path(video_id, extraction_type, 'json')
        md_path = self.get_extraction_path(video_id, extraction_type, 'markdown')

        deleted = False

        for filepath in [json_path, md_path]:
            if filepath.exists():
                try:
                    filepath.unlink()
                    logger.info(f"Deleted: {filepath}")
                    deleted = True
                except Exception as e:
                    logger.error(f"Failed to delete {filepath}: {e}")

        # Clean up empty directory
        if deleted:
            video_dir = json_path.parent
            if video_dir.exists() and not any(video_dir.iterdir()):
                video_dir.rmdir()
                logger.debug(f"Removed empty directory: {video_dir}")

        return deleted

    def get_extraction_metadata(
        self,
        video_id: str,
        extraction_type: str,
        model: str,
        item_count: int
    ) -> Dict[str, Any]:
        """
        Generate metadata entry for an extraction.

        Args:
            video_id: YouTube video ID
            extraction_type: Type of extraction
            model: AI model used
            item_count: Number of items extracted

        Returns:
            Metadata dictionary for storage in video metadata
        """
        json_path = self.get_extraction_path(video_id, extraction_type, 'json')
        md_path = self.get_extraction_path(video_id, extraction_type, 'markdown')

        # Convert paths to absolute before creating relative path
        abs_json = json_path.resolve()
        abs_md = md_path.resolve()
        abs_base = self.base_output_dir.resolve()

        metadata = {
            "created_at": datetime.now().isoformat(),
            "model": model,
            "count": item_count,
            "file": str(abs_json.relative_to(abs_base)),
            "markdown_file": str(abs_md.relative_to(abs_base))
        }

        # Add file sizes if they exist
        if json_path.exists():
            metadata["size_bytes"] = json_path.stat().st_size
        if md_path.exists():
            metadata["markdown_size_bytes"] = md_path.stat().st_size

        return metadata

    def get_available_extractions(self, video_id: str) -> Dict[str, Dict[str, Path]]:
        """
        Get all available extractions for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary mapping extraction type to {'json': Path, 'md': Path}
        """
        available = {}
        video_dir = self.ai_processed_dir / video_id

        if not video_dir.exists():
            return available

        for extraction_type in EXTRACTION_TYPES:
            json_path = video_dir / f"{extraction_type}.json"
            md_path = video_dir / f"{extraction_type}.md"

            if json_path.exists() or md_path.exists():
                available[extraction_type] = {
                    'json': json_path if json_path.exists() else None,
                    'md': md_path if md_path.exists() else None
                }

        return available
