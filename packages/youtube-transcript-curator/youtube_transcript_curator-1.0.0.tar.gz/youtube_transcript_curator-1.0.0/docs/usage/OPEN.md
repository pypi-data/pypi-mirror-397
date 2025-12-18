# ytc open - Open Files and Videos

Open transcript files, metadata, or YouTube videos from your library.

---

## Quick Syntax

```bash
ytc open [VIDEO_ID] [OPTIONS]
```

**Examples:**
```bash
ytc open IdPtTBbYOtw                          # Open transcript in Code
ytc open --last                               # Open most recent video
ytc open IdPtTBbYOtw --code                   # Explicitly open in VS Code
ytc open IdPtTBbYOtw --youtube                # Open on YouTube
ytc open IdPtTBbYOtw --youtube --time 5:45    # Jump to 5:45
```

---

## Description

Opens files from your local library or jumps to YouTube videos. Supports:

- Opening transcripts in VS Code
- Opening metadata JSON in VS Code
- Opening files in Finder
- Opening videos on YouTube in Chrome
- Jumping to specific timestamps

---

## Options

### Quick Access

#### `--last`

Open the most recently fetched video automatically (no VIDEO_ID needed).

**Default:** false (requires VIDEO_ID)

```bash
ytc open --last                # Open most recent transcript in Code
ytc open --last --youtube      # Open most recent on YouTube
ytc open --last --youtube --time 5:30   # Jump to specific time
```

### Opening Local Files

#### `--code`

Explicitly open in VS Code editor (this is the default behavior).

**Default:** true (when no other option specified)

```bash
ytc open VIDEO_ID --code       # Explicitly open in Code (same as default)
ytc open --last --code         # Open most recent in Code
```

#### `--meta`

Open metadata JSON instead of transcript file.

**Default:** false (opens transcript)

```bash
ytc open VIDEO_ID          # Open transcript
ytc open VIDEO_ID --meta   # Open metadata
```

#### `--finder`

Open in Finder instead of VS Code.

**Default:** false (opens in Code)

```bash
ytc open VIDEO_ID --finder              # Open transcript in Finder
ytc open VIDEO_ID --meta --finder       # Open metadata in Finder
```

### Opening YouTube Videos

#### `--youtube`

Open the video on YouTube in Chrome browser.

**Default:** false (opens local files)

```bash
ytc open VIDEO_ID --youtube
```

#### `--time FORMAT`

Jump to a specific timestamp when opening on YouTube.

**Supported Formats:**
- `MM:SS` - Minutes and seconds: `5:45`
- `HH:MM:SS` - Hours, minutes, seconds: `1:30:45`
- Seconds only: `345` or `345s`
- Human-readable: `5m45s`

**Default:** Start of video (no timestamp)

```bash
ytc open VIDEO_ID --youtube --time 5:45       # MM:SS
ytc open VIDEO_ID --youtube --time 345        # Seconds
ytc open VIDEO_ID --youtube --time 1:30:45    # HH:MM:SS
ytc open VIDEO_ID --youtube --time 5m45s      # Human readable
```

#### `--search KEYWORD`

Fuzzy search within the transcript and jump to matching timestamp on YouTube.

Uses case-insensitive substring matching to find keywords in the transcript and automatically opens the video at the matching timestamp.

**Behavior:**
- **0 matches:** Shows error and suggests using `ytc search`
- **1 match:** Auto-opens YouTube at the matching timestamp
- **2-5 matches:** Shows interactive menu for selection
- **5+ matches:** Shows first 5 matches with indicator of additional matches

**Default:** false (no search)

```bash
ytc open VIDEO_ID --youtube --search "keyword"   # Fuzzy search and jump
ytc open VIDEO_ID --youtube --search "robotics"  # Case-insensitive
```

---

## Examples

### Quick Access: Most Recent Video

#### Open Most Recent Transcript

```bash
$ ytc open --last

🎬 YouTube Transcript Curator > open
==================================================
📺 Most recent: Introduction to Kubernetes
   Video ID: dQw4w9WgXcQ

✓ Opening Transcript in Code: /path/to/youtube_dQw4w9WgXcQ.txt
```

Quickly access your most recently fetched video without remembering its ID.

