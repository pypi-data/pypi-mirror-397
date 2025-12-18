# ytc info - View Video Details

Display information about a transcribed video including metadata and file locations.

---

## Quick Syntax

```bash
ytc info [VIDEO_ID_OR_URL] [OPTIONS]
```

**Examples:**
```bash
ytc info IdPtTBbYOtw                    # Show info for specific video
ytc info --last                         # Show info for most recent
ytc info IdPtTBbYOtw --description      # Include full description
ytc info "https://youtu.be/IdPtTBbYOtw"
```

---

## Description

Shows details about a video you've already transcribed, including:

- Whether transcript and metadata files exist
- Video title, channel, and duration
- Video type (regular, livestream, livestream recording)
- YouTube URL
- When the transcript was processed (downloaded)
- File locations on disk

This is useful for checking what information you have about a video before opening or searching it.

---

## Options

### `--last`

Show information for the most recently fetched video (no VIDEO_ID needed).

**Default:** false (requires VIDEO_ID)

```bash
ytc info --last                # Show most recent video info
ytc info --last --description  # Include full description
```

### `--description`

Include the full video description in the output.

**Default:** false (only show basic metadata)

```bash
ytc info VIDEO_ID --description        # Show with full description
ytc info --last --description          # Most recent with description
```

---

## URL Formats Supported

All of these work:

```bash
# Just the video ID (11 characters)
ytc info IdPtTBbYOtw

# Short URL
ytc info "https://youtu.be/IdPtTBbYOtw"

# Full URL
ytc info "https://www.youtube.com/watch?v=IdPtTBbYOtw"

# With timestamps (timestamps are ignored)
ytc info "https://youtu.be/IdPtTBbYOtw?t=5m30s"
```

**⚠️ Important:** Always quote URLs with special characters:

```bash
ytc info "https://youtu.be/VIDEO?t=123&si=abc"    # ✓ Correct
ytc info https://youtu.be/VIDEO?t=123&si=abc      # ✗ Will fail!
```

---

## Examples

### Quick Access: Most Recent Video

```bash
$ ytc info --last

🎬 YouTube Transcript Curator > info
==================================================
📺 Most recent: VS Code Live - v1.106 Release
   Video ID: IdPtTBbYOtw

📊 Video Info: IdPtTBbYOtw
==================================================

📁 Files:
   ✓ transcript: ~/youtube-transcript-curator/data/output/transcripts/youtube_IdPtTBbYOtw.txt
   ✓ metadata: ~/youtube-transcript-curator/data/output/metadata/metadata_IdPtTBbYOtw.json

📋 Metadata:
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code
   Duration: 1:23:45
   Type: Regular
   URL: https://youtu.be/IdPtTBbYOtw
   Processed: 2025-11-14 15:30:22
```

Quickly check info for your most recent video without remembering the ID.

### Basic: Check Video Details

```bash
$ ytc info IdPtTBbYOtw

📊 Video Info: IdPtTBbYOtw
==================================================

📁 Files:
   ✓ transcript: ~/youtube-transcript-curator/data/output/transcripts/youtube_IdPtTBbYOtw.txt
   ✓ metadata: ~/youtube-transcript-curator/data/output/metadata/metadata_IdPtTBbYOtw.json

📋 Metadata:
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code
   Duration: 1:23:45
   Type: Regular
   URL: https://youtu.be/IdPtTBbYOtw
   Processed: 2025-11-14 15:30:22
```

### With Description: Full Video Details

```bash
$ ytc info IdPtTBbYOtw --description

📊 Video Info: IdPtTBbYOtw
==================================================

📁 Files:
   ✓ transcript: ~/youtube-transcript-curator/data/output/transcripts/youtube_IdPtTBbYOtw.txt
   ✓ metadata: ~/youtube-transcript-curator/data/output/metadata/metadata_IdPtTBbYOtw.json

📋 Metadata:
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code
   Duration: 1:23:45
   Type: Regular
   URL: https://youtu.be/IdPtTBbYOtw
   Processed: 2025-11-14 15:30:22

📄 Description:
   In this VS Code Live stream, we explore the new features in the v1.106 release
   including improved IntelliSense, better debugging support, and performance
   optimizations. We also discuss the roadmap for future releases.
```

### URL Input: Using Full YouTube URL

```bash
$ ytc info "https://www.youtube.com/watch?v=IdPtTBbYOtw"

📊 Video Info: IdPtTBbYOtw
==================================================

📁 Files:
   ✓ transcript: /path/to/youtube_IdPtTBbYOtw.txt
   ✓ metadata: /path/to/metadata_IdPtTBbYOtw.json

📋 Metadata:
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code
   Duration: 1:23:45
   Type: Regular
   URL: https://youtu.be/IdPtTBbYOtw
   Processed: 2025-11-14 15:30:22
```

