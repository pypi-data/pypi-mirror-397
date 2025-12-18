# Changelog

All notable changes to YouTube Transcript Curator are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2025-12-11

### Added

- **`ytc extract` command** - Extract structured information from transcripts using AI
  - `--books` - Extract books, papers, and articles mentioned
  - `--tools` - Extract tools, libraries, frameworks, and software
  - `--key-points` - Extract key insights grouped by importance (critical/important/notable)
  - `--last` - Extract from most recently fetched video
  - `--overwrite` - Force re-extraction if files exist
- **Dual-format output** - Saves both JSON (for querying) and Markdown (human-readable with clickable timestamps)
- **Open extracted data** - `ytc open --books`, `--tools`, `--key-points` flags
- **AI prompts module** - `src/ai/prompts.py` with extraction prompts and JSON parsing utilities
- **Tab completion** for `extract` command and new `open` flags
- **Help command updates** - Added "AI COMMANDS" section with `ytc ai` and `ytc extract`

### Fixed

- **Search path resolution** - Fixed bug where `ytc search` failed after repo was moved to different location
  - Added fallback path resolution in `library_manager.py`

### Documentation

- Created `docs/usage/EXTRACT.md` with full command documentation
- Updated `docs/usage/OVERVIEW.md` with extract command
- Updated `README.md` with AI extraction section
- Added lessons learned to `development/learnings.md`

---

## [0.8.0] - 2025-12-10

### Added

- **AI-processed data storage** - Auto-save summaries to `ai-processed/VIDEO_ID/summary_{length}.md`
- **Skip re-generation** - Existing summaries are displayed without re-calling Claude
- **`--overwrite` flag for `ytc ai`** - Force regeneration of summaries
- **Open summaries** - `ytc open VIDEO_ID --summary` opens saved summary
- **`AIProcessedManager` class** - Centralized management of AI-processed content
- **Metadata tracking** - `ai_processed` field in video metadata JSON

### New Files

- `src/core/ai_processed_manager.py` - Summary save/load/check methods
- `tests/unit/test_ai_processed_manager.py` - Full test coverage

---

## [0.7.0] - 2025-12-04

### Added

- **Test suite expansion** - 426 tests (up from 321), all passing
- **72% test coverage** - up from 55.64%
- **CONTRIBUTING.md** - Contribution guidelines for future public release
- **GitHub Actions CI/CD** - Automated testing on push/PR
- **Self-healing venv** - Automatic detection and fix for repo relocation

### Fixed

- All 14 previously failing tests now passing
- Mock patching in integration tests (correct import paths)
- Video ID validation in test fixtures (11 characters required)
- CLI command syntax in AI tests
- CLI output formatting improvements

### New Test Files

- `test_video_opener.py` - 39 tests, 87% coverage
- `test_formatter.py` - 42 tests, 96% coverage
- `test_config_loader.py` - 24 tests, 74% coverage

---

## [0.6.0] - 2025-11-20

### Added

- **`--code` flag for `ytc open`** - Explicitly open transcript in VS Code (default behavior, now with autocomplete)
- **`--last` flag for `ytc open`** - Open the most recently fetched video without specifying VIDEO_ID
- Improved error messages showing `--last` flag usage when VIDEO_ID is missing

### Changed

- Made VIDEO_ID argument optional for `ytc open` command to support `--last` flag
- Enhanced command help text with clearer default behavior descriptions

---

## [0.5.2] - 2025-11-16

### Added
- **`--align` flag for `ytc list`** - Display results in vertically aligned tabular format with proper column separators
- **`--search` flag for `ytc open`** - Fuzzy search within transcript and jump to matching timestamp on YouTube
- Tab completion support for new `--align` and `--search` flags
- Improved tab completion setup instructions with shell reload guidance

### Fixed
- Data folder location issue - transcripts, metadata, and logs now always save to project root regardless of working directory
- ANSI color code handling in column alignment - proper width calculation with invisible escape sequences
- Column alignment for mixed short/long title lengths
- Pipe character escaping in titles to prevent breaking aligned output columns
- Column width calculation for variable number of columns with injected sort fields

### Changed
- Updated shell completion scripts with new flag options
- Enhanced completion setup script with clearer reload instructions

### Documentation
- Updated LIST.md with `--align` flag documentation and examples
- Updated OPEN.md with `--search` flag documentation and usage examples
- Updated README with v0.5.2 version and feature descriptions

---

## [0.5.1] - 2025-11-15

### Fixed
- ASCII art formatting in README header

---

## [0.5.0] - 2025-11-14

### Added
- **Complete Phase 1-4 implementation**
- Fuzzy search in transcripts for YouTube video opening (Phase 4.1)
- Template-based output formatting with custom placeholders
- Tabular list output with `--align` flag
- Auto-injection of sort fields in compact format
- Tab completion for all commands
- Library change history tracking
- Full-text transcript search across library
- Video filtering by type and channel
- Multiple sort options (date, published, title, channel, duration, views)
- Enhanced CLI help system with command-specific documentation

### Dependencies
- youtube-transcript-api >= 1.2.3
- yt-dlp >= 2025.11.12
- Click 8.1.7
- PyYAML 6.0.1
- python-dotenv 1.0.0
- anthropic >= 0.39.0 (for Phase 2)
- pytest, pytest-cov, black, pylint, flake8 (dev dependencies)

---

## [0.1.0] - 2025-11-14

### Added
- **Complete Phase 1 MVP implementation**
- URL parser supporting multiple YouTube URL formats (standard, short, embed)
- Metadata fetcher using yt-dlp for comprehensive video information
- Transcript fetcher using youtube-transcript-api for caption extraction
- Output manager with organized file structure (metadata JSON, transcript text)
- CLI interface with `fetch` and `info` commands
- Configuration system with YAML and environment variable support
- Logging system with console and file output
- Setup script for automated environment configuration
- Comprehensive documentation in development/ folder

### Technical Details
- File naming: `metadata_[VIDEO_ID].json`, `youtube_[VIDEO_ID].txt`
- Timestamp format: `[MM:SS]` or `[HH:MM:SS]`
- Language preference support (defaults to English)
- Error handling for missing transcripts, network issues, rate limiting

### Dependencies
- youtube-transcript-api >= 1.2.3 (uses new instance-based API)
- yt-dlp >= 2025.11.12 (Python 3.14 compatible)
- Click 8.1.7
- PyYAML 6.0.1
- python-dotenv 1.0.0

### Notes
- Successfully tested with real YouTube videos (40+ minutes)
- Handles 1000+ transcript segments efficiently
- Standalone tool - no Docker or API keys required for Phase 1

---

## [0.0.1] - 2025-11-14

### Added
- Initial project structure and planning
- Development documentation (ideation, development plan, prerequisites)
- Project skeleton with folder structure
- Configuration templates
- README with usage instructions

---

**Legend:**
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements
