# YouTube Transcript Curator - Command Syntax Reference

Quick reference for exact command syntax.

---

## Fetch

```bash
ytc fetch <URL_OR_ID>
ytc fetch <URL_OR_ID> --overwrite
ytc fetch <URL_OR_ID> --no-timestamps
ytc fetch <URL_OR_ID> --output-dir <PATH>
```

---

## Info

```bash
ytc info <VIDEO_ID>
ytc info <URL>
```

---

## Open

### Open Local Files

```bash
ytc open <VIDEO_ID>                    # Transcript in Code (default)
ytc open <VIDEO_ID> --meta             # Metadata in Code
ytc open <VIDEO_ID> --finder           # Transcript in Finder
ytc open <VIDEO_ID> --meta --finder    # Metadata in Finder
```

### Open on YouTube

```bash
ytc open <VIDEO_ID> --youtube                    # At start
ytc open <VIDEO_ID> --youtube --time MM:SS       # MM:SS format
ytc open <VIDEO_ID> --youtube --time HH:MM:SS   # HH:MM:SS format
ytc open <VIDEO_ID> --youtube --time SECONDS     # Seconds only
ytc open <VIDEO_ID> --youtube --time NmNs        # Human readable
```

**Examples:**
```bash
ytc open IdPtTBbYOtw --youtube --time 5:45       # 5 minutes 45 seconds
ytc open IdPtTBbYOtw --youtube --time 345        # 345 seconds
ytc open IdPtTBbYOtw --youtube --time 5m45s      # 5 minutes 45 seconds
ytc open IdPtTBbYOtw --youtube --time 1:30:45    # 1 hour 30 min 45 sec
```

---

## List

```bash
ytc list                                 # All videos, compact
ytc list --format compact               # Compact (default)
ytc list --format full                  # Full details
ytc list --format ids                   # Just video IDs
ytc list --format json                  # JSON output

ytc list --type <TYPE>                  # Filter by type
ytc list --type regular                 # Regular videos
ytc list --type live                    # Livestream videos
ytc list --type rec                     # Livestream recordings

ytc list --channel "<CHANNEL>"          # Filter by channel
ytc list --channel "VS Code"            # Exact match (case-insensitive)

ytc list --sort <FIELD>                 # Sort by field
ytc list --sort date                    # By date (default)
ytc list --sort title                   # By title
ytc list --sort channel                 # By channel
ytc list --sort duration                # By duration

ytc list --reverse                      # Reverse sort order
ytc list --limit <N>                    # Show only first N
ytc list --limit 5                      # Show 5 videos
```

**Combined Examples:**
```bash
ytc list --type regular --sort title --limit 10
ytc list --channel "VS Code" --type live --reverse
ytc list --type rec --limit 3 --format full
```

---

## Search

```bash
ytc search "<KEYWORD>"                  # Search all transcripts
ytc search "<KEYWORD>" --context <N>    # With N lines of context
ytc search "<KEYWORD>" --count          # Only show counts
ytc search "<KEYWORD>" --json           # JSON output
```

**Examples:**
```bash
ytc search "python"
ytc search "neural network" --context 2
ytc search "authentication" --count
ytc search "JWT" --json
```

---

## Stats

```bash
ytc stats                               # Show library statistics
```

No options for stats.

---

## Help

```bash
ytc help                                # Show overall help
ytc help <COMMAND>                      # Show specific command help
ytc help fetch
ytc help open
ytc help list
ytc help search
ytc help stats
ytc help info
```

---

## Aliases (Terminal)

```bash
yt-cd                                  # Jump to project directory
yt-output                              # Open data/output in Finder
```

---

## Important Notes

### Always Quote URLs

```bash
ytc fetch "https://youtu.be/VIDEO_ID?t=123"     # ✓ Correct
ytc fetch https://youtu.be/VIDEO_ID?t=123       # ✗ May fail
```

### --time Format Examples

All of these jump to 90 seconds:

```bash
ytc open VIDEO_ID --youtube --time 1:30         # MM:SS
ytc open VIDEO_ID --youtube --time 90           # Seconds
ytc open VIDEO_ID --youtube --time 90s          # Seconds (explicit)
ytc open VIDEO_ID --youtube --time 1m30s        # Minutes + seconds
```

### Fuzzy Type Matching

These all work:

```bash
ytc list --type regular
ytc list --type reg
ytc list --type regular

ytc list --type livestream_recording
ytc list --type rec
ytc list --type livestream_recording
ytc list --type recording

ytc list --type live              # Matches any livestream type
ytc list --type ls               # Shortcut for livestream
```

---

## Common Mistakes

❌ Missing `--time` flag:
```bash
ytc open VIDEO_ID --youtube 5:45        # WRONG
```

✅ Correct:
```bash
ytc open VIDEO_ID --youtube --time 5:45
```

---

❌ Unquoted URL with special characters:
```bash
ytc fetch https://youtu.be/VIDEO?t=123    # WRONG
```

✅ Correct:
```bash
ytc fetch "https://youtu.be/VIDEO?t=123"
```

---

❌ Wrong timestamp separator:
```bash
ytc open VIDEO_ID --youtube --time 5.45   # WRONG (period)
```

✅ Correct:
```bash
ytc open VIDEO_ID --youtube --time 5:45   # Colon
```

---

For more details, see [docs/usage/](./usage/)