### Not Yet Transcribed

```bash
$ ytc info unknown123456789

📊 Video Info: unknown123456789
==================================================

❌ No files found for video: unknown123456789

Run: ytc fetch <URL>
```

---

## Use Cases

### Verify Before Opening

```bash
# Check if transcript exists before trying to open
ytc info VIDEO_ID

# Then open if files exist
ytc open VIDEO_ID
```

### Confirm What Was Downloaded

```bash
# After fetching, verify what was saved
ytc fetch "https://youtu.be/VIDEO_ID"
ytc info VIDEO_ID    # Confirm files are there
```

### Check When Transcript Was Downloaded

```bash
# See the exact time transcript was processed
ytc info VIDEO_ID

# Look at the "Processed:" timestamp
# Useful for checking recently downloaded videos
```

### Verify Transcript Location

```bash
# Find the exact file path for a transcript
ytc info VIDEO_ID

# Copy the transcript path if you need to:
# - Process it with other tools
# - Back it up
# - Move it elsewhere
```

### Batch Verification

```bash
# Check multiple videos to see which ones are downloaded
for id in VIDEO_ID_1 VIDEO_ID_2 VIDEO_ID_3; do
  ytc info "$id"
done
```

---

## Tips & Tricks

### Finding Video IDs

```bash
# Can't remember the video ID? Use list to find it
ytc list

# Then get info about a specific video
ytc info VIDEO_ID
```

### Checking File Sizes Manually

```bash
# Info shows the file paths, you can check sizes
ytc info VIDEO_ID

# Then check file size
ls -lh /path/to/youtube_VIDEO_ID.txt
```

### URL Recognition

```bash
# The command automatically extracts video ID from any URL format
# These all show the same video info:
ytc info VIDEO_ID
ytc info "https://youtu.be/VIDEO_ID"
ytc info "https://www.youtube.com/watch?v=VIDEO_ID"
ytc info "https://youtu.be/VIDEO_ID?t=5m30s"    # Timestamp ignored
```

---

## Common Issues

### Error: "Invalid YouTube URL or video ID"

**Problem:** `ytc info "not-a-valid-id"`

**Solution:** Make sure you're using a valid YouTube video ID or URL:

```bash
# Valid video IDs are 11 characters (letters, numbers, -, _)
ytc info IdPtTBbYOtw         # ✓ Correct

# Invalid formats
ytc info my-video            # ✗ Too short
ytc info "Random Title"      # ✗ Not an ID or URL
```

**Supported formats:**
```bash
ytc info VIDEO_ID                                      # 11-char ID
ytc info "https://youtu.be/VIDEO_ID"                   # Short URL
ytc info "https://www.youtube.com/watch?v=VIDEO_ID"    # Full URL
```

### Error: "No files found for video"

**Problem:** `ytc info VIDEO_ID` says files not found

**Reason:** You haven't downloaded the transcript yet

**Solution:** Fetch the transcript first:

```bash
ytc fetch "https://youtu.be/VIDEO_ID"
ytc info VIDEO_ID    # Now it will show the files
```

### Wrong URL Format

**Problem:** `ytc info "https://youtu.be/VIDEO"` returns error (unquoted URL)

**Solution:** Always quote URLs with special characters:

```bash
ytc info "https://youtu.be/VIDEO_ID?t=123"    # ✓ Correct (quoted)
ytc info https://youtu.be/VIDEO_ID?t=123      # ✗ Wrong (shell misinterprets &,?)
```

---

## Reading the Output

### Files Section

```
📁 Files:
   ✓ transcript: /path/to/youtube_VIDEO_ID.txt
   ✓ metadata: /path/to/metadata_VIDEO_ID.json
```

- `✓` means the file exists
- `✗` means the file is missing (you only fetched one type)
- Path shows exactly where the file is located

### Metadata Section

| Field | Meaning |
|-------|---------|
| Title | Video title on YouTube |
| Channel | Channel that uploaded the video |
| Duration | Total video length (HH:MM:SS format) |
| Type | Regular video or livestream/recording |
| URL | Clean YouTube URL (youtu.be format) |
| Processed | When the transcript was downloaded to your library |

### Video Types

```
Regular              # Standard YouTube video
Livestream           # Live stream broadcast
Livestream Recording # Recording of a livestream
```

---

## See Also

- [FETCH.md](./FETCH.md) - Download transcripts
- [OPEN.md](./OPEN.md) - Open files or YouTube videos
- [LIST.md](./LIST.md) - Browse your library
- [SEARCH.md](./SEARCH.md) - Find keywords in transcripts

---

**Shorthand:** `ytc info --help` shows quick reference
