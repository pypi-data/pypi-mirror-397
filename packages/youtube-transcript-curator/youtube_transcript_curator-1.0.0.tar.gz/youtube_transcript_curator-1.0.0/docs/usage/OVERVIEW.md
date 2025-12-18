# YouTube Transcript Curator - Usage Guide

Welcome! This folder contains detailed guides for each command in YouTube Transcript Curator.

## Quick Links

- **[Fetching Transcripts](./FETCH.md)** - Download transcripts from YouTube videos
- **[Viewing Video Info](./INFO.md)** - Get details about your transcribed videos
- **[Opening Files & Videos](./OPEN.md)** - Open transcripts, metadata, or YouTube videos
- **[Listing Videos](./LIST.md)** - Browse your transcribed video library
- **[Searching Transcripts](./SEARCH.md)** - Find keywords across all transcripts
- **[Library Statistics](./STATS.md)** - View statistics about your library
- **[Library History](./HISTORY.md)** - View fetch and deletion history
- **[Deleting Videos](./DELETE.md)** - Remove videos from your library
- **[AI Analysis](./AI.md)** - Generate summaries with Claude AI
- **[AI Extraction](./EXTRACT.md)** - Extract books, tools, and key points

---

## Command Overview

### Core Commands

| Command | Purpose | Complexity |
|---------|---------|-----------|
| `ytc fetch` | Extract transcripts from YouTube videos | Beginner |
| `ytc info` | Show details about transcribed videos | Beginner |
| `ytc open` | Open files or YouTube videos | Beginner → Advanced |
| `ytc list` | Browse video library with filters | Beginner → Advanced |
| `ytc search` | Find keywords across transcripts | Beginner |
| `ytc stats` | View library overview | Beginner |
| `ytc history` | View library change history | Beginner |
| `ytc delete` | Remove videos from library | Beginner |
| `ytc ai` | Generate AI summaries with Claude | Beginner |
| `ytc extract` | Extract books, tools, key points | Beginner |

---

## Getting Started

### 1. First Time: Fetch a Transcript

```bash
ytc fetch "https://youtu.be/VIDEO_ID"
```

**See:** [FETCH.md](./FETCH.md) for all options and examples

### 2. Check What You Downloaded

```bash
ytc info VIDEO_ID
```

**See:** [INFO.md](./INFO.md) for more details

### 3. Browse Your Library

```bash
ytc list
ytc list --type regular        # Filter by type
ytc list --channel "VS Code"   # Filter by channel
```

**See:** [LIST.md](./LIST.md) for advanced filtering and sorting

### 4. Open Videos

```bash
ytc open VIDEO_ID              # Open transcript in Code
ytc open VIDEO_ID --youtube    # Open on YouTube
ytc open VIDEO_ID --youtube --time 5:45  # Jump to timestamp
```

**See:** [OPEN.md](./OPEN.md) for all options

### 5. Search & Explore

```bash
ytc search "keyword"           # Find in transcripts
ytc stats                      # Library overview
```

**See:** [SEARCH.md](./SEARCH.md) and [STATS.md](./STATS.md)

---

## Common Tasks

### Find a video

```bash
# Browse your videos
ytc list

# Filter by channel
ytc list --channel "VS Code"

# Filter by type
ytc list --type regular

# Search all transcripts for a keyword
ytc search "authentication"
```

### Jump to a specific part of a video

```bash
# Option 1: Use timestamp directly
ytc open VIDEO_ID --youtube --time 5:45

# Option 2 (Phase 4.1): Search for keyword automatically
ytc open VIDEO_ID --youtube --search "authentication"  # Coming soon!
```

### Get recent videos

```bash
# Sort by upload date
ytc list --sort date

# Coming soon (Phase 4.1):
ytc list --recent              # Latest transcribed
ytc list --recent --limit 5    # Latest 5
```

### View library overview

```bash
ytc stats
```

---

## Documentation Structure

Each command guide follows this structure:

1. **Quick Syntax** - One-liner usage
2. **Description** - What the command does
3. **Options** - Available flags and parameters
4. **Examples** - From simple to advanced
5. **Tips** - Pro tips and tricks
6. **See Also** - Related commands

---

## Getting Help

### Built-in Help

```bash
# Overview
ytc help

# Specific command
ytc help fetch
ytc help open
ytc help list

# Standard Click help (technical)
ytc fetch --help
ytc open --help
```

### These Docs

Each command has a detailed guide:
- Start with **Overview** section
- Check **Examples** section
- Look at **Tips** for pro usage

---

## Tips for Success

- **Always quote URLs** when using fetch:
  ```bash
  ytc fetch "https://youtu.be/VIDEO_ID"  # ✓ Correct
  ytc fetch https://youtu.be/VIDEO_ID    # ✗ May fail
  ```

- **Use Tab Completion** to discover options:
  ```bash
  ytc <TAB>                  # See all commands
  ytc list <TAB>             # See list options
  ytc list --type <TAB>      # See available types
  ```

- **Combine Filters** for powerful results:
  ```bash
  ytc list --type live --channel "VS Code" --sort date
  ```

- **Use --format json** for scripting:
  ```bash
  ytc list --format json | jq '.[] | select(.channel | contains("VS Code"))'
  ```

---

## Phases & Feature Availability

| Feature | Version | Status |
|---------|---------|--------|
| Fetch transcripts | 0.1.0 | ✅ Available |
| List & filter | 0.3.0 | ✅ Available |
| Open in Code/Finder | 0.2.0 | ✅ Available |
| Open on YouTube | 0.4.0 | ✅ Available |
| Timestamps with YouTube | 0.4.0 | ✅ Available |
| Search in transcripts | 0.3.0 | ✅ Available |
| Fuzzy type matching | 0.3.0 | ✅ Available |
| AI Summarization | 0.6.0 | ✅ Available |
| AI Extraction (books, tools, key points) | 0.9.0 | ✅ Available |
| Cross-video search | 1.1.0 | 📅 Coming Soon |

---

**Ready to dive in?** Start with [FETCH.md](./FETCH.md) if you're new, or jump to any command guide above!