#### Open Most Recent on YouTube

```bash
$ ytc open --last --youtube

🎬 YouTube Transcript Curator > open
==================================================
📺 Most recent: Introduction to Kubernetes
   Video ID: dQw4w9WgXcQ

✓ Opening YouTube video dQw4w9WgXcQ
```

### Opening Transcripts (Local Files)

#### Default: Transcript in VS Code

```bash
$ ytc open IdPtTBbYOtw

✓ Opening Transcript in Code: /path/to/youtube_IdPtTBbYOtw.txt
```

Opens the file in your default editor (VS Code by default).

#### Open Metadata in Code

```bash
$ ytc open IdPtTBbYOtw --meta

✓ Opening Metadata in Code: /path/to/metadata_IdPtTBbYOtw.json
```

#### Open Transcript in Finder

```bash
$ ytc open IdPtTBbYOtw --finder

✓ Opening Transcript in Finder: /path/to/youtube_IdPtTBbYOtw.txt
```

Reveals the file in Finder (macOS).

#### Open Metadata in Finder

```bash
$ ytc open IdPtTBbYOtw --meta --finder

✓ Opening Metadata in Finder: /path/to/metadata_IdPtTBbYOtw.json
```

### Opening on YouTube

#### Basic: Open on YouTube

```bash
$ ytc open IdPtTBbYOtw --youtube

✓ Opening YouTube video IdPtTBbYOtw
```

Opens in Chrome browser at https://youtu.be/IdPtTBbYOtw

#### With Timestamp: Jump to 5 Minutes 45 Seconds

```bash
$ ytc open IdPtTBbYOtw --youtube --time 5:45

✓ Opening YouTube video IdPtTBbYOtw at 5:45
```

Opens at https://youtu.be/IdPtTBbYOtw?t=345

#### Different Timestamp Formats

All of these open at 90 seconds:

```bash
ytc open VIDEO_ID --youtube --time 1:30        # MM:SS
ytc open VIDEO_ID --youtube --time 90          # Seconds
ytc open VIDEO_ID --youtube --time 90s         # Seconds (explicit)
ytc open VIDEO_ID --youtube --time 1m30s       # Human readable
```

#### Jump to Hour, Minute, Second

```bash
ytc open VIDEO_ID --youtube --time 1:30:45
# Opens at 1 hour, 30 minutes, 45 seconds (5445 seconds)
```

#### Fuzzy Search and Jump to Match

```bash
$ ytc open a3uMv1S-1tM --youtube --search "skill"

Found 5 matches for 'skill' in a3uMv1S-1tM:

[1] [0:01] skills. And on paper it sounds really
[2] [0:58] Claude skills? You can see it as modular
[3] [1:28] so that the concept of skills are clear
[4] [1:54] claude which is different than skills
[5] [2:26] skills. What you can actually do though

Select match (1-5) or press Enter for [1]:
```

Enter a number to select, or just press Enter to use match 1. The video will open at the selected timestamp.

**Single Match (Auto-Opens):**

```bash
$ ytc open VIDEO_ID --youtube --search "unique-keyword"

✓ Found 1 match for 'unique-keyword'
[0:42] The specific part about unique-keyword...
→ Opening YouTube at 0:42...

✓ Opened YouTube video at 0:42
```

**No Matches:**

```bash
$ ytc open VIDEO_ID --youtube --search "nonexistent"

✗ No matches found for 'nonexistent' in VIDEO_ID
Try: ytc search nonexistent  # to find across all videos
```

---

## Use Cases

### Finding a Specific Part of a Long Video

You remember a topic was discussed but not the timestamp?

```bash
# Option 1: Fuzzy search the transcript (recommended)
ytc open VIDEO_ID --youtube --search "authentication"
# Will find the keyword and jump to that section automatically

# Option 2: Jump to approximate time you remember
ytc open VIDEO_ID --youtube --time 30:00  # Try 30 minutes in

# Option 3: Search across all videos first
ytc search "authentication"  # Find which videos mention it
ytc open VIDEO_ID --youtube --search "authentication"
```

### Sharing a Video Link with Timestamp

Found something interesting at 5:45?

