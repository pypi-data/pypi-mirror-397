# ytc delete - Remove Videos from Your Library

Safely delete videos from your transcribed library with confirmation prompts.

---

## Quick Syntax

```bash
ytc delete [VIDEO_ID_OR_URL] [OPTIONS]
```

**Examples:**
```bash
ytc delete IdPtTBbYOtw                  # Delete with confirmation
ytc delete --last                       # Delete most recent video
ytc delete IdPtTBbYOtw --force          # Delete without confirmation
ytc delete "https://youtu.be/IdPtTBbYOtw"
```

---

## Description

Permanently removes a video and all its associated files from your library:

- Metadata JSON file
- Transcript text file
- Formatted file (if exists)

The command shows you exactly what will be deleted and asks for confirmation before proceeding (unless you use `--force`).

---

## Options

### `--last`

Delete the most recently fetched video (no VIDEO_ID needed).

**Default:** false (requires VIDEO_ID)

```bash
ytc delete --last                # Delete most recent with confirmation
ytc delete --last --force        # Delete most recent without confirmation
```

### `--force`

Skip the confirmation prompt and delete immediately. Use with caution!

**Default:** false (show confirmation)

```bash
# With confirmation (default)
ytc delete VIDEO_ID

# Without confirmation
ytc delete VIDEO_ID --force
```

**⚠️ Warning:** This cannot be undone. Use `--force` carefully!

---

## URL Formats Supported

All of these work:

```bash
# Just the video ID (11 characters)
ytc delete IdPtTBbYOtw

# Short URL
ytc delete "https://youtu.be/IdPtTBbYOtw"

# Full URL
ytc delete "https://www.youtube.com/watch?v=IdPtTBbYOtw"

# With timestamps (timestamps are ignored)
ytc delete "https://youtu.be/IdPtTBbYOtw?t=5m30s"
```

**⚠️ Important:** Always quote URLs with special characters:

```bash
ytc delete "https://youtu.be/VIDEO?t=123&si=abc"    # ✓ Correct
ytc delete https://youtu.be/VIDEO?t=123&si=abc      # ✗ Will fail!
```

---

## Examples

### Quick Access: Delete Most Recent

```bash
$ ytc delete --last

🎬 YouTube Transcript Curator > delete
==================================================
📺 Most recent: VS Code Live - v1.106 Release
   Video ID: IdPtTBbYOtw

🗑️  Video to Delete: IdPtTBbYOtw
==================================================
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code

📁 Files to Delete:
   • metadata: metadata_IdPtTBbYOtw.json (0.05 MB)
   • transcript: youtube_IdPtTBbYOtw.txt (1.23 MB)

⚠️  This cannot be undone!
Are you sure you want to delete these files? [y/N]: y

✓ Successfully deleted IdPtTBbYOtw
```

Quickly delete your most recent video without needing to remember the ID.

### Basic: Delete with Confirmation

```bash
$ ytc delete IdPtTBbYOtw

🗑️  Video to Delete: IdPtTBbYOtw
==================================================
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code

📁 Files to Delete:
   • metadata: metadata_IdPtTBbYOtw.json (0.05 MB)
   • transcript: youtube_IdPtTBbYOtw.txt (1.23 MB)

⚠️  This cannot be undone!
Are you sure you want to delete these files? [y/N]: y

✓ Successfully deleted 2 file(s)
✓ Removed from library
```

### Using URL Input

```bash
$ ytc delete "https://youtu.be/IdPtTBbYOtw"

🗑️  Video to Delete: IdPtTBbYOtw
==================================================
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code

📁 Files to Delete:
   • metadata: metadata_IdPtTBbYOtw.json (0.05 MB)
   • transcript: youtube_IdPtTBbYOtw.txt (1.23 MB)

⚠️  This cannot be undone!
Are you sure you want to delete these files? [y/N]: y

✓ Successfully deleted 2 file(s)
✓ Removed from library
```

### Force Delete (No Confirmation)

```bash
$ ytc delete IdPtTBbYOtw --force

🗑️  Video to Delete: IdPtTBbYOtw
==================================================
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code

📁 Files to Delete:
   • metadata: metadata_IdPtTBbYOtw.json (0.05 MB)
   • transcript: youtube_IdPtTBbYOtw.txt (1.23 MB)

✓ Successfully deleted 2 file(s)
✓ Removed from library
```

### Decline Deletion

```bash
$ ytc delete IdPtTBbYOtw

🗑️  Video to Delete: IdPtTBbYOtw
==================================================
   Title: VS Code Live - v1.106 Release
   Channel: Visual Studio Code

📁 Files to Delete:
   • metadata: metadata_IdPtTBbYOtw.json (0.05 MB)
   • transcript: youtube_IdPtTBbYOtw.txt (1.23 MB)

⚠️  This cannot be undone!
Are you sure you want to delete these files? [y/N]: n

❌ Deletion cancelled
```

### Video Not Found

```bash
$ ytc delete unknown123456789

❌ No files found for video: unknown123456789
```

---

## What Gets Deleted

The delete command removes the following files:

| File Type | Example | Purpose |
|-----------|---------|---------|
| Metadata | `metadata_VIDEO_ID.json` | Video info (title, channel, duration, etc.) |
| Transcript | `youtube_VIDEO_ID.txt` | Full transcript with timestamps |
| Formatted | `formatted_VIDEO_ID.md` | Optional formatted version (if exists) |

