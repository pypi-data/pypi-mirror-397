# ytc fetch - Extract Transcripts from YouTube

Extract transcript and metadata from any YouTube video.

---

## Quick Syntax

```bash
ytc fetch <URL_OR_VIDEO_ID>
```

**Examples:**
```bash
ytc fetch "https://youtu.be/dQw4w9WgXcQ"
ytc fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
ytc fetch dQw4w9WgXcQ
```

---

## Description

Fetches the transcript and metadata from a YouTube video and saves them locally.

### What Gets Downloaded

1. **Metadata JSON** (`metadata_[VIDEO_ID].json`)
   - Video ID, URL, title, channel, duration
   - View count, upload date, video type (regular/livestream/etc.)
   - When transcribed (`processed_at`)
   - File locations

2. **Transcript** (`youtube_[VIDEO_ID].txt`)
   - Full transcript text with timestamps
   - Line-by-line, readable format
   - Preserves timing information

### Where Files Are Saved

```
data/output/
├── metadata/
│   └── metadata_[VIDEO_ID].json
└── transcripts/
    └── youtube_[VIDEO_ID].txt
```

---

## Options

### `--overwrite`

Overwrite existing files if they already exist.

**Default:** false (won't overwrite)

```bash
# First time - creates files
ytc fetch "https://youtu.be/VIDEO_ID"

# Re-fetch with new options
ytc fetch "https://youtu.be/VIDEO_ID" --overwrite
```

### `--no-timestamps`

Remove timestamps from the transcript (saves a bit of space).

**Default:** false (keeps timestamps)

```bash
# Transcript WITH timestamps (default)
ytc fetch "https://youtu.be/VIDEO_ID"
# Output: [00:45] Welcome to the tutorial...

# Transcript WITHOUT timestamps
ytc fetch "https://youtu.be/VIDEO_ID" --no-timestamps
# Output: Welcome to the tutorial...
```

### `--output-dir PATH`

Save to a custom directory instead of default `data/output`.

**Default:** `data/output` (from config)

```bash
ytc fetch "https://youtu.be/VIDEO_ID" --output-dir /custom/path
```

---

## URL Formats Supported

All of these work:

```bash
# Shortening URLs
ytc fetch "https://youtu.be/dQw4w9WgXcQ"
ytc fetch "youtu.be/dQw4w9WgXcQ"

# Standard URLs
ytc fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
ytc fetch "www.youtube.com/watch?v=dQw4w9WgXcQ"

# With timestamps (ignored for fetch, but okay)
ytc fetch "https://youtu.be/dQw4w9WgXcQ?t=123s"
ytc fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=5m30s"

# Just the video ID
ytc fetch "dQw4w9WgXcQ"
ytc fetch dQw4w9WgXcQ
```

**⚠️ Important:** Always quote URLs with special characters:

```bash
ytc fetch "https://youtu.be/VIDEO?t=123&si=abc"    # ✓ Correct
ytc fetch https://youtu.be/VIDEO?t=123&si=abc      # ✗ Will fail!
```

---

## Examples

### Basic - Download a Single Video

```bash
$ ytc fetch "https://youtu.be/dQw4w9WgXcQ"

Fetching transcript for dQw4w9WgXcQ...
✓ Metadata saved
✓ Transcript saved (1,200 lines)
✓ Processed in 2.3 seconds

📺 Video Info:
   Title: Never Gonna Give You Up
   Channel: Rick Astley
   Duration: 3:32
   Views: 1,234,567,890
   Uploaded: 2009-10-25

📁 Files saved to: ~/youtube-transcript-curator/data/output
   📄 Metadata: metadata/metadata_dQw4w9WgXcQ.json
   📝 Transcript: transcripts/youtube_dQw4w9WgXcQ.txt
```

### Download Multiple Videos

```bash
# One by one
ytc fetch "https://youtu.be/VIDEO_ID_1"
ytc fetch "https://youtu.be/VIDEO_ID_2"
ytc fetch "https://youtu.be/VIDEO_ID_3"
```

### Re-fetch with Different Options

```bash
# Original: with timestamps
ytc fetch "https://youtu.be/dQw4w9WgXcQ"

# Later: re-fetch without timestamps
ytc fetch "https://youtu.be/dQw4w9WgXcQ" --overwrite --no-timestamps
```

### Custom Output Directory

```bash
ytc fetch "https://youtu.be/VIDEO_ID" --output-dir ~/Videos/transcripts
```

---

## Tips & Tricks

### Batch Download from a Text File

```bash
# Create a file with URLs (one per line)
cat > urls.txt << EOF
https://youtu.be/VIDEO_ID_1
https://youtu.be/VIDEO_ID_2
https://youtu.be/VIDEO_ID_3
EOF

# Download all
while read url; do
  ytc fetch "$url"
done < urls.txt
```

### Quick Copy for Batch Processing

```bash
# Get list of video IDs to fetch
ytc list --format ids > videos_to_fetch.txt

# Then use in a loop
while read id; do
  ytc fetch "$id"
done < videos_to_fetch.txt
```

### Check Before Re-fetching

```bash
# Check if already downloaded
ytc info VIDEO_ID

# If yes, re-fetch with --overwrite
ytc fetch VIDEO_ID --overwrite
```

### View Downloaded Transcript

```bash
# In VS Code
ytc open VIDEO_ID

# In Finder
ytc open VIDEO_ID --finder

# In terminal (on macOS)
cat data/output/transcripts/youtube_VIDEO_ID.txt
```

---

## Common Issues

### Error: "No transcript found"

**Problem:** The video doesn't have captions enabled.

**Solution:** Some YouTube videos don't have transcripts available (especially livestreams without auto-generated captions). Not much can be done in this case.

```bash
# Try anyway
ytc fetch "https://youtu.be/VIDEO_ID"

# If it fails, check if video has captions on YouTube
# Not all videos have transcripts available
```

### Error: "Too many requests"

**Problem:** You're hitting YouTube's rate limiting.

**Solution:** Wait a bit before fetching more videos. There's a 1-second delay between requests built in.

```bash
# Just wait and try again
sleep 10
ytc fetch "https://youtu.be/NEXT_VIDEO_ID"
```

### Error: "Failed to open file"

**Problem:** Permission issue or disk space issue.

**Solution:** Check output directory permissions:

```bash
# Check permissions
ls -la data/output/

# Make sure you have write access
chmod 755 data/output
```

### URL Format Errors

**Problem:** `ytc fetch VIDEO_ID?t=5m30s`

**Error:** "Got unexpected extra argument"

**Solution:** Always quote URLs with special characters:

```bash
ytc fetch "https://youtu.be/VIDEO_ID?t=5m30s"  # ✓ Correct
```

---

## What Happens Next

After fetching, you can:

- **View Info:** `ytc info VIDEO_ID` - See what was downloaded
- **Browse:** `ytc list` - List all your transcribed videos
- **Open:** `ytc open VIDEO_ID` - Open transcript in Code or Finder
- **Search:** `ytc search "keyword"` - Find text in all transcripts
- **Open on YouTube:** `ytc open VIDEO_ID --youtube` - Jump to video (Phase 4.0)

---

## See Also

- [INFO.md](./INFO.md) - View details about a downloaded video
- [LIST.md](./LIST.md) - Browse your video library
- [OPEN.md](./OPEN.md) - Open files or videos
- [SEARCH.md](./SEARCH.md) - Search transcripts

---

**Shorthand:** `ytc fetch --help` shows quick reference