```bash
# Open locally to find the exact moment
ytc open VIDEO_ID

# Once you know the time, share the YouTube link
ytc open VIDEO_ID --youtube --time 5:45
# Then copy the URL from browser: https://youtu.be/VIDEO_ID?t=345
```

### Reviewing a Video While Working

```bash
# Open transcript in Code for reference
ytc open VIDEO_ID

# Also open on YouTube for playback
ytc open VIDEO_ID --youtube --time 10:00

# You can now:
# - Read transcript in Code
# - Watch video in Chrome
# - Reference both side-by-side
```

### Learning at Your Own Pace

```bash
# Find the topic you want to learn about
ytc search "JWT authentication"

# Once you find the video, jump straight to it
ytc open VIDEO_ID --youtube --time 5:45

# Or open transcript to read along
ytc open VIDEO_ID
```

---

## Tips & Tricks

### Finding the Right Timestamp

```bash
# Open transcript to find the line you want
ytc open VIDEO_ID

# Search for key phrase (Cmd+F in Code)
# See the timestamp at the start of that line

# Jump there on YouTube
ytc open VIDEO_ID --youtube --time 5:45
```

### Quick Workflow for Research

```bash
# 1. Search for topic across all videos
ytc search "database optimization"

# 2. Open metadata of relevant video
ytc open VIDEO_ID --meta

# 3. Check details in metadata
# (title, channel, duration, etc.)

# 4. Jump to that part on YouTube
ytc open VIDEO_ID --youtube --time 15:30

# 5. Or open transcript for detailed review
ytc open VIDEO_ID
```

### Browser Integration

```bash
# Opening with --youtube uses your default browser
# Currently optimized for Chrome
# Falls back to system default if Chrome not found

# If Chrome not installed, try:
# 1. Install Google Chrome
# 2. Or set your default browser to Chrome
# 3. Or manually visit: https://youtu.be/VIDEO_ID?t=SECONDS
```

### Batch Opening

```bash
# Get a list of videos you want to review
ytc list --channel "VS Code" --format ids > list.txt

# Open each one (you'll be prompted for each)
for id in $(cat list.txt); do
  ytc open "$id" --youtube
done
```

---

## Common Issues

### Error: "Transcript file not found"

**Problem:** You haven't downloaded the transcript yet.

**Solution:** Fetch it first:

```bash
ytc fetch VIDEO_ID
ytc open VIDEO_ID
```

### Error: "Chrome not found"

**Problem:** You don't have Google Chrome installed.

**Options:**
1. Install Google Chrome: https://www.google.com/chrome/
2. Use a different browser manually: Copy the URL from the terminal
3. Check that Chrome is in standard location

```bash
# You can manually construct the URL:
# https://youtu.be/{VIDEO_ID}?t={SECONDS}

ytc open VIDEO_ID --youtube --time 5:45
# Tells you: https://youtu.be/VIDEO_ID?t=345
# Copy/paste into your browser
```

### Wrong Timestamp Format

**Problem:** `ytc open VIDEO_ID --youtube --time 5.45` (period instead of colon)

**Solution:** Use correct format:

```bash
ytc open VIDEO_ID --youtube --time 5:45    # ✓ Correct (MM:SS)
ytc open VIDEO_ID --youtube --time 5.45    # ✗ Won't work
```

### Editor Won't Open

**Problem:** `ytc open VIDEO_ID` doesn't open in Code

**Issue:** VS Code not found, or not in PATH

**Solutions:**
```bash
# Use Finder instead
ytc open VIDEO_ID --finder

# Or open manually
cat data/output/transcripts/youtube_VIDEO_ID.txt
```

---

## Phase 4.0 vs Phase 4.1

### Phase 4.0 (Current)

- Open YouTube with manual timestamps
- `ytc open VIDEO_ID --youtube --time 5:45`

### Phase 4.1 (Coming Soon)

- Automatic timestamp from keyword search
- `ytc open VIDEO_ID --youtube --search "authentication"`
- Finds first mention and jumps there automatically

---

## See Also

- [FETCH.md](./FETCH.md) - Download transcripts
- [INFO.md](./INFO.md) - View video details
- [LIST.md](./LIST.md) - Browse your library
- [SEARCH.md](./SEARCH.md) - Find keywords

---

**Shorthand:** `ytc open --help` shows quick reference
