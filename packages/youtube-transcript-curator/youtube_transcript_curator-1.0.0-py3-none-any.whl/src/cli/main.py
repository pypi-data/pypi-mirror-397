"""Command-line interface for YouTube Transcript Curator."""

import click
import sys
import logging
import builtins
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logging, get_logger
from src.utils.url_parser import YouTubeURLParser
from src.utils.formatter import Formatter, Colors
from src.core.metadata_fetcher import MetadataFetcher
from src.core.transcript_fetcher import TranscriptFetcher
from src.core.output_manager import OutputManager
from src.core.library_manager import LibraryManager
from src.core.library_logger import LibraryLogger
from src.cli.config_command import config as config_cmd

logger = get_logger(__name__)


def _short_path(path: Path | str) -> str:
    """Return a shorter display path (relative to cwd or using ~)."""
    path = Path(path).resolve()
    cwd = Path.cwd().resolve()
    home = Path.home()

    # Try relative to current directory first
    try:
        rel = path.relative_to(cwd)
        return f"./{rel}"
    except ValueError:
        pass

    # Try home-relative path
    try:
        rel = path.relative_to(home)
        return f"~/{rel}"
    except ValueError:
        pass

    # Fall back to absolute
    return str(path)


@click.group()
@click.pass_context
def cli(ctx):
    """YouTube Transcript Curator - Curate, organize, and explore YouTube transcripts."""
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Load configuration
    try:
        config = ConfigLoader()
        ctx.obj['config'] = config

        # Setup logging
        log_level = config.get_log_level()
        log_file = config.get('logging.file')
        log_format = config.get('logging.format')
        console_output = config.get('logging.console_output', True)

        # Resolve log file path to absolute path (project root) if relative
        if log_file:
            log_file_path = Path(log_file)
            if not log_file_path.is_absolute():
                project_root = Path(__file__).parent.parent.parent
                log_file_path = project_root / log_file_path
        else:
            log_file_path = None

        setup_logging(
            log_level=log_level,
            log_file=log_file_path,
            console_output=console_output,
            log_format=log_format
        )

        # Only log initialization to file, not console (avoids clutter in help/etc)
        logger.debug(f"YouTube Transcript Curator v{config.get_version()} initialized")

    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('url')
@click.option('--overwrite', is_flag=True, help='Overwrite existing files')
@click.option('--no-timestamps', is_flag=True, help='Exclude timestamps from transcript')
@click.option('--output-dir', type=click.Path(), help='Custom output directory')
@click.pass_context
def fetch(ctx, url: str, overwrite: bool, no_timestamps: bool, output_dir: Optional[str]):
    """Fetch transcript and metadata for a YouTube video.

    URL: YouTube video URL (any format) or video ID

    Examples:

        ytc fetch "https://www.youtube.com/watch?v=VIDEO_ID"

        ytc fetch "https://youtu.be/VIDEO_ID"

        ytc fetch VIDEO_ID
    """
    config = ctx.obj['config']

    click.echo()
    click.echo(Colors.get_command_title("fetch"))
    click.echo("=" * 50)

    # Step 1: Parse and validate URL
    click.echo("\n📎 Parsing URL...")
    video_id = YouTubeURLParser.extract_video_id(url)

    if not video_id:
        click.echo(f"❌ Invalid YouTube URL: {url}", err=True)
        click.echo("\nSupported formats:")
        click.echo("  - https://www.youtube.com/watch?v=VIDEO_ID")
        click.echo("  - https://youtu.be/VIDEO_ID")
        click.echo("  - VIDEO_ID (11 characters)")
        sys.exit(1)

    standard_url = YouTubeURLParser.build_standard_url(video_id)
    click.echo(f"✓ Video ID: {video_id}")
    logger.info(f"Processing video: {video_id}")

    # Step 2: Setup output manager
    output_base_dir = Path(output_dir) if output_dir else config.get_output_dir()
    should_overwrite = overwrite or config.should_overwrite_files()
    output_manager = OutputManager(output_base_dir, overwrite=should_overwrite)

    # Check if files already exist
    existing_files = output_manager.check_file_exists(video_id)
    if any(existing_files.values()) and not should_overwrite:
        click.echo("\n⚠️  Files already exist for this video:")
        for file_type, exists in existing_files.items():
            if exists:
                click.echo(f"   - {file_type}")
        click.echo("\nUse --overwrite to replace existing files.")
        sys.exit(1)

    # Step 3: Fetch metadata
    click.echo("\n📋 Fetching video metadata...")
    try:
        metadata_fetcher = MetadataFetcher()
        metadata = metadata_fetcher.fetch(video_id, standard_url)

        click.echo("\n📺 Video Info:")
        click.echo(f"        Title: {metadata['title']}")
        click.echo(f"     Duration: {metadata['duration_string']}")
        if metadata['view_count']:
            click.echo(f"        Views: {metadata['view_count']:,}")
        click.echo(f"      Channel: {metadata['channel']}")
        if metadata.get('channel_subscribers'):
            click.echo(f"  Subscribers: {metadata['channel_subscribers']:,}")
        if metadata.get('upload_date'):
            click.echo(f"     Uploaded: {metadata['upload_date']}")

        if not metadata['has_captions']:
            click.echo("\n⚠️  Warning: Video may not have captions available")

    except Exception as e:
        click.echo(f"\n❌ Failed to fetch metadata: {e}", err=True)
        logger.error(f"Metadata fetch failed for {video_id}: {e}")
        sys.exit(1)

    # Step 4: Fetch transcript
    click.echo("\n📝 Fetching transcript...")
    try:
        preferred_languages = config.get('transcript.languages', ['en'])
        transcript_fetcher = TranscriptFetcher(preferred_languages=preferred_languages)

        transcript_data = transcript_fetcher.fetch(video_id)
        include_timestamps = not no_timestamps
        transcript_text = transcript_fetcher.format_transcript(
            transcript_data,
            include_timestamps=include_timestamps
        )

        click.echo(f"✓ Retrieved {len(transcript_data)} transcript segments")

    except Exception as e:
        click.echo(f"\n❌ Failed to fetch transcript: {e}", err=True)
        logger.error(f"Transcript fetch failed for {video_id}: {e}")
        sys.exit(1)

    # Step 5: Save files
    click.echo(f"\n💾 Saving to {_short_path(output_base_dir)}")
    try:
        # Save transcript
        transcript_path = output_manager.save_transcript(transcript_text, video_id)
        trans_filename = Path(transcript_path).name
        click.echo(f"✓ transcripts/{trans_filename}")

        # Update metadata with file reference
        metadata = output_manager.update_metadata_with_file_references(
            metadata,
            transcript_path
        )

        # Save metadata
        metadata_path = output_manager.save_metadata(metadata, video_id)
        meta_filename = Path(metadata_path).name
        click.echo(f"✓ metadata/{meta_filename}")

    except FileExistsError as e:
        click.echo(f"\n❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Failed to save files: {e}", err=True)
        logger.error(f"File save failed for {video_id}: {e}")
        sys.exit(1)

    # Success summary
    click.echo("\n" + "=" * 50)
    click.echo("✅ Success!")

    click.echo("\n💡 Quick access:")
    click.echo("   ytc info --last")
    click.echo("   ytc open --last")
    click.echo("   ytc open --last --code")
    click.echo("   ytc open --last --meta")
    click.echo()

    logger.info(f"Successfully processed video: {video_id}")

    # Log the fetch to library change log
    log_dir = Path(output_base_dir) / 'logs'
    lib_logger = LibraryLogger(log_dir)
    lib_logger.log_fetch(
        video_id=video_id,
        title=metadata['title'],
        channel=metadata['channel'],
        url=standard_url
    )


