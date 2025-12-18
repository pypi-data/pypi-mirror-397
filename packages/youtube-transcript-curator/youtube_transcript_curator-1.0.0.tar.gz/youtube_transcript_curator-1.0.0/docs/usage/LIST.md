# ytc list - Browse Your Video Library

List and browse all your transcribed videos with powerful filtering and sorting.

---

## Quick Syntax

```bash
ytc list [OPTIONS]
```

**Examples:**
```bash
ytc list                              # All videos
ytc list --type regular               # Filter by type
ytc list --channel "VS Code"          # Filter by channel
ytc list --sort title                 # Sort alphabetically
ytc list --limit 10                   # Show only 10
```

---

## Description

Shows all transcribed videos from your library with flexible options to filter, sort, and format the output.

---

## Options

### `--format`

Change how results are displayed. Supports presets or custom templates.

**Preset Formats:**

- `compact` (default) - One line per video with ID, title, channel, duration, type
- `full` - Detailed information for each video (multi-line)
- `ids` - Just video IDs (great for scripts)
- `json` - JSON format (for parsing)

**Custom Templates:**

Use `%` placeholders to create custom formats:

- `%i` / `%id` - Video ID
- `%t` / `%title` - Video title
- `%c` / `%channel` - Channel name
- `%d` / `%duration` - Video duration
- `%T` / `%type` - Video type (Regular, Livestream, etc.)
- `%p` / `%published` - YouTube upload date
- `%P` / `%processed` - When transcribed
- `%v` / `%views` - View count

**Preset Examples:**

```bash
ytc list                    # Compact format (default)
ytc list --format compact   # Explicit compact
ytc list --format full      # Show all details
ytc list --format ids       # Just IDs
ytc list --format json      # JSON output
```

**Template Examples:**

```bash
# Custom format: ID | Title : Channel > (Published) | Duration
ytc list --format "%i | %t : %c > ( %p ) | %d"

# Simple format with view count
ytc list --format "%i: %t (%v views)"

# Title with duration
ytc list --format "%t (%d)"

# Compact with channel and views
ytc list --format "%i | %t | %c | %v"
```

### `--type`

Filter by video type with **fuzzy matching support**.

**Types:**
- `regular` - Regular uploaded videos
- `livestream_recording` - Recorded livestreams
- `livestream` - Live streamed content (if available)

**Fuzzy Shortcuts:**
- `reg` → regular
- `rec` / `recording` → livestream_recording
- `live` / `ls` → any livestream type

```bash
ytc list --type regular              # Exact match
ytc list --type reg                  # Fuzzy match (shortcut)
ytc list --type livestream_recording # Full name
ytc list --type rec                  # Shortcut
ytc list --type live                 # Any livestream
```

### `--channel`

Filter by channel name (case-insensitive).

```bash
ytc list --channel "VS Code"         # Exact channel name
ytc list --channel "The Construct"   # Partial matching works
```

### `--sort`

Sort results by specified field.

**Choices:**
- `date` (default) - When transcribed (newest first)
- `published` - YouTube upload date (newest first)
- `title` - Alphabetically by title
- `channel` - By channel name
- `duration` - By video length (shortest first)
- `views` - By view count (most viewed first)

```bash
ytc list                        # Sort by when transcribed (default, newest first)
ytc list --sort date           # Explicit date sorting (when transcribed)
ytc list --sort published      # By YouTube upload date
ytc list --sort title          # Alphabetically
ytc list --sort channel        # By channel
ytc list --sort duration       # By length
ytc list --sort views          # By view count
```

### `--reverse`

Reverse the sort order.

```bash
ytc list --sort title          # A → Z
ytc list --sort title --reverse # Z → A
```

### Auto-Injection with Compact Format

When using `--format compact` (default) with sorts that aren't already shown, the relevant field is automatically inserted between channel and duration:

**Auto-Injection Examples:**