**Location:** All files are stored in `data/output/` subdirectories.

---

## Use Cases

### Clean Up Library

```bash
# Delete videos you no longer need
ytc delete OLD_VIDEO_ID_1
ytc delete OLD_VIDEO_ID_2

# Or with --force for batch cleanup
ytc delete OLD_VIDEO_ID_1 --force
```

### Remove Accidental Duplicates

```bash
# If you transcribed the same video twice
ytc list --format ids | grep VIDEO_ID

# Delete the duplicate
ytc delete VIDEO_ID
```

### Archive Old Videos

```bash
# Before archiving, delete from local library
ytc delete VIDEO_ID

# Now you can move archived transcripts to backup storage
```

### Free Up Disk Space

```bash
# Check library size
ytc stats

# Delete large videos you no longer reference
ytc delete LARGE_VIDEO_ID
```

---

## Tips & Tricks

### Check Before Deleting

```bash
# View video details first
ytc info VIDEO_ID

# Then delete if sure
ytc delete VIDEO_ID
```

### List Videos Before Bulk Deletion

```bash
# See all videos from a channel
ytc list --channel "VS Code"

# Delete one you don't need
ytc delete VIDEO_ID
```

### Safe Workflow

```bash
# 1. Search for references before deleting
ytc search "keyword from video"

# 2. Check the video info
ytc info VIDEO_ID

# 3. Confirm you want to delete (no --force)
ytc delete VIDEO_ID

# 4. Review the files one last time before confirming
# 5. Answer 'y' only if sure
```

### Re-download After Deletion

```bash
# If you delete by accident, you can re-fetch
ytc delete VIDEO_ID

# Later: re-download if needed
ytc fetch "https://youtu.be/VIDEO_ID"
```

---

## Common Issues

### Error: "No files found for video"

**Problem:** `ytc delete VIDEO_ID` says files not found

**Reason:** The video hasn't been transcribed yet or was already deleted

**Solution:** Check if the video exists first:

```bash
ytc info VIDEO_ID       # See if files exist
ytc list                # Browse available videos
```

### Error: "Invalid YouTube URL or video ID"

**Problem:** `ytc delete "not-a-valid-id"`

**Solution:** Use a valid video ID or URL:

```bash
# Valid video IDs are 11 characters
ytc delete IdPtTBbYOtw         # ✓ Correct

# Valid URLs
ytc delete "https://youtu.be/IdPtTBbYOtw"                    # ✓ Correct
ytc delete "https://www.youtube.com/watch?v=IdPtTBbYOtw"     # ✓ Correct

# Invalid formats
ytc delete my-video            # ✗ Too short
ytc delete "Random Title"      # ✗ Not an ID or URL
```

### Accidentally Used --force

**Problem:** You deleted with `--force` and didn't mean to

**Solution:** Re-download the transcript:

```bash
# The files are permanently deleted, but you can re-fetch
ytc fetch "https://youtu.be/VIDEO_ID"
```

The transcribed data will be re-downloaded from YouTube (note: requires the video to still have captions available).

### Permission Denied Error

**Problem:** `ytc delete VIDEO_ID` returns permission error

**Reason:** The `data/output/` directory or files don't have write permissions

**Solution:** Check file permissions:

```bash
# Check output directory permissions
ls -la data/output/metadata/
ls -la data/output/transcripts/

# Fix permissions if needed
chmod 755 data/output/
```

---

## Safety Features

### Confirmation Prompt (Default)

By default, the delete command shows you:
- Video title and channel
- Exact files that will be deleted
- File sizes
- A confirmation prompt before deletion

This prevents accidental deletions.

### --force Flag (Use Carefully)

The `--force` flag skips confirmation for automation but:
- Still shows what will be deleted
- Still verifies files exist
- Still removes from library
- Cannot be undone

Use only when you're certain you want to delete.

---

## Recovery

### If Deleted by Accident

Unfortunately, **deleted files cannot be recovered** from the local system. However:

1. **Re-download:** The transcript data still exists on YouTube (if available)
   ```bash
   ytc fetch "https://youtu.be/VIDEO_ID"
   ```

2. **Backup:** If you have backups of `data/output/`, restore from there

3. **Cloud Backups:** If you synced the `data/output/` folder to cloud storage (Dropbox, Google Drive), you might recover from there

### Prevention for Future

Consider:
- Regularly backing up `data/output/` directory
- Using `--force` sparingly (rely on confirmation prompts)
- Testing deletion with `ytc info` and `ytc list` first

---

## Deletion Cannot Be Undone

**Important:** This operation permanently deletes files. They cannot be recovered from the Trash or Recycle Bin.

Before using `--force`, always:
1. Verify the video ID with `ytc info`
2. Understand what you're deleting
3. Consider if you might need it later
4. Have backups if you need archival

---

## See Also

- [LIST.md](./LIST.md) - Browse your library before deleting
- [INFO.md](./INFO.md) - Check video details first
- [SEARCH.md](./SEARCH.md) - Find references to videos
- [FETCH.md](./FETCH.md) - Re-download if needed

---

**Shorthand:** `ytc delete --help` shows quick reference
