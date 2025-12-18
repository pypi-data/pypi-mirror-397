# ytc history - View Library Change History

Track all fetches and deletions in your transcript library.

---

## Quick Syntax

```bash
ytc history [OPTIONS]
```

**Examples:**
```bash
ytc history                    # Show recent activity
ytc history --action fetch     # Only show fetches
ytc history --action delete    # Only show deletions
ytc history --limit 50         # Show more entries
```

---

## Description

Shows a chronological log of all library changes, including when videos were fetched and deleted.

### What Gets Logged

1. **Fetch Operations**
   - Video ID and title
   - When it was fetched
   - Source URL

2. **Delete Operations**
   - Video ID and title
   - When it was deleted
   - Any backup information

---

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--action` | Choice | `all` | Filter by action type: `all`, `fetch`, `delete` |
| `--limit` | Integer | `20` | Number of entries to show |

---

## Usage Examples

### View All Recent Activity

```bash
$ ytc history

📋 Library History
==================================================

Recent Activity (showing last 20 entries):

2025-12-10 14:32:15 [FETCH] BFxSYP5IRjQ
   Title: I Tested 5 Document Parsers for AI Agents

2025-12-10 12:15:08 [FETCH] IdPtTBbYOtw
   Title: VS Code Live - v1.106 Release

2025-12-09 16:45:22 [DELETE] abc123xyz
   Title: Old Tutorial Video
```

### View Only Fetches

```bash
$ ytc history --action fetch

📋 Library History (fetch only)
==================================================

Recent Fetches (showing last 20 entries):

2025-12-10 14:32:15 [FETCH] BFxSYP5IRjQ
   Title: I Tested 5 Document Parsers for AI Agents

2025-12-10 12:15:08 [FETCH] IdPtTBbYOtw
   Title: VS Code Live - v1.106 Release
```

### View More History

```bash
$ ytc history --limit 50
```

---

## Where History Is Stored

The history log is stored in:

```
data/output/logs/library_changes.log
```

This file is automatically maintained by YTC. Each entry is timestamped and includes the operation type, video ID, and relevant metadata.

---

## Use Cases

### Recovery After Accidental Deletion

Check what was deleted and when:

```bash
ytc history --action delete
```

Then re-fetch if needed:

```bash
ytc fetch VIDEO_ID
```

### Track Processing Progress

See how many videos you've processed recently:

```bash
ytc history --action fetch --limit 100
```

### Audit Trail

The history provides a complete audit trail of all library operations for documentation or compliance purposes.

---

## Related Commands

| Command | Description |
|---------|-------------|
| `ytc list` | Browse your current library |
| `ytc delete` | Remove videos from library |
| `ytc stats` | View library statistics |

---

## See Also

- [DELETE.md](./DELETE.md) - How to remove videos
- [STATS.md](./STATS.md) - Library statistics
- [OVERVIEW.md](./OVERVIEW.md) - All commands reference