@cli.command()
@click.argument('input_id', required=False)
@click.option('--last', is_flag=True, help='Show info for the most recently fetched video')
@click.option('--description', is_flag=True, help='Show video description')
@click.pass_context
def info(ctx, input_id: str, last: bool, description: bool):
    """
    Show information about a processed video.

    INPUT_ID: YouTube video ID or URL (or use --last for most recent)
    """
    config = ctx.obj['config']

    click.echo()
    click.echo(Colors.get_command_title("info"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    output_manager = OutputManager(output_dir)

    # Handle --last flag to get most recent video
    if last:
        from src.core.library_manager import LibraryManager
        metadata_dir = Path(output_dir) / 'metadata'
        library = LibraryManager(metadata_dir)
        videos = library.get_all_videos()

        if not videos:
            click.echo("❌ No videos found in library", err=True)
            sys.exit(1)

        # Sort by date (most recent first) and get the first one
        sorted_videos = library.sort_by(videos, 'date', reverse=False)
        most_recent = sorted_videos[0]
        input_id = most_recent.get('video_id')

    # Validate input_id is provided or determined
    if not input_id:
        click.echo("❌ Error: INPUT_ID is required (or use --last flag)", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc info VIDEO_ID           # Show specific video", err=True)
        click.echo("  ytc info --last             # Show most recent video", err=True)
        sys.exit(1)

    # Parse input - extract video ID if URL provided
    video_id = YouTubeURLParser.extract_video_id(input_id)
    if not video_id:
        click.echo(f"❌ Invalid YouTube URL or video ID: {input_id}", err=True)
        click.echo("\nSupported formats:")
        click.echo("  - https://www.youtube.com/watch?v=VIDEO_ID")
        click.echo("  - https://youtu.be/VIDEO_ID")
        click.echo("  - VIDEO_ID (11 characters)")
        sys.exit(1)

    # Check what files exist
    existing_files = output_manager.check_file_exists(video_id)
    file_paths = output_manager.get_file_paths(video_id)

    if not any(existing_files.values()):
        click.echo(f"\n❌ No files found for video: {video_id}")
        click.echo("\nRun: ytc fetch <URL>")
        sys.exit(1)

    # If metadata exists, show details
    if existing_files['metadata']:
        import json
        with builtins.open(file_paths['metadata'], 'r') as f:
            metadata = json.load(f)

        # Video Info section (aligned labels)
        click.echo("\n📺 Video Info:")
        click.echo(f"        Title: {metadata.get('title')}")
        click.echo(f"     Duration: {metadata.get('duration_string')}")
        views = metadata.get('view_count', 0)
        if views:
            click.echo(f"        Views: {views:,}")
        click.echo(f"      Channel: {metadata.get('channel')}")
        subs = metadata.get('channel_subscribers', 0)
        if subs:
            click.echo(f"  Subscribers: {subs:,}")
        upload = metadata.get('upload_date')
        if upload:
            click.echo(f"     Uploaded: {upload}")
        click.echo(f"         Type: {metadata.get('video_type', 'unknown').replace('_', ' ').title()}")
        click.echo(f"          URL: {metadata.get('url')}")

        # Processing section (aligned labels)
        click.echo("\n🔧 Processing:")
        processed = metadata.get('processed_at', '')
        if processed:
            # Truncate microseconds for cleaner display
            processed = processed.split('.')[0].replace('T', ' ')
        click.echo(f"      Fetched: {processed}")
        click.echo(f"    Formatted: {'Yes' if existing_files.get('formatted') else 'No'}")
        click.echo("      Summary: No")

        # Show description if --description flag is used
        if description:
            desc = metadata.get('description', '')
            if desc:
                click.echo("\n📄 Description:")
                click.echo(f"   {desc}")
            else:
                click.echo("\n📄 Description: Not available")

    # Files section with short paths
    click.echo(f"\n📁 Files saved to: {_short_path(output_dir)}")
    if existing_files.get('transcript'):
        trans_name = Path(file_paths['transcript']).name
        click.echo(f"   ✓ transcripts/{trans_name}")
    if existing_files.get('metadata'):
        meta_name = Path(file_paths['metadata']).name
        click.echo(f"   ✓ metadata/{meta_name}")
    if existing_files.get('formatted'):
        fmt_name = Path(file_paths['formatted']).name
        click.echo(f"   ✓ formatted/{fmt_name}")
    click.echo()


@cli.command(name='list')
@click.option('--format', default='compact', help='Output format (compact, full, ids, json, or custom template with % placeholders)')
@click.option('--type', 'video_type', help='Filter by type (regular, livestream, livestream_recording)')
@click.option('--channel', help='Filter by channel name')
@click.option('--sort', type=click.Choice(['date', 'published', 'title', 'channel', 'duration', 'views']), default='date', help='Sort by field')
@click.option('--reverse', is_flag=True, help='Reverse sort order')
@click.option('--limit', type=int, help='Limit number of results')
@click.option('--align', is_flag=True, help='Display with vertically aligned columns')
@click.pass_context
def list(ctx, format, video_type, channel, sort, reverse, limit, align):
    """List all transcribed videos."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("list"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    metadata_dir = Path(output_dir) / 'metadata'

    # Load library
    library = LibraryManager(metadata_dir)
    videos = library.get_all_videos()

    if not videos:
        click.echo("📭 No transcribed videos found.")
        return

    # Apply filters
    if video_type:
        try:
            videos = library.filter_by_type(video_type)
        except ValueError as e:
            click.echo(f"❌ {e}", err=True)
            click.echo("\nTip: Tab completion shows available types:", err=True)
            click.echo("  yt list --type <TAB>", err=True)
            click.echo("\nYou can also use fuzzy matches: live, rec, reg, ls", err=True)
            sys.exit(1)
    if channel:
        videos = library.filter_by_channel(channel)

    # Apply sorting
    videos = library.sort_by(videos, sort, reverse)

    # Format and display
    if align:
        # Use aligned format with vertically aligned columns (ignores --format flag when --align is used)
        output = Formatter.format_videos_aligned(videos, limit=limit, sort_key=sort)
    else:
        # Use specified format (pass sort_key for auto-injection in compact format)
        output = Formatter.format_videos_list(videos, format, limit, sort_key=sort)

    click.echo(output)

    if not videos:
        click.echo("\n❌ No videos match the filters.")


@cli.command()
@click.argument('video_id', required=False)
@click.option('--meta', is_flag=True, help='Open metadata file instead of transcript')
@click.option('--summary', is_flag=True, help='Open AI-generated summary instead of transcript')
@click.option('--length', type=click.Choice(['short', 'medium', 'long'], case_sensitive=False), default='medium', help='Summary length to open (use with --summary)')
@click.option('--books', 'open_books', is_flag=True, help='Open extracted books list')
@click.option('--tools', 'open_tools', is_flag=True, help='Open extracted tools list')
@click.option('--key-points', 'open_key_points', is_flag=True, help='Open extracted key points')
@click.option('--code', is_flag=True, help='Open in VS Code editor (default)')
@click.option('--finder', is_flag=True, help='Open in Finder instead of editor')
@click.option('--youtube', is_flag=True, help='Open in YouTube/Chrome browser')
@click.option('--time', help='Jump to timestamp (format: MM:SS, HH:MM:SS, seconds, or 1m30s)')
@click.option('--search', help='Fuzzy search for keyword in transcript and open YouTube at matching timestamp')
@click.option('--last', is_flag=True, help='Open the most recently fetched video')
@click.pass_context
def open(ctx, video_id, meta, summary, length, open_books, open_tools, open_key_points, code, finder, youtube, time, search, last):
    """Open transcript, metadata, summary, or extracted data."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("open"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()

    # Handle --last flag to get most recent video
    if last:
        from src.core.library_manager import LibraryManager
        metadata_dir = Path(output_dir) / 'metadata'
        library = LibraryManager(metadata_dir)
        videos = library.get_all_videos()

        if not videos:
            click.echo("❌ No videos found in library", err=True)
            sys.exit(1)

        # Sort by date (most recent first) and get the first one
        sorted_videos = library.sort_by(videos, 'date', reverse=False)
        most_recent = sorted_videos[0]
        video_id = most_recent.get('video_id')

        if not video_id:
            click.echo("❌ Could not determine video ID from most recent video", err=True)
            sys.exit(1)

        click.echo(f"📺 Most recent: {most_recent.get('title', 'Unknown')}")
        click.echo(f"   Video ID: {video_id}\n")

    # Validate video_id is provided or determined
    if not video_id:
        click.echo("❌ Error: VIDEO_ID is required (or use --last flag)", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc open VIDEO_ID           # Open specific video", err=True)
        click.echo("  ytc open --last             # Open most recent video", err=True)
        sys.exit(1)

    # Handle YouTube opening with fuzzy search
    if youtube or search:
        from src.core.video_opener import VideoOpener

        output_manager = OutputManager(output_dir)
        file_paths = output_manager.get_file_paths(video_id)
        existing_files = output_manager.check_file_exists(video_id)

        # Check if transcript exists for search
        if search:
            if not existing_files['transcript']:
                click.echo(f"❌ Transcript file not found for {video_id}", err=True)
                sys.exit(1)

            # Search in transcript
            opener = VideoOpener()
            transcript_file = file_paths['transcript']
            search_result = opener.search_transcript_for_keyword(
                video_id=video_id,
                keyword=search,
                transcript_file=transcript_file,
                max_results=5
            )

            if search_result['error']:
                click.echo(f"❌ Error searching transcript: {search_result['error']}", err=True)
                sys.exit(1)

            matches = search_result['matches']
            total_found = search_result['total_found']

            # Handle no matches
            if not matches:
                click.echo(f"✗ No matches found for '{search}' in {video_id}")
                click.echo(f"Try: ytc search {search}  # to find across all videos")
                sys.exit(1)

            # Handle single match - auto-open
            if len(matches) == 1:
                match = matches[0]
                click.echo(f"✓ Found 1 match for '{search}'")
                click.echo(f"[{match['timestamp_str']}] {match['excerpt']}")
                click.echo(f"→ Opening YouTube at {match['timestamp_str']}...")

                opener = VideoOpener()
                if opener.open_youtube(video_id, time_seconds=match['timestamp_seconds']):
                    click.echo(f"✓ Opened YouTube video {video_id} at {match['timestamp_str']}")
                else:
                    click.echo("❌ Failed to open YouTube video", err=True)
                    sys.exit(1)
                return

            # Handle multiple matches - show menu
            if len(matches) <= 5:
                click.echo(f"Found {len(matches)} matches for '{search}' in {video_id}:\n")
            else:
                click.echo(f"Found {total_found}+ matches for '{search}' in {video_id}")
                click.echo("Showing first 5 matches:\n")

            for i, match in enumerate(matches, 1):
                click.echo(f"[{i}] [{match['timestamp_str']}] {match['excerpt']}")

            click.echo()
            # Interactive selection
            while True:
                user_input = click.prompt("Select match (1-5) or press Enter for [1]", default="1", show_default=False)
                try:
                    selection = int(user_input)
                    if 1 <= selection <= len(matches):
                        selected_match = matches[selection - 1]
                        break
                    else:
                        click.echo(f"❌ Please enter a number between 1 and {len(matches)}")
                except ValueError:
                    click.echo("❌ Please enter a valid number")

            # Open YouTube at selected timestamp
            opener = VideoOpener()
            if opener.open_youtube(video_id, time_seconds=selected_match['timestamp_seconds']):
                click.echo(f"✓ Opened YouTube video at {selected_match['timestamp_str']}")
            else:
                click.echo("❌ Failed to open YouTube video", err=True)
                sys.exit(1)
            return

        # Regular YouTube opening (without search)
        if youtube:
            opener = VideoOpener()
            if opener.open_youtube(video_id, time_str=time):
                if time:
                    click.echo(f"✓ Opening YouTube video {video_id} at {time}")
                else:
                    click.echo(f"✓ Opening YouTube video {video_id}")
            else:
                click.echo(f"❌ Failed to open YouTube video {video_id}", err=True)
                sys.exit(1)
            return

    # Handle file opening (transcript/metadata/summary in Code or Finder)
    output_manager = OutputManager(output_dir)

    # Get file paths
    file_paths = output_manager.get_file_paths(video_id)
    existing_files = output_manager.check_file_exists(video_id)

    # Determine which file to open
    if summary:
        # Open AI-generated summary
        from src.core.ai_processed_manager import AIProcessedManager
        ai_manager = AIProcessedManager(Path(output_dir))

        if not ai_manager.check_summary_exists(video_id, length):
            click.echo(f"❌ {length.title()} summary not found for {video_id}", err=True)
            click.echo("\nGenerate it first:", err=True)
            click.echo(f"  ytc ai {video_id} --summarize --length {length}", err=True)
            sys.exit(1)

        file_to_open = ai_manager.get_summary_path(video_id, length)
        file_type = f"{length.title()} Summary"

        # If --finder, open the AI processed directory instead
        if finder:
            video_ai_dir = ai_manager.get_video_ai_directory(video_id)
            if video_ai_dir:
                file_to_open = video_ai_dir
                file_type = "AI Processed Directory"
    elif open_books or open_tools or open_key_points:
        # Open AI-extracted content
        from src.core.ai_processed_manager import AIProcessedManager
        ai_manager = AIProcessedManager(Path(output_dir))

        # Determine extraction type
        if open_books:
            extraction_type = 'books'
            display_name = "Books"
        elif open_tools:
            extraction_type = 'tools'
            display_name = "Tools"
        else:
            extraction_type = 'key_points'
            display_name = "Key Points"

        if not ai_manager.check_extraction_exists(video_id, extraction_type):
            click.echo(f"❌ {display_name} extraction not found for {video_id}", err=True)
            click.echo("\nExtract it first:", err=True)
            flag = extraction_type.replace('_', '-')
            click.echo(f"  ytc extract {video_id} --{flag}", err=True)
            sys.exit(1)

        # Open markdown version by default (human-readable)
        file_to_open = ai_manager.get_extraction_path(video_id, extraction_type, 'markdown')
        file_type = f"{display_name} Extraction"

        # If --finder, open the AI processed directory instead
        if finder:
            video_ai_dir = ai_manager.get_video_ai_directory(video_id)
            if video_ai_dir:
                file_to_open = video_ai_dir
                file_type = "AI Processed Directory"
    elif meta:
        if not existing_files['metadata']:
            click.echo(f"❌ Metadata file not found for {video_id}")
            sys.exit(1)
        file_to_open = file_paths['metadata']
        file_type = "Metadata"
    else:
        if not existing_files['transcript']:
            click.echo(f"❌ Transcript file not found for {video_id}")
            sys.exit(1)
        file_to_open = file_paths['transcript']
        file_type = "Transcript"

    # Open in Finder/file manager or VS Code (default: VS Code)
    if finder:
        import subprocess
        import platform
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(['open', '-R', file_to_open], check=True)
                click.echo(f"✓ Opening {file_type} in Finder: {file_to_open}")
            elif system == "Linux":
                # Linux: open containing folder (can't highlight specific file)
                folder = str(Path(file_to_open).parent)
                subprocess.run(['xdg-open', folder], check=True)
                click.echo(f"✓ Opening folder in file manager: {folder}")
            else:
                click.echo(f"❌ File manager not supported on {system}", err=True)
                sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Failed to open in file manager: {e}", err=True)
            sys.exit(1)
    else:
        # Default behavior: open in VS Code (--code flag or no flag)
        import subprocess
        try:
            subprocess.run(['code', file_to_open], check=True)
            click.echo(f"✓ Opening {file_type} in Code: {file_to_open}")
        except FileNotFoundError:
            click.echo(f"❌ Code editor not found. Please open manually: {file_to_open}", err=True)
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Failed to open editor: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.argument('keyword')
@click.option('--context', type=int, default=0, help='Lines of context around matches')
@click.option('--count', is_flag=True, help='Only show match counts')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.pass_context
def search(ctx, keyword, context, count, output_json):
    """Search transcripts for keyword."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("search"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    metadata_dir = Path(output_dir) / 'metadata'

    # Load library
    library = LibraryManager(metadata_dir)

    # Search
    results = library.search_transcripts(keyword, context_lines=context)

    if not results:
        click.echo(f"No matches found for '{keyword}'")
        return

    if output_json:
        import json
        click.echo(json.dumps(results, indent=2))
    elif count:
        click.echo(f"\n🔍 Matches for '{keyword}':\n")
        for video_id, result in results.items():
            match_count = result.get('match_count', 0)
            title = result.get('title', 'Unknown')
            click.echo(f"  {title}: {match_count} match{'es' if match_count != 1 else ''}")
        click.echo(f"\nTotal: {sum(r.get('match_count', 0) for r in results.values())} matches")
    else:
        output = Formatter.format_search_results(results)
        click.echo(output)


@cli.command()
@click.pass_context
def stats(ctx):
    """Show library statistics."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("stats"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    metadata_dir = Path(output_dir) / 'metadata'

    # Load library
    library = LibraryManager(metadata_dir)
    stats_data = library.get_statistics()

    # Format and display
    output = Formatter.format_statistics(stats_data)
    click.echo(output)


@cli.command()
@click.argument('video_id', required=False)
@click.option('--last', is_flag=True, help='Delete the most recently fetched video')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete(ctx, video_id: str, last: bool, force: bool):
    """Delete a video from your library.

    VIDEO_ID: YouTube video ID or URL (or use --last for most recent)
    """
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("delete"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    output_manager = OutputManager(output_dir)
    metadata_dir = Path(output_dir) / 'metadata'

    # Handle --last flag to get most recent video
    if last:
        from src.core.library_manager import LibraryManager
        library = LibraryManager(metadata_dir)
        videos = library.get_all_videos()

        if not videos:
            click.echo("❌ No videos found in library", err=True)
            sys.exit(1)

        # Sort by date (most recent first) and get the first one
        sorted_videos = library.sort_by(videos, 'date', reverse=False)
        most_recent = sorted_videos[0]
        video_id = most_recent.get('video_id')

        if not video_id:
            click.echo("❌ Could not determine video ID from most recent video", err=True)
            sys.exit(1)

        click.echo(f"📺 Most recent: {most_recent.get('title', 'Unknown')}")
        click.echo(f"   Video ID: {video_id}\n")

    # Validate video_id is provided or determined
    if not video_id:
        click.echo("❌ Error: VIDEO_ID is required (or use --last flag)", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc delete VIDEO_ID         # Delete specific video", err=True)
        click.echo("  ytc delete --last           # Delete most recent video", err=True)
        sys.exit(1)

    # Parse input - extract video ID if URL provided
    from src.utils.url_parser import YouTubeURLParser
    extracted_id = YouTubeURLParser.extract_video_id(video_id)
    if not extracted_id:
        click.echo(f"❌ Invalid YouTube URL or video ID: {video_id}", err=True)
        sys.exit(1)

    video_id = extracted_id

    # Check if files exist
    existing_files = output_manager.check_file_exists(video_id)
    file_paths = output_manager.get_file_paths(video_id)

    if not any(existing_files.values()):
        click.echo(f"❌ No files found for video: {video_id}", err=True)
        sys.exit(1)

    # Show what will be deleted
    click.echo(f"\n🗑️  Video to Delete: {video_id}")
    click.echo("=" * 50)

    # Load metadata to show title
    if existing_files['metadata']:
        import json
        with builtins.open(file_paths['metadata'], 'r') as f:
            metadata = json.load(f)
        title = metadata.get('title', 'Unknown')
        channel = metadata.get('channel', 'Unknown')
        click.echo(f"   Title: {title}")
        click.echo(f"   Channel: {channel}")

    click.echo("\n📁 Files to Delete:")
    for file_type, exists in existing_files.items():
        if exists:
            path = file_paths[file_type]
            size_mb = path.stat().st_size / (1024 * 1024)
            click.echo(f"   • {file_type}: {path.name} ({size_mb:.2f} MB)")

    # Confirm unless --force flag
    if not force:
        click.echo("\n⚠️  This cannot be undone!")
        if not click.confirm("Are you sure you want to delete these files?"):
            click.echo("❌ Deletion cancelled")
            return

    # Delete files
    try:
        results = output_manager.delete_video_files(video_id)
        deleted_count = sum(1 for v in results.values() if v)

        # Remove from library
        library = LibraryManager(metadata_dir)
        library.delete_video(video_id)

        click.echo(f"\n✓ Successfully deleted {deleted_count} file(s)")
        click.echo("✓ Removed from library")

        # Log the deletion
        log_dir = output_dir / 'logs'
        lib_logger = LibraryLogger(log_dir)
        lib_logger.log_delete(
            video_id=video_id,
            title=title,
            channel=channel
        )

    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during deletion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--action', type=click.Choice(['all', 'fetch', 'delete']), default='all', help='Filter by action type')
@click.option('--limit', type=int, default=20, help='Number of entries to show')
@click.pass_context
def history(ctx, action: str, limit: int):
    """Show library change history (fetches and deletions)."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("history"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()
    log_dir = Path(output_dir) / 'logs'

    lib_logger = LibraryLogger(log_dir)

    if action == 'all':
        entries = lib_logger.get_recent_changes(limit=limit)
    else:
        entries = lib_logger.get_changes_by_action(action)[-limit:]
        # Reverse to show most recent first
        entries = entries[::-1]

    if not entries:
        if action == 'all':
            click.echo("📭 No entries in history")
        else:
            click.echo(f"📭 No {action} entries in history")
        return

    click.echo(f"\n📋 Library Change History ({action})")
    click.echo("=" * 80)

    for i, entry in enumerate(entries, 1):
        action_icon = "⬇️ " if entry['action'] == 'fetch' else "🗑️ "
        timestamp = entry['timestamp'].split('T')[0] + " " + entry['timestamp'].split('T')[1].split('.')[0]

        click.echo(f"\n{i}. {action_icon} {entry['action'].upper()} - {timestamp}")
        click.echo(f"   Video ID: {entry['video_id']}")
        click.echo(f"   Title: {entry['title']}")
        click.echo(f"   Channel: {entry['channel']}")
        if entry['action'] == 'fetch':
            click.echo(f"   URL: {entry['url']}")

    click.echo("\n" + "=" * 80)
    click.echo(f"Showing {len(entries)} of {len(entries)} entries")


@cli.command(name='help')
@click.argument('command', required=False)
@click.pass_context
def help_cmd(ctx, command):
    """Show help for commands."""
    config = ctx.obj['config']
    version = config.get_version()

    # Suppress logging output for help command (avoid clutter)
    logging.getLogger().setLevel(logging.CRITICAL)

    # Build colored header with box frame
    # Box frame is 72 chars total: ╔ (1) + content (70) + ╗ (1)
    # Dark gray box frame (exactly 72 chars wide)
    top_line = click.style("╔" + "═" * 70 + "╗", fg='black', bold=True)
    bottom_line = click.style("╚" + "═" * 70 + "╝", fg='black', bold=True)

    # Build colored text INSIDE the box
    yt_colored = click.style("YouTube", fg='red', bold=True)
    transcript_colored = click.style("Transcript", fg='green', bold=True)
    curator_colored = click.style("Curator", fg='blue', bold=True)
    version_colored = click.style(f"v{version}", fg='yellow', bold=True)
    ref_colored = click.style("Quick Reference", fg='cyan', bold=True)

    # Create header line with colors inside (70 chars of content + 2 borders = 72 total)
    header_text = yt_colored + " " + transcript_colored + " " + curator_colored + " - " + version_colored + " - " + ref_colored
    # Calculate padding (account for colored text length = visible text length)
    visible_text = f"YouTube Transcript Curator v{version} - Quick Reference"
    padding_needed = 70 - len(visible_text)
    spaces_before = padding_needed // 2
    spaces_after = padding_needed - spaces_before

    colored_header_line = click.style("║", fg='black', bold=True)
    colored_header_line += " " * max(0, spaces_before - 1)
    colored_header_line += header_text
    colored_header_line += " " * max(0, spaces_after - 1)
    colored_header_line += click.style("║", fg='black', bold=True)

    # Build help text with bold section headers
    core_header = click.style("CORE COMMANDS", bold=True)
    library_header = click.style("LIBRARY MANAGEMENT", bold=True)
    ai_header = click.style("AI COMMANDS", bold=True)
    detailed_header = click.style("DETAILED HELP", bold=True)
    tips_header = click.style("TIPS", bold=True)
    keyboard_header = click.style("KEYBOARD SHORTCUTS", bold=True)

    help_text = top_line + "\n" + colored_header_line + "\n" + bottom_line + f"""

{core_header}
─────────────────────────────────────────────────────────────────────────────
  ytc fetch <URL>             Extract transcript and metadata from YouTube video
  ytc info <ID_OR_URL>        Show information about a transcribed video

{library_header}
─────────────────────────────────────────────────────────────────────────────
  ytc list                    List all stored video transcripts (compact format)
  ytc open <VIDEO_ID>         Open transcript, metadata, or YouTube video
  ytc search <KEYWORD>        Search all transcripts
  ytc stats                   Show library statistics
  ytc delete <VIDEO_ID>       Delete a video transcript from your library
  ytc history                 Show library change history (fetches/deletes)

{ai_header}
─────────────────────────────────────────────────────────────────────────────
  ytc ai <VIDEO_ID>           AI-powered transcript analysis with Claude
  ytc extract <VIDEO_ID>      Extract books, tools, key points with AI

{detailed_header}
─────────────────────────────────────────────────────────────────────────────

► ytc fetch <URL>
  Extract transcript and metadata from a YouTube video.

  Usage:
    ytc fetch "https://youtu.be/VIDEO_ID"
    ytc fetch "https://www.youtube.com/watch?v=VIDEO_ID&t=123s"
    ytc fetch VIDEO_ID

  Options:
    --overwrite         Overwrite existing files
    --no-timestamps     Exclude timestamps from transcript
    --output-dir PATH   Custom output directory

  Example:
    ytc fetch "https://youtu.be/dQw4w9WgXcQ" --overwrite

► ytc info <ID_OR_URL>
  Show details about a transcribed video.

  Usage:
    ytc info VIDEO_ID
    ytc info "https://youtu.be/VIDEO_ID"
    ytc info "https://www.youtube.com/watch?v=VIDEO_ID"

  Note: Always quote URLs with special characters (?, &, etc.)

► ytc list [OPTIONS]
  List all transcribed videos with filtering and sorting.

  Options:
    --format CHOICE        Output format: compact (default), full, ids, json
    --type TYPE            Filter by type: regular, livestream_recording
    --channel NAME         Filter by channel (case-insensitive)
    --sort FIELD           Sort by: date (default), title, channel, duration
    --reverse              Reverse sort order
    --limit N              Show only first N results

  Examples:
    ytc list
    ytc list --type regular --sort title
    ytc list --channel "VS Code" --format full
    ytc list --limit 5

► ytc open <VIDEO_ID> [OPTIONS]
  Open transcript, metadata, or YouTube video.

  File Opening (default: transcript in VS Code):
    --meta               Open metadata JSON instead
    --finder             Open in Finder instead of Code

  YouTube Opening:
    --youtube            Open video in YouTube/Chrome browser
    --time FORMAT        Jump to timestamp (MM:SS, HH:MM:SS, seconds, 1m30s)
    --search KEYWORD     Fuzzy search for keyword and jump to first match

  Examples:
    ytc open COKyFP_VNAs                          # Open transcript in Code
    ytc open COKyFP_VNAs --meta                   # Open metadata in Code
    ytc open COKyFP_VNAs --finder                 # Open transcript in Finder
    ytc open IdPtTBbYOtw --youtube                # Open in YouTube
    ytc open IdPtTBbYOtw --youtube --time 5:45    # Jump to 5:45
    ytc open COKyFP_VNAs --youtube --search "robotics"  # Fuzzy search

► ytc search <KEYWORD> [OPTIONS]
  Search transcripts for keyword.

  Options:
    --context N          Show N lines before/after matches
    --count              Show only match counts per video
    --json               Output as JSON

  Examples:
    ytc search "python"
    ytc search "tutorial" --context 2
    ytc search "AI" --count

► ytc stats
  Show library overview: total videos, duration, breakdown by type and channel.

  Example:
    ytc stats

► ytc delete <VIDEO_ID>
  Delete a video from your library (with confirmation).

  Options:
    --force              Skip confirmation prompt

  Examples:
    ytc delete VIDEO_ID
    ytc delete "https://youtu.be/VIDEO_ID"
    ytc delete VIDEO_ID --force

{tips_header}
─────────────────────────────────────────────────────────────────────────────
• Always quote URLs: ytc fetch "https://youtu.be/..."
• Use --help on any command for more details: ytc fetch --help
• Press Tab for command completion (after setup)
• Search tips: Use quotes for phrases: ytc search "machine learning"

{keyboard_header}
─────────────────────────────────────────────────────────────────────────────
• ytc-cd         Jump to project directory
• ytc-output     Open data/output in Finder
"""

    if command:
        # Show help for specific command
        command = command.lower().replace('-', '_')
        commands_help = {
            'fetch': """
► ytc fetch <URL>
  Extract transcript and metadata from a YouTube video.

  Usage:
    ytc fetch "https://youtu.be/VIDEO_ID"
    ytc fetch "https://www.youtube.com/watch?v=VIDEO_ID&t=123s"
    ytc fetch VIDEO_ID

  Options:
    --overwrite         Overwrite existing files
    --no-timestamps     Exclude timestamps from transcript
    --output-dir PATH   Custom output directory

  Example:
    ytc fetch "https://youtu.be/dQw4w9WgXcQ" --overwrite
""",
            'info': """
► ytc info <ID_OR_URL>
  Show details about a transcribed video.

  Usage:
    ytc info VIDEO_ID
    ytc info "https://youtu.be/VIDEO_ID"
    ytc info "https://www.youtube.com/watch?v=VIDEO_ID"

  Shows:
    - Which files exist (metadata, transcript)
    - Video title, channel, duration, URL, type
    - File locations and quick access commands

  Note: Always quote URLs with special characters (?, &, etc.)
""",
            'list': """
► ytc list [OPTIONS]
  List all transcribed videos with filtering and sorting.

  Output Formats:
    --format CHOICE        Output format: compact (default), full, ids, json
    --align                Display with vertically aligned columns (same colors as compact)

  Filtering & Sorting:
    --type TYPE            Filter by type (fuzzy matching supported):
                           regular, livestream, livestream_recording
                           Fuzzy shortcuts: reg, live, rec, ls, recording
    --channel NAME         Filter by channel (case-insensitive)
    --sort FIELD           Sort by: date (default), title, channel, duration, views, published
    --reverse              Reverse sort order
    --limit N              Show only first N results

  Fuzzy Type Matching:
    Type matching is forgiving! Use shortcuts instead of exact names:
    ytc list --type reg       # matches: regular
    ytc list --type live      # matches: livestream
    ytc list --type rec       # matches: livestream_recording

  Tab Completion:
    ytc list --type <TAB>     # Shows all available type shortcuts

  Examples:
    ytc list                                   # All videos, compact format
    ytc list --align                           # All videos with aligned columns
    ytc list --align --limit 10 --sort views   # Top 10 by views, aligned
    ytc list --type regular                    # Only regular videos
    ytc list --type live                       # All livestream types
    ytc list --sort title                      # Sort alphabetically
    ytc list --channel "VS Code"               # Filter by channel
    ytc list --limit 5 --format full           # Top 5 with details
    ytc list --align --type regular --sort duration  # Filtered, sorted, aligned
""",
            'open': """
► ytc open <VIDEO_ID> [OPTIONS]
  Open transcript, metadata, or YouTube video.

  File Opening (default: transcript in VS Code):
    --meta               Open metadata JSON instead
    --finder             Open in Finder instead of Code

  YouTube Opening:
    --youtube            Open video in YouTube/Chrome browser
    --time FORMAT        Jump to timestamp (MM:SS, HH:MM:SS, seconds, 1m30s)
    --search KEYWORD     Fuzzy search for keyword and jump to first match

  Examples:
    ytc open COKyFP_VNAs                          # Open transcript in Code
    ytc open COKyFP_VNAs --meta                   # Open metadata in Code
    ytc open COKyFP_VNAs --finder                 # Open transcript in Finder
    ytc open IdPtTBbYOtw --youtube                # Open in YouTube
    ytc open IdPtTBbYOtw --youtube --time 5:45    # Jump to 5:45
    ytc open COKyFP_VNAs --youtube --search "robotics"  # Fuzzy search
""",
            'search': """
► ytc search <KEYWORD> [OPTIONS]
  Search transcripts for keyword.

  Options:
    --context N          Show N lines before/after matches
    --count              Show only match counts per video
    --json               Output as JSON

  Examples:
    ytc search "python"                  # Search for python
    ytc search "neural network" --count  # Count matches only
    ytc search "tutorial" --context 2    # Show context around matches
    ytc search "AI" --json               # Output as JSON
""",
            'stats': """
► ytc stats
  Show library overview: total videos, duration, breakdown by type and channel.

  Displays:
    - Total videos and total duration
    - Average video duration
    - Breakdown by type (Regular, Livestream Recording)
    - Top 10 channels by video count

  Example:
    ytc stats
""",
            'delete': """
► ytc delete <VIDEO_ID> [OPTIONS]
  Delete a video from your library.

  Supports:
    - Video ID (11 characters): yt delete VIDEO_ID
    - YouTube URL: yt delete "https://youtu.be/VIDEO_ID"
    - Full URL: yt delete "https://www.youtube.com/watch?v=VIDEO_ID"

  Options:
    --force              Skip confirmation prompt (use with caution!)

  What Gets Deleted:
    - Metadata JSON file
    - Transcript text file
    - Formatted file (if exists)

  Examples:
    ytc delete VIDEO_ID                    # Shows what will be deleted, asks for confirmation
    ytc delete "https://youtu.be/VIDEO_ID" # Accepts URL format
    ytc delete VIDEO_ID --force            # Skip confirmation (caution!)

  Warning:
    This action cannot be undone. The deleted files are permanently removed.
""",
            'history': """
► ytc history [OPTIONS]
  Show library change history (all fetches and deletions).

  Options:
    --action CHOICE    Filter by action: all (default), fetch, or delete
    --limit N          Show last N entries (default: 20)

  Examples:
    ytc history                    # Show all recent changes (last 20)
    ytc history --action fetch     # Show only fetches
    ytc history --action delete    # Show only deletions
    ytc history --limit 50         # Show last 50 entries
    ytc history --action delete --limit 10  # Show last 10 deletions

  Use Case: Recover accidentally deleted videos by checking the log!
""",
            'ai': """
► ytc ai <VIDEO_ID> [OPTIONS]
  Use Claude AI to analyze or summarize video transcripts.

  Options:
    --prompt TEXT        Custom prompt for AI analysis
    --summarize          Generate a summary (uses default summary prompt)
    --length CHOICE      Summary length: short, medium (default), long
    --last               Use the most recently fetched video

  Examples:
    ytc ai VIDEO_ID --summarize                    # Generate summary
    ytc ai VIDEO_ID --summarize --length short     # Short summary
    ytc ai --last --summarize                      # Summarize most recent
    ytc ai VIDEO_ID --prompt "What are the main ideas?"  # Custom question
""",
            'extract': """
► ytc extract <VIDEO_ID> [OPTIONS]
  Extract structured information from transcripts using AI.

  Options:
    --books         Extract books and papers mentioned
    --tools         Extract tools and software mentioned
    --key-points    Extract key insights and takeaways
    --last          Use the most recently fetched video
    --overwrite     Force re-extraction if exists

  Output: Saves both JSON and Markdown files for each extraction type.

  Examples:
    ytc extract VIDEO_ID --books              # Extract books mentioned
    ytc extract VIDEO_ID --tools              # Extract tools mentioned
    ytc extract VIDEO_ID --key-points         # Extract key insights
    ytc extract VIDEO_ID --books --tools      # Multiple extractions
    ytc extract --last --key-points           # Extract from most recent

  View extracted data:
    ytc open VIDEO_ID --books                 # Open books.md
    ytc open VIDEO_ID --tools                 # Open tools.md
    ytc open VIDEO_ID --key-points            # Open key_points.md
""",
            'config': """
► ytc config <COMMAND>
  Manage YTC configuration settings.

  Commands:
    show               Show all configuration settings
    get KEY            Get value of specific key
    set KEY VALUE      Set configuration value
    edit               Open config file in editor
    path               Show config file location
    reset              Reset to default configuration
    init               Initialize new config file
    where              Show config directory
    move NEW_PATH      Move config to new location

  Examples:
    ytc config show                                # View all settings
    ytc config get output.directory                # Get specific value
    ytc config set logging.level INFO              # Change log level
    ytc config edit                                # Edit in VS Code
    ytc config path                                # See where config lives
""",
        }

        if command in commands_help:
            click.echo(commands_help[command])
        else:
            click.echo(f"❌ Unknown command: {command}\n")
            click.echo("Available commands: fetch, info, list, open, search, stats, delete, history, ai, config")
    else:
        # Use pager for full help (allows scrolling with less/more)
        click.echo_via_pager(help_text)


@cli.command()
@click.argument('video_id', required=False)
@click.option('--prompt', help='Question or instruction for AI analysis')
@click.option('--summarize', is_flag=True, help='Generate a summary of the video')
@click.option('--length', type=click.Choice(['short', 'medium', 'long'], case_sensitive=False), default='medium', help='Summary length (use with --summarize)')
@click.option('--last', is_flag=True, help='Analyze the most recently fetched video')
@click.option('--overwrite', is_flag=True, help='Regenerate summary even if it exists')
@click.pass_context
def ai(ctx, video_id, prompt, summarize, length, last, overwrite):
    """AI-powered transcript analysis using Claude."""
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("ai"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()

    # Handle --last flag to get most recent video
    if last:
        from src.core.library_manager import LibraryManager
        metadata_dir = Path(output_dir) / 'metadata'
        library = LibraryManager(metadata_dir)
        videos = library.get_all_videos()

        if not videos:
            click.echo("❌ No videos found in library", err=True)
            sys.exit(1)

        # Sort by date (most recent first) and get the first one
        sorted_videos = library.sort_by(videos, 'date', reverse=False)
        most_recent = sorted_videos[0]
        video_id = most_recent.get('video_id')

        if not video_id:
            click.echo("❌ Could not determine video ID from most recent video", err=True)
            sys.exit(1)

        click.echo(f"📺 Most recent: {most_recent.get('title', 'Unknown')}")
        click.echo(f"   Video ID: {video_id}\n")

    # Validate video_id is provided or determined
    if not video_id:
        click.echo("❌ Error: VIDEO_ID is required (or use --last flag)", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc ai VIDEO_ID --prompt \"Your question\"", err=True)
        click.echo("  ytc ai --last --prompt \"Your question\"", err=True)
        sys.exit(1)

    # Build prompt based on flags
    if summarize and prompt:
        click.echo("⚠️  Warning: Both --summarize and --prompt provided. Using --summarize.", err=True)
        prompt = None

    if summarize:
        # Build summarization prompt based on length
        if length == 'short':
            prompt = (
                "Provide a very concise summary of this video in 1-2 sentences. "
                "Focus on the main topic and key takeaway."
            )
        elif length == 'long':
            prompt = (
                "Provide a detailed summary of this video with the following structure:\n"
                "1. Introduction: Main topic and context\n"
                "2. Key sections: Break down each major section with timestamps if mentioned\n"
                "3. Important points: List all significant concepts, techniques, or insights\n"
                "4. Conclusion: Final takeaways and recommendations\n\n"
                "Be thorough and include specific details from the transcript."
            )
        else:  # medium (default)
            prompt = (
                "Provide a summary of this video including:\n"
                "1. Main topic\n"
                "2. Key points (5-10 bullet points)\n"
                "3. Conclusion or main takeaway\n\n"
                "Be concise but capture the essential content."
            )

    # Validate prompt is provided
    if not prompt:
        click.echo("❌ Error: Either --prompt or --summarize is required", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc ai VIDEO_ID --prompt \"List all books mentioned\"", err=True)
        click.echo("  ytc ai VIDEO_ID --summarize", err=True)
        click.echo("  ytc ai VIDEO_ID --summarize --length short", err=True)
        sys.exit(1)

    # Check if transcript exists
    output_manager = OutputManager(Path(output_dir))
    file_paths = output_manager.get_file_paths(video_id)
    existing_files = output_manager.check_file_exists(video_id)

    if not existing_files['transcript']:
        click.echo(f"❌ Transcript file not found for {video_id}", err=True)
        click.echo("\nFetch it first:", err=True)
        click.echo("  ytc fetch VIDEO_URL", err=True)
        sys.exit(1)

    transcript_file = file_paths['transcript']

    # Load transcript
    try:
        with builtins.open(str(transcript_file), 'r', encoding='utf-8') as f:
            transcript = f.read()

        if not transcript.strip():
            click.echo(f"❌ Transcript file is empty: {transcript_file}", err=True)
            sys.exit(1)

        click.echo(f"📄 Loaded transcript ({len(transcript)} characters)\n")

    except Exception as e:
        click.echo(f"❌ Error loading transcript: {e}", err=True)
        sys.exit(1)

    # Check if summary already exists (for --summarize only)
    from src.core.ai_processed_manager import AIProcessedManager
    ai_manager = AIProcessedManager(Path(output_dir))

    if summarize and not overwrite:
        if ai_manager.check_summary_exists(video_id, length):
            # Load and display existing summary
            existing_summary = ai_manager.load_summary(video_id, length)
            summary_path = ai_manager.get_summary_path(video_id, length)

            click.echo(f"ℹ️  Summary already exists: {_short_path(summary_path)}")
            click.echo("ℹ️  Use --overwrite to regenerate\n")

            # Display existing content
            click.echo("─" * 50)
            click.echo(existing_summary)
            click.echo("─" * 50)
            return

    # Initialize AI provider (local Claude by default)
    from src.ai.local_provider import LocalClaudeProvider

    try:
        provider = LocalClaudeProvider()

        # Validate Claude is available
        if not provider.validate_availability():
            click.echo("❌ Claude CLI not found in PATH", err=True)
            click.echo("\nInstall it from: https://docs.anthropic.com/en/docs/cli", err=True)
            click.echo("Or run: brew install anthropic-ai/tap/claude", err=True)
            sys.exit(1)

        click.echo(f"🤖 Analyzing with Claude ({provider.get_model_name()})...\n")

        # Send to Claude
        response = provider.analyze(transcript, prompt)

        # Display response
        click.echo("─" * 50)
        click.echo(response)
        click.echo("─" * 50)

        # Save summary if --summarize was used
        if summarize:
            try:
                saved_path = ai_manager.save_summary(
                    video_id=video_id,
                    summary_text=response,
                    length=length,
                    model=provider.get_model_name(),
                    overwrite=overwrite
                )
                click.echo(f"\n✓ Summary saved to: {_short_path(saved_path)}")

                # Update metadata with AI processed info
                file_paths = output_manager.get_file_paths(video_id)
                metadata_path = file_paths['metadata']
                if metadata_path.exists():
                    try:
                        import json
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)

                        # Add ai_processed field if it doesn't exist
                        if 'ai_processed' not in metadata:
                            metadata['ai_processed'] = {}

                        # Add summary metadata
                        summary_key = f"summary_{length}"
                        metadata['ai_processed'][summary_key] = ai_manager.get_summary_metadata(
                            video_id, length, provider.get_model_name()
                        )

                        # Save updated metadata
                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)

                        logger.debug(f"Updated metadata with AI processed info: {metadata_path}")

                    except Exception as e:
                        import traceback
                        logger.warning(f"Failed to update metadata: {e}")
                        logger.debug(f"Traceback: {traceback.format_exc()}")
                        # Don't fail the command if metadata update fails

            except Exception as e:
                click.echo(f"\n⚠️  Warning: Failed to save summary: {e}", err=True)
                # Don't fail the command if save fails

        else:
            click.echo("\n✓ Analysis complete")

    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ AI analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('video_id', required=False)
@click.option('--books', is_flag=True, help='Extract books and papers mentioned')
@click.option('--tools', is_flag=True, help='Extract tools and software mentioned')
@click.option('--key-points', 'key_points', is_flag=True, help='Extract key insights and takeaways')
@click.option('--last', is_flag=True, help='Extract from most recently fetched video')
@click.option('--overwrite', is_flag=True, help='Force re-extraction if exists')
@click.pass_context
def extract(ctx, video_id, books, tools, key_points, last, overwrite):
    """Extract structured information from video transcripts using AI.

    Examples:
        ytc extract VIDEO_ID --books
        ytc extract VIDEO_ID --tools
        ytc extract VIDEO_ID --key-points
        ytc extract --last --books --tools
    """
    config = ctx.obj['config']
    click.echo(Colors.get_command_title("extract"))
    click.echo("=" * 50)
    output_dir = config.get_output_dir()

    # Handle --last flag to get most recent video
    if last:
        from src.core.library_manager import LibraryManager
        metadata_dir = Path(output_dir) / 'metadata'
        library = LibraryManager(metadata_dir)
        videos = library.get_all_videos()

        if not videos:
            click.echo("❌ No videos found in library", err=True)
            sys.exit(1)

        sorted_videos = library.sort_by(videos, 'date', reverse=False)
        most_recent = sorted_videos[0]
        video_id = most_recent.get('video_id')

        if not video_id:
            click.echo("❌ Could not determine video ID from most recent video", err=True)
            sys.exit(1)

        click.echo(f"📺 Most recent: {most_recent.get('title', 'Unknown')}")
        click.echo(f"   Video ID: {video_id}\n")

    # Validate video_id is provided or determined
    if not video_id:
        click.echo("❌ Error: VIDEO_ID is required (or use --last flag)", err=True)
        click.echo("\nUsage:", err=True)
        click.echo("  ytc extract VIDEO_ID --books", err=True)
        click.echo("  ytc extract --last --tools", err=True)
        sys.exit(1)

    # Validate at least one extraction type is specified
    extraction_types = []
    if books:
        extraction_types.append('books')
    if tools:
        extraction_types.append('tools')
    if key_points:
        extraction_types.append('key_points')

    if not extraction_types:
        click.echo("❌ Error: At least one extraction type is required", err=True)
        click.echo("\nOptions:", err=True)
        click.echo("  --books       Extract books and papers mentioned", err=True)
        click.echo("  --tools       Extract tools and software mentioned", err=True)
        click.echo("  --key-points  Extract key insights and takeaways", err=True)
        sys.exit(1)

    # Check if transcript exists
    output_manager = OutputManager(Path(output_dir))
    file_paths = output_manager.get_file_paths(video_id)
    existing_files = output_manager.check_file_exists(video_id)

    if not existing_files['transcript']:
        click.echo(f"❌ Transcript file not found for {video_id}", err=True)
        click.echo("\nFetch it first:", err=True)
        click.echo("  ytc fetch VIDEO_URL", err=True)
        sys.exit(1)

    transcript_file = file_paths['transcript']

    # Load transcript
    try:
        with builtins.open(str(transcript_file), 'r', encoding='utf-8') as f:
            transcript = f.read()

        if not transcript.strip():
            click.echo(f"❌ Transcript file is empty: {transcript_file}", err=True)
            sys.exit(1)

        click.echo(f"📄 Loaded transcript ({len(transcript)} characters)\n")

    except Exception as e:
        click.echo(f"❌ Error loading transcript: {e}", err=True)
        sys.exit(1)

    # Get video title for metadata
    video_title = ""
    metadata_path = file_paths['metadata']
    if metadata_path.exists():
        try:
            import json as json_module
            with open(metadata_path, 'r', encoding='utf-8') as f:
                video_metadata = json_module.load(f)
            video_title = video_metadata.get('title', '')
        except Exception:
            pass

    # Initialize managers
    from src.core.ai_processed_manager import AIProcessedManager
    from src.ai.local_provider import LocalClaudeProvider
    from src.ai.prompts import (
        get_extraction_prompt,
        parse_claude_json_response,
        validate_extraction_items,
        get_extraction_type_display_name,
        get_extraction_type_emoji
    )

    ai_manager = AIProcessedManager(Path(output_dir))

    # Initialize Claude provider
    try:
        provider = LocalClaudeProvider()

        if not provider.validate_availability():
            click.echo("❌ Claude CLI not found in PATH", err=True)
            click.echo("\nInstall it from: https://docs.anthropic.com/en/docs/cli", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Failed to initialize Claude: {e}", err=True)
        sys.exit(1)

    # Process each extraction type
    for extraction_type in extraction_types:
        display_name = get_extraction_type_display_name(extraction_type)
        emoji = get_extraction_type_emoji(extraction_type)

        click.echo(f"{emoji} Extracting {display_name}...")

        # Check if extraction already exists
        if not overwrite and ai_manager.check_extraction_exists(video_id, extraction_type):
            existing_data = ai_manager.load_extraction(video_id, extraction_type, 'json')
            json_path = ai_manager.get_extraction_path(video_id, extraction_type, 'json')

            click.echo(f"ℹ️  {display_name} extraction already exists: {_short_path(json_path)}")
            click.echo("ℹ️  Use --overwrite to regenerate\n")

            # Display existing item count
            if existing_data and 'items' in existing_data:
                click.echo(f"   Found {len(existing_data['items'])} items\n")
            continue

        # Get extraction prompt
        prompt = get_extraction_prompt(extraction_type)

        click.echo(f"🤖 Analyzing with Claude ({provider.get_model_name()})...\n")

        try:
            # Send to Claude
            response = provider.analyze(transcript, prompt)

            # Parse JSON response
            try:
                items = parse_claude_json_response(response)
                items = validate_extraction_items(items, extraction_type)
            except ValueError as e:
                click.echo(f"⚠️  Warning: Failed to parse extraction: {e}", err=True)
                click.echo("Raw response (first 500 chars):", err=True)
                click.echo(response[:500], err=True)
                continue

            # Display results
            if not items:
                click.echo(f"   No {display_name.lower()} found in this video.\n")
            else:
                click.echo(f"   Found {len(items)} items:\n")

                # Display first few items
                for i, item in enumerate(items[:5], 1):
                    if extraction_type == 'books':
                        title = item.get('title', 'Unknown')
                        author = item.get('author', 'Unknown')
                        mentioned_at = item.get('mentioned_at', '?')
                        click.echo(f"   {i}. \"{title}\" by {author}")
                        click.echo(f"      Mentioned at: {mentioned_at}")
                    elif extraction_type == 'tools':
                        name = item.get('name', 'Unknown')
                        category = item.get('category', 'tool')
                        mentioned_at = item.get('mentioned_at', '?')
                        click.echo(f"   {i}. {name} ({category})")
                        click.echo(f"      Mentioned at: {mentioned_at}")
                    elif extraction_type == 'key_points':
                        point = item.get('point', '')
                        importance = item.get('importance', 'notable')
                        click.echo(f"   {i}. [{importance.upper()}] {point[:80]}...")

                if len(items) > 5:
                    click.echo(f"\n   ... and {len(items) - 5} more items")

                click.echo()

            # Save extraction
            try:
                json_path, md_path = ai_manager.save_extraction(
                    video_id=video_id,
                    extraction_type=extraction_type,
                    items=items,
                    model=provider.get_model_name(),
                    video_title=video_title,
                    overwrite=overwrite
                )

                click.echo("✓ Saved to:")
                click.echo(f"  - {_short_path(json_path)}")
                click.echo(f"  - {_short_path(md_path)}\n")

                # Update metadata
                if metadata_path.exists():
                    try:
                        import json as json_module
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json_module.load(f)

                        if 'ai_processed' not in metadata:
                            metadata['ai_processed'] = {}

                        metadata['ai_processed'][extraction_type] = ai_manager.get_extraction_metadata(
                            video_id, extraction_type, provider.get_model_name(), len(items)
                        )

                        with open(metadata_path, 'w', encoding='utf-8') as f:
                            json_module.dump(metadata, f, indent=2, ensure_ascii=False)

                        logger.debug(f"Updated metadata with {extraction_type} extraction")

                    except Exception as e:
                        logger.warning(f"Failed to update metadata: {e}")

            except Exception as e:
                click.echo(f"⚠️  Warning: Failed to save extraction: {e}", err=True)

        except Exception as e:
            click.echo(f"❌ Extraction failed for {display_name}: {e}", err=True)
            continue

    click.echo("✓ Extraction complete")


# Register the config command group
cli.add_command(config_cmd)


if __name__ == '__main__':
    cli(obj={})