```bash
# Sort by published: shows date between channel and duration
ytc list --sort published
# Output: ID | Title | Channel | 2025-11-14 | Duration [Type]

# Sort by views: shows view count between channel and duration
ytc list --sort views
# Output: ID | Title | Channel | 934188 | Duration [Type]
```

This keeps the compact format readable while showing the field you're sorting by. For full control over format, use custom templates with `--format`.

### `--align`

Display results in a vertically aligned tabular format with `|` column separators.

This format is useful when you want to visually align columns for easy scanning. It preserves the same color scheme as the compact format but provides cleaner column separation.

```bash
ytc list                    # Compact format (default)
ytc list --align            # Aligned tabular format
ytc list --align --sort views  # Aligned format sorted by views
```

**Aligned Format Example:**

```bash
$ ytc list --align --sort published --limit 3
fHGMA8hLNt8 | Get These Context Agents... Fix 90% of the Problem... | AI LABS            | 2025-11-15   | 12:56        [Regular]
Oneu1jg7E8w | If I Started with AI Today—This Is Exactly What I'... | Matt Maher         | 2025-11-14   | 13:14        [Regular]
UWVkwvvmyKo | Google Just Dropped a World-Aware AI Agent Shockin... | AI Revolution      | 2025-11-14   | 9:13         [Regular]
```

When used with sort options that inject fields (like `--sort views` or `--sort published`), the injected field is displayed between channel and duration.

### `--limit`

Show only the first N results.

```bash
ytc list                # All videos
ytc list --limit 5      # First 5
ytc list --limit 10     # First 10
ytc list --limit 1      # Just 1
```

---

## Examples

### Basic: List All Videos

```bash
$ ytc list

S0dwRNwI050 | Monitor Your Robots from the... | The Construct Robotics Institute | 1:08:54 [Regular]
COKyFP_VNAs | How to create Web Dashboards... | The Construct Robotics Institute | 1:01:34 [Regular]
dQw4w9WgXcQ | Tech Talks Weekly Episode 5 | TechTalk Productions | 41:48 [Regular]
IdPtTBbYOtw | VS Code Live - v1.106 Release | Visual Studio Code | 1:28:12 [Livestream Recording]
```

### Filter by Type

```bash
$ ytc list --type regular
S0dwRNwI050 | Monitor Your Robots from the... | The Construct Robotics Institute | 1:08:54 [Regular]
COKyFP_VNAs | How to create Web Dashboards... | The Construct Robotics Institute | 1:01:34 [Regular]
dQw4w9WgXcQ | Tech Talks Weekly Episode 5 | TechTalk Productions | 41:48 [Regular]
```

### Fuzzy Type Matching

```bash
# All work the same:
ytc list --type regular
ytc list --type reg
ytc list --type rg

# For livestreams:
ytc list --type live              # Any livestream type
ytc list --type ls               # Shortcut
ytc list --type livestream_recording
ytc list --type rec
ytc list --type recording
```

### Filter by Channel

```bash
$ ytc list --channel "VS Code"
IdPtTBbYOtw | VS Code Live - v1.106 Release | Visual Studio Code | 1:28:12 [Livestream Recording]
```

### Sort Differently

```bash
# Sort by title
$ ytc list --sort title
COKyFP_VNAs | How to create Web Dashboards... | The Construct Robotics Institute | 1:01:34 [Regular]
dQw4w9WgXcQ | Tech Talks Weekly Episode 5 | TechTalk Productions | 41:48 [Regular]
IdPtTBbYOtw | VS Code Live - v1.106 Release | Visual Studio Code | 1:28:12 [Livestream Recording]
S0dwRNwI050 | Monitor Your Robots from the... | The Construct Robotics Institute | 1:08:54 [Regular]

# Reverse order (Z → A)
$ ytc list --sort title --reverse
S0dwRNwI050 | Monitor Your Robots from the... | The Construct Robotics Institute | 1:08:54 [Regular]
IdPtTBbYOtw | VS Code Live - v1.106 Release | Visual Studio Code | 1:28:12 [Livestream Recording]
dQw4w9WgXcQ | Tech Talks Weekly Episode 5 | TechTalk Productions | 41:48 [Regular]
COKyFP_VNAs | How to create Web Dashboards... | The Construct Robotics Institute | 1:01:34 [Regular]

# Sort by YouTube upload date (newest first)
$ ytc list --sort published
[Videos sorted by when they were published on YouTube, newest first]

# Sort by view count (most viewed first)
$ ytc list --sort views
[Videos sorted by view count, most viewed first]

# Oldest published videos first
$ ytc list --sort published --reverse
[Videos sorted by publish date, oldest first]
```

