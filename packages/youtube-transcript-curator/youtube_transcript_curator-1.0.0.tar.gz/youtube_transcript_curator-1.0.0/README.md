```
 ██╗   ██╗  ████████╗    ██████╗
 ╚██╗ ██╔╝  ╚══██╔══╝   ██╔════╝
  ╚████╔╝      ██║      ██║
   ╚██╔╝       ██║      ██║
    ██║        ██║      ╚██████╗
    ╚═╝        ╚═╝       ╚═════╝
```

# 🎬 YouTube Transcript Curator (YTC)

> **Your Swiss Army CLI for YouTube transcript management.**
> Fetch, list, search, and open your transcript library at lightning speed. ⚡

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/DolphinDream/youtube-transcript-curator)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Tests](https://img.shields.io/badge/tests-458%20passed-brightgreen.svg)](https://github.com/DolphinDream/youtube-transcript-curator/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-72%25-brightgreen.svg)](https://github.com/DolphinDream/youtube-transcript-curator/tree/main/tests)

---

## 🔥 The Problem

Ever watched a 2-hour tutorial and can't remember which minute had that crucial command?
Spent hours searching through conference talks for a specific quote?
Watched a video last month but can't find it in your history?

**YouTube Transcript Curator solves this.**

---

## ✨ What Makes It Special

⚡ **One Command. One URL. Done.**
Fetch any YouTube video's transcript and metadata in seconds with a single command. No navigation menus, no waiting—just `ytc fetch URL` and you're done.

🔍 **Search Everything. Instantly.**
Full-text search across your entire transcript library. Find that exact quote from weeks ago in milliseconds. Use fuzzy `--search` to jump directly to matching timestamps on YouTube.

📊 **Smart Library Right in Your Terminal**
Filter by type (regular, livestream), sort by views/date/duration/channel. View results in compact, aligned table, or custom template format. All without leaving the terminal.

🎯 **Precision Control with Timestamps**
Open videos at exact timestamps. Jump to the exact moment you need. Combine with search to find content and jump to it instantly on YouTube.

📝 **Fully Customizable Output**
Template-based formatting with color-coded fields and custom placeholders. Make your library look exactly how you want—compact, detailed, or completely custom.

🗂️ **Complete Audit Trail**
Every fetch and deletion is logged. Never wonder if you've already transcribed a video. Check the history anytime.

⌨️ **Tab Completion for Ninja Speed**
All commands, flags, and options are tab-completable. Type `ytc list --ali<TAB>` and watch it complete. No memorizing syntax—become a transcript ninja with keyboard shortcuts alone.

⚡ **Quick Access with `--last` Flag**
Work with your most recent video instantly. Use `ytc open --last`, `ytc info --last`, or `ytc delete --last` without remembering the video ID. Perfect for workflows where you're processing videos sequentially.

📝 **Rich Video Metadata Display**
Use `--description` with `ytc info` to see full video descriptions. Use `--code` with `ytc open` to explicitly open in VS Code. Every detail you need, exactly when you need it.

---

## 🚀 Quick Start

### 📦 Installation

#### Option 1: Install with pipx (Recommended)

[pipx](https://pipx.pypa.io/) installs CLI tools in isolated environments - no dependency conflicts, no permission issues:

```bash
# Install pipx if you don't have it
brew install pipx  # macOS
# or: sudo apt install pipx  # Ubuntu/Debian

# Install YTC
pipx install youtube-transcript-curator

# Verify installation
ytc help
```

#### Option 2: Install with pip

If you prefer pip, use a virtual environment to avoid "externally managed environment" errors:

```bash
# Create and activate a venv (recommended)
python3 -m venv ~/.ytc-venv
source ~/.ytc-venv/bin/activate

# Install
pip install youtube-transcript-curator

# Verify
ytc help
```

> **Note:** On modern systems (macOS Homebrew, Ubuntu 23.04+), installing globally with `pip install` may fail. Use pipx or a venv instead.

#### Option 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/DolphinDream/youtube-transcript-curator.git
cd youtube-transcript-curator

# Run setup script (creates venv, installs dependencies, sets up tab completion)
chmod +x scripts/setup.sh
./scripts/setup.sh

# Add bin directory to PATH in your shell profile (~/.zshrc or ~/.bash_profile)
# Replace /path/to/repo with your actual cloned repository location
export PATH="/path/to/repo/youtube-transcript-curator/bin:$PATH"

# Reload shell configuration
source ~/.zshrc  # or ~/.bash_profile for bash
```

### 🗄️ Configuration

YTC needs to know where to store your transcript library (metadata, transcripts, logs).

**PyPI Installation:** First time you run `ytc`, a setup wizard prompts you to choose a storage location:

- Recommended: `~/Documents/YTC-Library` (macOS/Windows) or `~/YTC-Library` (Linux)
- Custom path of your choice
- Current directory

**Repository Installation:** Uses the built-in `data/output/` directory by default.

Your choice is saved to `~/.ytc/config.yaml`:

```yaml
version: 1
data:
  path: ~/Documents/YTC-Library
```

You can also override with an environment variable:

```bash
export YTC_DATA_PATH=~/my-transcripts
```

**For detailed configuration options:** See [docs/usage/CONFIG.md](./docs/usage/CONFIG.md)

### ⚡ 30-Second Demo

```bash
# Fetch a transcript
ytc fetch "https://youtu.be/dQw4w9WgXcQ"
ytc fetch "https://youtu.be/9-Jl0dxWQs8"

# List your library
ytc list

# Search across all transcripts
ytc search "machine learning"

# Open video at specific timestamp
ytc open 9-Jl0dxWQs8 --youtube --time 22:11

# Get help
ytc help
```

---

## 🎯 Core Commands

| Command | Description |
|---------|-------------|
| `ytc fetch <URL>` | Extract transcript and metadata from YouTube video |
| `ytc list` | Browse your transcript library with filters and sorting |
| `ytc search <KEYWORD>` | Search across all transcripts |
| `ytc open <VIDEO_ID>` | Open transcript in editor or video in YouTube |
| `ytc info <VIDEO_ID>` | Show detailed information about a video |
| `ytc ai <VIDEO_ID>` | AI-powered transcript analysis with Claude |
| `ytc extract <VIDEO_ID>` | Extract books, tools, and key points with AI |
| `ytc stats` | Display library statistics |
| `ytc delete <VIDEO_ID>` | Remove video from library |
| `ytc history` | View fetch and deletion history |

**For detailed guides:** See [docs/usage/](./docs/usage/) — particularly [AI.md](./docs/usage/AI.md) and [EXTRACT.md](./docs/usage/EXTRACT.md) for AI features

---

## 🎪 Key Features in Action

### 1. 📥 Fetch Transcripts

```bash
$ ytc fetch "https://youtu.be/IdPtTBbYOtw"

🎬 YouTube Transcript Curator > fetch
==================================================

📎 Parsing URL...
✓ Video ID: IdPtTBbYOtw

📋 Fetching video metadata...

📺 Video Info:
        Title: VS Code Live - v1.106 Release
     Duration: 1:28:12
        Views: 12,345
      Channel: Visual Studio Code
     Uploaded: 2024-12-05

📝 Fetching transcript...
✓ Retrieved 1,247 transcript segments

💾 Saving to ./data/output
✓ transcripts/youtube_IdPtTBbYOtw.txt
✓ metadata/metadata_IdPtTBbYOtw.json

==================================================
✅ Success!

💡 Quick access:
   ytc info --last
   ytc open --last
```

### 2. 🔎 Search Your Library

```bash
$ ytc search "robotics"

🎬 YouTube Transcript Curator > search
==================================================

🔍 Search Results

Found 8 matches in 4 videos

📺 How to create Web Dashboards for ROS 2 | COKyFP_VNAs
   The Construct Robotics Institute (4 matches)
      Line 165: [08:24] are a developer you are a robotics
      Line 167: [08:29] your robot might not be robotics
      ...

📺 Monitor Your Robots from the Web with Foxglove | S0dwRNwI050
   The Construct Robotics Institute (2 matches)
      Line 11: [00:48] the booing of Robotics projects we will
      ...
```

### 3. 🏷️ Smart Filtering & Sorting

```bash
# Sort by views (most popular first)
ytc list --sort views --limit 10

# Filter livestreams, sort by date
ytc list --type livestream --sort published

# Custom format with template
ytc list --format "%i | %t (%v views)"
```

### 4. 🎨 Template Formatting

Create custom output formats with placeholders:

```bash
# Format: ID | Title : Channel > (Published) | Duration
ytc list --format "%i | %t : %c > ( %p ) | %d"

# Simple format with view counts
ytc list --format "%i: %t (%v views)"
```

**Available placeholders:**
- `%i` / `%id` - Video ID
- `%t` / `%title` - Video title
- `%c` / `%channel` - Channel name
- `%d` / `%duration` - Video duration
- `%p` / `%published` - YouTube upload date
- `%v` / `%views` - View count
- `%P` / `%processed` - When transcribed
- `%T` / `%type` - Video type (Regular, Livestream, etc.)

### 5. 🤖 AI-Powered Transcript Analysis

Use Claude AI to understand your videos better:

```bash
# Generate automatic summary
ytc ai VIDEO_ID --summarize

# Ask specific questions
ytc ai VIDEO_ID --prompt "What are the main takeaways?"

# Summarize your most recent video
ytc ai --last --summarize --length short

# Extract code examples
ytc ai VIDEO_ID --prompt "List all code examples with explanations"
```

**Capabilities:**
- Auto-generate summaries (short, medium, or long)
- Ask custom questions about content
- Extract key concepts and patterns
- Works with local Claude CLI (no API costs)
- Perfect for learning, research, and documentation

See [docs/usage/AI.md](./docs/usage/AI.md) for complete AI documentation and examples.

### 6. 📚 Extract Books, Tools & Key Points

Extract structured information from videos with AI:

```bash
# Extract books and papers mentioned
ytc extract VIDEO_ID --books

# Extract tools, libraries, and frameworks
ytc extract VIDEO_ID --tools

# Extract key insights grouped by importance
ytc extract VIDEO_ID --key-points

# Extract everything at once
ytc extract VIDEO_ID --books --tools --key-points

# Open extracted data
ytc open VIDEO_ID --tools    # Opens tools.md
ytc open VIDEO_ID --books    # Opens books.md
```

**Output formats:**
- **JSON** - Structured data for querying and automation
- **Markdown** - Human-readable with clickable YouTube timestamps

**Example output:**

```
$ ytc extract VIDEO_ID --tools

🛠️ Extracting Tools & Software...
🤖 Analyzing with Claude...

   Found 12 items:
   1. LangChain (framework) - Mentioned at: 0:19
   2. ChromaDB (database) - Mentioned at: 0:19
   3. Docling (app) - Mentioned at: 0:14
   ...

✓ Saved to tools.json + tools.md
```

See [docs/usage/EXTRACT.md](./docs/usage/EXTRACT.md) for complete extraction documentation.

---

## 📂 Project Structure

```
youtube-transcript-curator/
├── src/
│   ├── cli/           # Command-line interface
│   ├── core/          # Core business logic
│   │   ├── metadata_fetcher.py
│   │   ├── transcript_fetcher.py
│   │   ├── library_manager.py
│   │   ├── library_logger.py
│   │   └── video_opener.py
│   └── utils/         # Utilities (config, logging, formatting)
├── config/
│   └── settings.yaml  # Application configuration
├── data/output/       # Default library location (repo installs only)
│   ├── metadata/      # Video metadata (JSON)
│   ├── transcripts/   # Raw transcripts
│   └── logs/          # Library change log
├── docs/usage/        # Detailed command documentation
├── scripts/           # Setup and utility scripts
└── tests/             # Unit and integration tests
```

---

## 💾 Output Files

### 📋 Metadata JSON

```json
{
  "video_id": "IdPtTBbYOtw",
  "url": "https://youtu.be/IdPtTBbYOtw",
  "title": "VS Code Live - v1.106 Release",
  "channel": "Visual Studio Code",
  "duration": 5292,
  "duration_string": "1:28:12",
  "view_count": 15234,
  "upload_date": "2025-11-01",
  "video_type": "livestream_recording",
  "processed_at": "2025-11-14T15:30:22",
  "transcript_file": "/absolute/path/to/youtube_IdPtTBbYOtw.txt"
}
```

### 📄 Raw Transcript

```text
0:00 - Welcome everyone to VS Code Live
0:15 - Today we're releasing version 1.106
1:30 - Let's start with the new features
5:45 - The terminal improvements are huge
...
```

---

## 🗺️ Roadmap

### ✅ Complete

- **Phases 1-4:** Core functionality
  - Transcript extraction with timestamps
  - Video metadata (title, channel, duration, views)
  - Library management (list, filter, sort, delete)
  - Full-text search, history tracking, tab completion

- **Phase 5:** AI Integration (v0.7.0)
  - Claude CLI integration (`ytc ai` command)
  - Transcript summarization with length control
  - Custom prompts for Q&A

- **Phase 6:** Testing & CI/CD (v0.8.0)
  - 458 tests, 72% coverage
  - GitHub Actions workflow
  - PyPI distribution

- **Phase 7-8:** AI-Processed Data (v0.8.0 - v0.9.0)
  - Auto-save summaries and extractions
  - `ytc extract --books --tools --key-points`
  - Dual-format output (JSON + Markdown)

### 🔄 Current (v1.0.0)

- First public release
- Full test coverage (680+ tests, macOS + Linux)
- PyPI distribution ready

### 🌐 Planned

- **API/IPC Mode:** Native messaging, HTTP server
- **Chrome Extension (YTCx):** One-click fetch, library status
- **Advanced Features:** Tags, collections, export formats
- **Cross-Platform:** Windows support

---

## ⚙️ Requirements

- **Python:** 3.10 or higher
- **Platform:** macOS and Linux (Ubuntu tested)
  - Windows support planned for future releases
- **Dependencies:** See `requirements.txt`

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [CONFIG.md](docs/usage/CONFIG.md) | Data storage configuration |
| [FETCH.md](docs/usage/FETCH.md) | Extract transcripts from YouTube |
| [LIST.md](docs/usage/LIST.md) | Browse and filter your library |
| [SEARCH.md](docs/usage/SEARCH.md) | Search across all transcripts |
| [OPEN.md](docs/usage/OPEN.md) | Open files and videos |
| [INFO.md](docs/usage/INFO.md) | View video details |
| [AI.md](docs/usage/AI.md) | AI-powered transcript analysis |
| [EXTRACT.md](docs/usage/EXTRACT.md) | Extract books, tools, key points |
| [STATS.md](docs/usage/STATS.md) | Library statistics |
| [DELETE.md](docs/usage/DELETE.md) | Remove videos from library |
| [OVERVIEW.md](docs/usage/OVERVIEW.md) | Complete command reference |

---

## ❓ FAQ

### Q: What platforms are supported?
**A:** macOS and Linux (Ubuntu tested). Windows is not currently supported due to bash script dependencies. The `--finder` flag behaves slightly differently on Linux (opens containing folder instead of highlighting the specific file).

### Q: Can I use this for commercial purposes?
**A:** Yes, the tool is MIT licensed. However, respect YouTube's Terms of Service and use transcripts responsibly.

### Q: What if a video doesn't have captions?
**A:** The tool will fail gracefully and notify you that captions are unavailable. It only works with videos that have auto-generated or manual captions.

### Q: Can I contribute?
**A:** Absolutely! See the Contributing section below.

### Q: How do I recover a deleted transcript?
**A:** Check `ytc history --action delete` to see what was deleted, then re-fetch the transcript from YouTube using the original URL or video ID.

### Q: Does this download the actual video?
**A:** No. It only fetches the text transcript and metadata. No video files are downloaded.

---

## 🤝 Contributing

Contributions are welcome! Areas where help is appreciated:

- **Platform Support:** Testing and fixes for Windows
- **Documentation:** Tutorials, examples, screenshots
- **Features:** Implement items from the roadmap
- **Bug Reports:** [Report issues](https://github.com/DolphinDream/youtube-transcript-curator/issues/new?labels=bug&title=Bug:%20) you encounter
- **Feature Requests:** [Open an issue](https://github.com/DolphinDream/youtube-transcript-curator/issues/new?labels=enhancement&title=Feature%20Request:%20) with your ideas
- **Questions:** [Start a discussion](https://github.com/DolphinDream/youtube-transcript-curator/issues/new?labels=question&title=Question:%20) about usage or development

**Guidelines:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Your feedback helps shape the future of YTC!

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Inspired by the need for better video research tools

---

## ⚙️ Version Info

| Item | Value |
|------|-------|
| **Version** | 1.0.0 |
| **Last Updated** | 2025-12-14 |
| **Status** | First Public Release |
| **Next Phase** | Cross-Video Features (v1.1.0) |

---

## ☕ Support

If you find YTC useful and want to support continued development:

> "I won't get rich from this project, but if you feel generous, every small donation helps keep my AI subscriptions active so I can continue co-authoring awesome tools like this one. Think of it as putting coins in my coding meter!" 🤖💰

[❤️ Sponsor on GitHub](https://github.com/sponsors/DolphinDream)

Your support is genuinely appreciated! 🙏

---

## 👨‍💻 Author

**Marius Giurgi** — Developer & Creator

Passionate about building tools that make developers' lives easier. Lover of clean code, thoughtful design, and open-source collaboration.

**Connect:**
- GitHub: [@DolphinDream](https://github.com/DolphinDream)
- LinkedIn: [mariusgiurgi](https://linkedin.com/in/mariusgiurgi)

**Interests:** Python, CLI tools, video processing, productivity automation, developer experience, robotics, autonomy, AI

**Made with** ☕ **and** 💜

---
