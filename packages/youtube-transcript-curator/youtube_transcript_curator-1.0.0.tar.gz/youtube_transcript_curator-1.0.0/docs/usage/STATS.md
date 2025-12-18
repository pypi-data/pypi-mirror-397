# ytc stats - Library Statistics

View overview statistics about your transcribed video library.

---

## Quick Syntax

```bash
ytc stats
```

No options or arguments needed.

---

## Description

Shows statistics about your entire library of transcribed videos:

- Total number of videos transcribed
- Total duration of all videos combined
- Breakdown by video type (regular, livestream, etc.)
- Breakdown by channel
- Most active channels

This is useful for understanding the size and composition of your library at a glance.

---

## Example

```bash
$ ytc stats

📊 Library Statistics
═══════════════════════════════════════════════════════════════════════════

📈 Overview
   Total Videos:       42
   Total Duration:     3 days, 5 hours, 47 minutes

📂 By Type
   Regular:            35 videos (87%)
   Livestream:         4 videos (10%)
   Livestream Rec:     3 videos (7%)

🎬 Top Channels
   Visual Studio Code:           8 videos
   JavaScript Pro:               6 videos
   React Tutorial Channel:        5 videos
   Python Deep Dive:             4 videos
   Web Dev Simplified:            3 videos
   (24 other channels)
```

---

## Understanding the Output

### Overview Section

**Total Videos:** Count of all transcribed videos in your library

**Total Duration:** Sum of all video durations combined

Example:
```
Total Videos:       42
Total Duration:     3 days, 5 hours, 47 minutes
```

This means you've transcribed 42 videos with a combined watching time of ~3.25 days.

### By Type Section

Shows breakdown of videos by category:

```
Regular:            35 videos (87%)      ← Standard YouTube videos
Livestream:         4 videos (10%)       ← Live broadcasts
Livestream Rec:     3 videos (7%)        ← Recordings of streams
```

Percentages add up to more than 100% because some videos might have multiple type tags.

### Top Channels Section

Shows the channels with the most videos in your library:

```
Visual Studio Code:           8 videos
JavaScript Pro:               6 videos
React Tutorial Channel:        5 videos
```

Useful for understanding which content creators you watch most frequently.

---

## Use Cases

### Understand Your Learning Library

```bash
# See what you've been watching
ytc stats

# How many videos? How much content?
# Which channels do you follow most?
```

### Plan Download Strategy

```bash
# Check if library is growing too large
ytc stats

# See total duration
# Decide if you need to archive old transcripts
```

### Find Your Most-Used Resources

```bash
# See top channels
ytc stats

# Use this info to:
# - Focus on channels with most content
# - Plan what to watch next from top channels
# - Identify which creators you rely on most
```

### Library Health Check

```bash
# Periodically run to see library growth
ytc stats    # See total count and duration
ytc list     # See all videos if interested
```

---

## Tips & Tricks

### Combining with Other Commands

```bash
# Get stats, then explore a top channel
ytc stats

# See "Visual Studio Code" has 8 videos?
# List all from that channel:
ytc list --channel "Visual Studio Code"
```

### Tracking Library Growth

```bash
# Useful to check periodically
# How much content are you accumulating?

ytc stats      # Check total duration
# Keep mental note or save to file
```

### Finding Content Gaps

```bash
# Run stats to see which channels you have
ytc stats

# If you have many videos from one channel,
# you're probably familiar with their content

# Good for deciding what new channels to explore
```

---

## Common Questions

### What's the Difference Between "Livestream" and "Livestream Rec"?

- **Livestream:** The broadcast type (live-recorded event)
- **Livestream Rec:** Manually recorded or archived livestream

Both are essentially the same - livestream content. The distinction helps with organization if you have many livestreams.

### Why Do Percentages Add Up to More Than 100%?

Videos can have multiple type tags, so percentages reflect the presence of each tag, not exclusive categories.

```
Regular:     35 videos (might be 87%)
Livestream:  4 videos (might be 10%)
────────────────────────────
Could total more than 100% if videos tagged with multiple types
```

### Does "Total Duration" Include Timestamps?

No. Total duration is the actual video length, not affected by the `--no-timestamps` option when fetching. If you downloaded a 1-hour video, it counts as 1 hour regardless of timestamp formatting.

### What if Stats Show 0 Videos?

You haven't transcribed any videos yet. Start with:

```bash
ytc fetch "https://youtu.be/VIDEO_ID"
```

Then run stats again to see your first video appear.

---

## Exporting Stats

### Save to File

```bash
# Capture the output
ytc stats > library_stats.txt

# Review later
cat library_stats.txt
```

### Combine with List for Detailed Report

```bash
# Get stats overview
ytc stats

# Then get detailed list in JSON
ytc list --format json > all_videos.json

# Now you have both overview and details
```

---

## See Also

- [LIST.md](./LIST.md) - Browse and filter your library
- [SEARCH.md](./SEARCH.md) - Find keywords across videos
- [FETCH.md](./FETCH.md) - Download more transcripts

---

**Shorthand:** `ytc stats --help` shows quick reference