### Show Only First 10

```bash
$ ytc list --limit 10
[Shows first 10 videos]
```

### Full Details

```bash
$ ytc list --format full
[Shows complete information for each video]
```

### JSON Output (For Scripts)

```bash
$ ytc list --format json
[{"video_id":"S0dwRNwI050", "title":"Monitor Your Robots...", ...}]
```

Just Video IDs:

```bash
$ ytc list --format ids
S0dwRNwI050
COKyFP_VNAs
dQw4w9WgXcQ
IdPtTBbYOtw
```

### Combined Filters

```bash
# Show only VS Code videos, sorted by title
$ ytc list --channel "VS Code" --sort title

# Show 5 regular videos, reverse sorted by duration
$ ytc list --type regular --limit 5 --sort duration --reverse

# Show livestream recordings, organized by channel
$ ytc list --type live --sort channel
```

---

## Tips & Tricks

### Extract Video IDs for Batch Processing

```bash
# Get all video IDs
ytc list --format ids > videos.txt

# Use in a loop
while read id; do
  ytc open "$id" --youtube
done < videos.txt
```

### Get JSON for Processing

```bash
# Get all videos as JSON
ytc list --format json > library.json

# Filter with jq (if installed)
cat library.json | jq '.[] | select(.channel | contains("VS Code"))'
```

### Find Videos by Partial Channel Name

```bash
# Case-insensitive, partial matching works
ytc list --channel "Construct"  # Matches "The Construct Robotics Institute"
ytc list --channel "code"       # Matches "Visual Studio Code"
```

### Combine with Other Commands

```bash
# Get video IDs, then open first one on YouTube
first_id=$(ytc list --format ids | head -1)
ytc open "$first_id" --youtube

# Get all regular video IDs
ytc list --type regular --format ids

# Count videos by channel
ytc list --format full | grep "Channel:" | sort | uniq -c
```

---

## Common Issues

### No videos found

**Problem:** `ytc list` returns "No transcribed videos found"

**Solution:** You need to fetch videos first:

```bash
ytc fetch "https://youtu.be/VIDEO_ID"
ytc list
```

### Wrong type name

**Problem:** `ytc list --type video` shows error

**Solution:** Use one of the supported types:

```bash
ytc list --type regular              # ✓ Correct
ytc list --type livestream_recording # ✓ Correct
ytc list --type live                 # ✓ Correct (any livestream)

# Fuzzy shortcuts work too
ytc list --type reg   # regular
ytc list --type rec   # livestream_recording
ytc list --type live  # any livestream
```

### Channel filtering not working

**Problem:** `ytc list --channel "xyz"` shows nothing

**Solution:** Check the actual channel name:

```bash
# See all channels
ytc list --format full

# Then filter with exact spelling
ytc list --channel "The Construct Robotics Institute"

# Partial matching is case-insensitive
ytc list --channel "construct"  # Works if channel contains "construct"
```

---

## See Also

- [FETCH.md](./FETCH.md) - Download transcripts
- [OPEN.md](./OPEN.md) - Open videos or files
- [SEARCH.md](./SEARCH.md) - Search transcripts
- [INFO.md](./INFO.md) - View video details
- [STATS.md](./STATS.md) - Library statistics

---

**Shorthand:** `ytc list --help` shows quick reference
