"""Format output with colors and styling."""

import json
from typing import List, Dict, Any


class Colors:
    """ANSI color codes."""
    RESET = '\033[0m'
    DIM = '\033[90m'
    BRIGHT_WHITE = '\033[97m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    RED = '\033[91m'

    @staticmethod
    def get_title(command: str = None):
        """Get colored YTC title: Red=YouTube, Green=Transcript, Blue=Curator.

        Args:
            command: Optional command name. If provided, appends " > command"

        Returns:
            Colored title, optionally with command name
        """
        title = f"🎬 {Colors.RED}YouTube{Colors.RESET} {Colors.GREEN}Transcript{Colors.RESET} {Colors.BLUE}Curator{Colors.RESET}"
        if command:
            return f"{title} > {command}"
        return title

    @staticmethod
    def get_command_title(command: str):
        """Get colored YTC title with command name.

        Args:
            command: Command name (fetch, list, search, etc.)

        Returns:
            Formatted title with command: 🎬 YouTube Transcript Curator > command
        """
        return Colors.get_title(command)


class TemplateFormatter:
    """Handle template-based formatting with placeholders."""

    # Color mapping for each field
    FIELD_COLORS = {
        'id': Colors.DIM,
        'video_id': Colors.DIM,
        'title': Colors.GREEN,
        'channel': Colors.CYAN,
        'duration': Colors.YELLOW,
        'duration_string': Colors.YELLOW,
        'type': None,  # Special handling for type
        'video_type': None,  # Special handling for type
        'published': Colors.MAGENTA,
        'upload_date': Colors.MAGENTA,
        'processed': Colors.BRIGHT_WHITE,
        'processed_at': Colors.BRIGHT_WHITE,
        'views': Colors.BLUE,
        'view_count': Colors.BLUE,
    }

    # Placeholder to field mapping
    PLACEHOLDER_MAP = {
        'i': 'video_id',
        'id': 'video_id',
        't': 'title',
        'title': 'title',
        'c': 'channel',
        'channel': 'channel',
        'd': 'duration_string',
        'duration': 'duration_string',
        'T': 'video_type',
        'type': 'video_type',
        'p': 'upload_date',
        'published': 'upload_date',
        'P': 'processed_at',
        'processed': 'processed_at',
        'v': 'view_count',
        'views': 'view_count',
    }

    @staticmethod
    def get_type_badge(vtype):
        """Get colored type badge."""
        if vtype == 'regular':
            return f"{Colors.GREEN}[Regular]{Colors.RESET}"
        elif vtype == 'livestream_recording':
            return f"{Colors.BLUE}[Livestream Recording]{Colors.RESET}"
        elif vtype == 'livestream':
            return f"{Colors.MAGENTA}[Livestream]{Colors.RESET}"
        else:
            return f"{Colors.DIM}[Unknown]{Colors.RESET}"

    @staticmethod
    def format_field(field_name, value):
        """Format a field value with appropriate color."""
        if not value:
            return ''

        # Special handling for type
        if field_name in ('video_type', 'type'):
            return TemplateFormatter.get_type_badge(value)

        # Get color for this field
        color = TemplateFormatter.FIELD_COLORS.get(field_name, Colors.RESET)
        if color:
            return f"{color}{value}{Colors.RESET}"
        return str(value)

    @staticmethod
    def format_with_template(template, video):
        """Format video using a template string with placeholders."""
        result = template

        # Find all placeholders like %i, %title, etc.
        import re
        placeholders = re.findall(r'%(\w+)', template)

        for placeholder in placeholders:
            field_name = TemplateFormatter.PLACEHOLDER_MAP.get(placeholder, placeholder)
            value = video.get(field_name, '')

            formatted_value = TemplateFormatter.format_field(field_name, str(value))
            result = result.replace(f'%{placeholder}', formatted_value)

        return result


class Formatter:
    """Format video lists and metadata for display."""

    @staticmethod
    def format_video_compact(video: Dict[str, Any], sort_key: str = None) -> str:
        """
        Format video in compact format: ID | Title | Channel | [Injected Field] | Duration [Type]

        If sort_key is provided and is not 'date', auto-inject the sort field between channel and duration.

        Args:
            video: Video metadata dictionary
            sort_key: Current sort key (for auto-injection)

        Returns:
            Formatted string with colors
        """
        video_id = video.get('video_id', '')
        title = video.get('title', 'Unknown')
        channel = video.get('channel', 'Unknown')
        duration = video.get('duration_string', '0:00')
        vtype = video.get('video_type', 'unknown')

        # Truncate title if too long (max 50 chars)
        title_display = title[:50] + '...' if len(title) > 50 else title

        # Format type badge with color
        type_badge = TemplateFormatter.get_type_badge(vtype)

        # Build base format
        parts = [
            f"{Colors.DIM}{video_id}{Colors.RESET}",
            f"{Colors.GREEN}{title_display}{Colors.RESET}",
            f"{Colors.CYAN}{channel}{Colors.RESET}",
        ]

        # Auto-inject sort field between channel and duration (if needed)
        if sort_key and sort_key not in ('date', 'title', 'channel', 'duration'):
            if sort_key == 'published':
                injected = f"{Colors.MAGENTA}{video.get('upload_date', 'N/A')}{Colors.RESET}"
            elif sort_key == 'views':
                injected = f"{Colors.BLUE}{video.get('view_count', '0')}{Colors.RESET}"
            elif sort_key == 'processed':
                injected = f"{Colors.BRIGHT_WHITE}{video.get('processed_at', 'N/A')}{Colors.RESET}"
            else:
                injected = None

            if injected:
                parts.append(injected)

        # Add duration and type
        parts.append(f"{Colors.YELLOW}{duration}{Colors.RESET}")
        parts.append(type_badge)

        return ' | '.join(parts[:-1]) + f" {parts[-1]}"

    @staticmethod
    def format_video_full(video: Dict[str, Any]) -> str:
        """
        Format video with full details (multi-line).

        Args:
            video: Video metadata dictionary

        Returns:
            Formatted multi-line string
        """
        lines = []
        lines.append(f"\n{Colors.BRIGHT_WHITE}📺 {video.get('title', 'Unknown')}{Colors.RESET}")
        lines.append(f"   {Colors.DIM}ID:{Colors.RESET} {video.get('video_id')}")
        lines.append(f"   {Colors.CYAN}Channel:{Colors.RESET} {video.get('channel', 'Unknown')}")
        lines.append(f"   {Colors.YELLOW}Duration:{Colors.RESET} {video.get('duration_string', '0:00')}")

        vtype = video.get('video_type', 'unknown')
        if vtype == 'regular':
            type_display = f"{Colors.GREEN}Regular{Colors.RESET}"
        elif vtype == 'livestream_recording':
            type_display = f"{Colors.BLUE}Livestream Recording{Colors.RESET}"
        elif vtype == 'livestream':
            type_display = f"{Colors.MAGENTA}Livestream{Colors.RESET}"
        else:
            type_display = f"{Colors.DIM}Unknown{Colors.RESET}"

        lines.append(f"   Type: {type_display}")
        lines.append(f"   {Colors.DIM}Uploaded:{Colors.RESET} {video.get('upload_date', 'Unknown')}")
        lines.append(f"   {Colors.DIM}Processed:{Colors.RESET} {video.get('processed_at', 'Unknown')}")
        lines.append(f"   {Colors.DIM}URL:{Colors.RESET} {video.get('url', 'N/A')}")

        return '\n'.join(lines)

    @staticmethod
    def format_video_ids_only(videos: List[Dict[str, Any]]) -> str:
        """
        Format videos as simple list of IDs.

        Args:
            videos: List of video metadata dictionaries

        Returns:
            Newline-separated video IDs
        """
        return '\n'.join(v.get('video_id', '') for v in videos)

    @staticmethod
    def format_video_json(videos: List[Dict[str, Any]]) -> str:
        """
        Format videos as JSON.

        Args:
            videos: List of video metadata dictionaries

        Returns:
            JSON string
        """
        return json.dumps(videos, indent=2)

    @staticmethod
    def format_videos_list(
        videos: List[Dict[str, Any]],
        format_type: str = 'compact',
        limit: int = None,
        sort_key: str = None
    ) -> str:
        """
        Format list of videos.

        Args:
            videos: List of video metadata dictionaries
            format_type: Format type (compact, full, ids, json, or template with %)
            limit: Maximum number of videos to display
            sort_key: Current sort key (for auto-injection into compact format)

        Returns:
            Formatted string
        """
        if limit:
            videos = videos[:limit]

        # Check if format_type is a template (contains %)
        if '%' in format_type:
            # Template format - use exactly as specified
            lines = [TemplateFormatter.format_with_template(format_type, v) for v in videos]
            return '\n'.join(lines)
        elif format_type == 'compact':
            # Compact format with possible auto-injection
            lines = [Formatter.format_video_compact(v, sort_key=sort_key) for v in videos]
            return '\n'.join(lines)
        elif format_type == 'full':
            return '\n'.join(Formatter.format_video_full(v) for v in videos)
        elif format_type == 'ids':
            return Formatter.format_video_ids_only(videos)
        elif format_type == 'json':
            return Formatter.format_video_json(videos)
        else:
            return Formatter.format_videos_list(videos, 'compact', limit, sort_key)

    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove ANSI color codes from text."""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

    @staticmethod
    def format_videos_aligned(
        videos: List[Dict[str, Any]],
        limit: int = None,
        sort_key: str = None
    ) -> str:
        """
        Format videos with aligned columns (no borders, same colors as compact).

        Columns are vertically aligned with proper spacing, using same color scheme
        as compact format: ID | Title | Channel | [Optional Sort Field] | Duration [Type]

        Args:
            videos: List of video metadata dictionaries
            limit: Maximum number of videos to display
            sort_key: Current sort key (for auto-injection, like in compact format)

        Returns:
            Formatted string with aligned columns
        """
        if limit:
            videos = videos[:limit]

        if not videos:
            return ""

        # Prepare data for each video
        rows = []
        for video in videos:
            video_id = video.get('video_id', '')
            title = video.get('title', 'Unknown')
            channel = video.get('channel', 'Unknown')
            duration = video.get('duration_string', '0:00')
            vtype = video.get('video_type', 'unknown')

            # Truncate title (same as compact: max 50 chars)
            title_display = title[:50] + '...' if len(title) > 50 else title
            # Escape pipe characters in title to prevent breaking alignment
            title_display = title_display.replace('|', '·')

            # Format type badge with color
            type_badge = TemplateFormatter.get_type_badge(vtype)

            # Build parts with colors (same as compact format)
            parts = [
                f"{Colors.DIM}{video_id}{Colors.RESET}",
                f"{Colors.GREEN}{title_display}{Colors.RESET}",
                f"{Colors.CYAN}{channel}{Colors.RESET}",
            ]

            # Auto-inject sort field (same logic as compact)
            if sort_key and sort_key not in ('date', 'title', 'channel', 'duration'):
                if sort_key == 'published':
                    injected = f"{Colors.MAGENTA}{video.get('upload_date', 'N/A')}{Colors.RESET}"
                elif sort_key == 'views':
                    injected = f"{Colors.BLUE}{video.get('view_count', '0')}{Colors.RESET}"
                elif sort_key == 'processed':
                    injected = f"{Colors.BRIGHT_WHITE}{video.get('processed_at', 'N/A')}{Colors.RESET}"
                else:
                    injected = None

                if injected:
                    parts.append(injected)

            # Add duration and type
            parts.append(f"{Colors.YELLOW}{duration}{Colors.RESET}")
            parts.append(type_badge)

            # Store raw parts for column width calculation
            # (strip ANSI codes for width calculation)
            raw_parts = [Formatter.strip_ansi(p) for p in parts]
            rows.append((parts, raw_parts))

        # Calculate column widths dynamically based on actual data
        # Determine max number of columns across all rows
        max_cols = max(len(r[1]) for r in rows) if rows else 4

        col_widths = []
        for col_idx in range(max_cols):
            # Get max width for this column across all rows
            col_values = [r[1][col_idx] for r in rows if col_idx < len(r[1])]
            max_width = max(len(v) for v in col_values) if col_values else 0

            # Apply minimum widths for known columns
            if col_idx == 0:  # ID
                col_widths.append(max(11, max_width))
            elif col_idx == 1:  # Title - cap at 50 for display, but use actual width if less
                title_width = max(20, max_width)
                # If max_width is > 50, we truncated in display, so use 50+dots
                # Otherwise use the actual width for proper alignment
                if max_width > 53:  # 50 chars + "..." from truncation
                    col_widths.append(53)
                else:
                    col_widths.append(title_width)
            elif col_idx == 2:  # Channel
                col_widths.append(max(15, max_width))
            elif col_idx == max_cols - 1:  # Type badge (last column)
                col_widths.append(max(20, max_width))
            elif col_idx == max_cols - 2:  # Duration (second to last column)
                col_widths.append(max(12, max_width))
            else:  # Optional injected fields (middle columns, indices 3 through max_cols-3)
                col_widths.append(max(12, max_width))

        # Format lines with proper alignment
        lines = []
        for parts, raw_parts in rows:
            formatted_parts = []
            for i, (part, raw) in enumerate(zip(parts, raw_parts)):
                width = col_widths[i] if i < len(col_widths) else 20
                # Calculate padding needed (visible text width, not ANSI-including width)
                padding_needed = width - len(raw)
                # Pad the part with spaces (adding padding AFTER the color codes end)
                padded_part = part + (' ' * padding_needed)
                formatted_parts.append(padded_part)

            # Build line with proper separators
            formatted_line = ""
            for i, padded_part in enumerate(formatted_parts):
                if i == len(formatted_parts) - 1:  # Last column (type badge)
                    formatted_line += padded_part
                elif i == len(formatted_parts) - 2:  # Duration column
                    formatted_line += padded_part + " "
                else:
                    formatted_line += padded_part + " | "

            lines.append(formatted_line)

        return '\n'.join(lines)

    @staticmethod
    def format_statistics(stats: Dict[str, Any]) -> str:
        """
        Format library statistics.

        Args:
            stats: Statistics dictionary from LibraryManager

        Returns:
            Formatted string
        """
        lines = []
        lines.append(f"\n{Colors.BRIGHT_WHITE}📊 Transcript Library Statistics{Colors.RESET}\n")

        lines.append(f"Total videos: {Colors.YELLOW}{stats.get('total_videos', 0)}{Colors.RESET}")
        lines.append(f"Total duration: {Colors.YELLOW}{stats.get('total_duration_formatted', '0h 0m')}{Colors.RESET}")

        if stats.get('total_videos', 0) > 0:
            avg_minutes = stats.get('average_duration_minutes', 0)
            avg_hours = avg_minutes // 60
            avg_mins = avg_minutes % 60
            lines.append(f"Average duration: {Colors.YELLOW}{avg_hours}h {avg_mins}m{Colors.RESET}")

        # By type
        by_type = stats.get('by_type', {})
        if by_type:
            lines.append(f"\n{Colors.CYAN}By type:{Colors.RESET}")
            for vtype, info in sorted(by_type.items()):
                count = info.get('count', 0)
                duration = info.get('duration', 0)
                minutes = duration // 60
                hours = minutes // 60
                mins = minutes % 60

                if vtype == 'regular':
                    badge = f"{Colors.GREEN}Regular{Colors.RESET}"
                elif vtype == 'livestream_recording':
                    badge = f"{Colors.BLUE}Livestream Recording{Colors.RESET}"
                else:
                    badge = vtype

                lines.append(f"  {badge}: {Colors.YELLOW}{count}{Colors.RESET} video{'s' if count != 1 else ''} ({hours}h {mins}m)")

        # By channel (top 10)
        by_channel = stats.get('by_channel', {})
        if by_channel:
            lines.append(f"\n{Colors.CYAN}Top channels:{Colors.RESET}")
            for idx, (channel, info) in enumerate(by_channel.items(), 1):
                count = info.get('count', 0)
                duration = info.get('duration', 0)
                minutes = duration // 60
                hours = minutes // 60
                mins = minutes % 60
                lines.append(f"  {idx}. {Colors.BRIGHT_WHITE}{channel}{Colors.RESET} ({Colors.YELLOW}{count}{Colors.RESET} video{'s' if count != 1 else ''}, {hours}h {mins}m)")

        return '\n'.join(lines)

    @staticmethod
    def format_search_results(results: Dict[str, Dict[str, Any]]) -> str:
        """
        Format transcript search results.

        Args:
            results: Search results dictionary from LibraryManager

        Returns:
            Formatted string
        """
        if not results:
            return f"{Colors.YELLOW}No matches found.{Colors.RESET}"

        lines = [f"\n{Colors.BRIGHT_WHITE}🔍 Search Results{Colors.RESET}\n"]

        total_matches = sum(r.get('match_count', 0) for r in results.values())
        lines.append(f"Found {Colors.YELLOW}{total_matches}{Colors.RESET} matches in {Colors.YELLOW}{len(results)}{Colors.RESET} video{'s' if len(results) != 1 else ''}\n")

        for video_id, result in results.items():
            title = result.get('title', 'Unknown')
            channel = result.get('channel', 'Unknown')
            match_count = result.get('match_count', 0)

            lines.append(f"{Colors.BRIGHT_WHITE}📺 {title}{Colors.RESET} {Colors.DIM}|{Colors.RESET} {Colors.DIM}{video_id}{Colors.RESET}")
            lines.append(f"   {Colors.CYAN}{channel}{Colors.RESET} ({Colors.YELLOW}{match_count}{Colors.RESET} matches)")

            # Show first few matches
            matches = result.get('matches', [])[:5]
            for match in matches:
                line_num = match.get('line_number', 0)
                text = match.get('text', '')
                # Truncate long lines
                if len(text) > 80:
                    text = text[:77] + '...'
                lines.append(f"      Line {Colors.DIM}{line_num}{Colors.RESET}: {text}")

            if len(result.get('matches', [])) > 5:
                remaining = len(result.get('matches', [])) - 5
                lines.append(f"      {Colors.DIM}... and {remaining} more match{'es' if remaining != 1 else ''}{Colors.RESET}")

            lines.append('')

        return '\n'.join(lines)
