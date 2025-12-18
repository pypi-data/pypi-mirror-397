# ytc extract - Extract Structured Information from Transcripts

Use Claude AI to extract books, tools, and key insights from video transcripts into searchable formats.

---

## Quick Syntax

```bash
ytc extract [VIDEO_ID] [OPTIONS]
```

**Examples:**
```bash
ytc extract VIDEO_ID --books              # Extract books/papers mentioned
ytc extract VIDEO_ID --tools              # Extract tools/software mentioned
ytc extract VIDEO_ID --key-points         # Extract key insights
ytc extract VIDEO_ID --books --tools      # Multiple extractions
ytc extract --last --key-points           # Extract from most recent video
```

---

## Description

Extract structured information from video transcripts using Claude AI. Each extraction creates dual-format output:

- **JSON** (`.json`) - Structured data for querying and automation
- **Markdown** (`.md`) - Human-readable format for immediate use

Extractions are saved to `data/output/ai-processed/VIDEO_ID/` and can be opened with `ytc open`.

**Features:**
- Extract books, papers, and articles mentioned
- Identify tools, libraries, frameworks, and software
- Capture key insights grouped by importance
- Clickable timestamp links in markdown output
- Avoids re-extraction (use `--overwrite` to regenerate)

---

## Options

### `--books`

Extract books, papers, articles, and written resources mentioned in the video.

**Output:** `books.json` + `books.md`

**Extracted fields:**
- Title and author
- Type (book, paper, article, blog_post)
- Timestamp where mentioned
- Context (why it was mentioned)

```bash
ytc extract VIDEO_ID --books
ytc open VIDEO_ID --books    # Open the extracted list
```

### `--tools`

Extract tools, software, libraries, frameworks, apps, and services mentioned.

**Output:** `tools.json` + `tools.md`

**Extracted fields:**
- Name and category (library, framework, app, service, database, etc.)
- Timestamp where mentioned
- Context (how it was used/recommended)
- URL (if mentioned)

```bash
ytc extract VIDEO_ID --tools
ytc open VIDEO_ID --tools    # Open the extracted list
```

### `--key-points`

Extract key insights, main takeaways, and important concepts from the video.

**Output:** `key_points.json` + `key_points.md`

**Extracted fields:**
- Point (the insight itself)
- Importance level (critical, important, notable)
- Timestamp where discussed
- Supporting context

```bash
ytc extract VIDEO_ID --key-points
ytc open VIDEO_ID --key-points    # Open the extracted list
```

### `--last`

Extract from the most recently fetched video (no VIDEO_ID needed).

```bash
ytc extract --last --books --tools --key-points
```

### `--overwrite`

Force re-extraction even if files already exist.

```bash
ytc extract VIDEO_ID --books                 # Shows existing if found
ytc extract VIDEO_ID --books --overwrite     # Regenerates extraction
```

---

## Examples

### Extract Tools from a Technical Video

```bash
$ ytc extract BFxSYP5IRjQ --tools

🎬 YouTube Transcript Curator > extract
==================================================
📄 Loaded transcript (19221 characters)

🛠️ Extracting Tools & Software...
🤖 Analyzing with Claude (claude-3-5-haiku-20241022)...

   Found 12 items:

   1. DPT (Document Pre-trained Transformer) (framework)
      Mentioned at: 0:14
   2. Docling (app)
      Mentioned at: 0:14
   3. Llama Parse (app)
      Mentioned at: 0:14
   4. ChromaDB (database)
      Mentioned at: 0:19
   5. Langchain (framework)
      Mentioned at: 0:19

   ... and 7 more items

✓ Saved to:
  - ./data/output/ai-processed/BFxSYP5IRjQ/tools.json
  - ./data/output/ai-processed/BFxSYP5IRjQ/tools.md
```

### Extract Key Points

```bash
$ ytc extract VIDEO_ID --key-points

💡 Extracting Key Points...
🤖 Analyzing with Claude...

   Found 14 items:

   1. [CRITICAL] Financial document extraction has a 68% error rate...
   2. [CRITICAL] DPT by Andrew Ng breaks down tables into structures...
   3. [IMPORTANT] DPT successfully identified the NVIDIA logo...
   4. [IMPORTANT] Docling is a popular open-source tool with 40k+ stars...
   5. [NOTABLE] Vision models are better for images but slower...

✓ Saved to key_points.json + key_points.md
```

### Multiple Extractions at Once

```bash
$ ytc extract VIDEO_ID --books --tools --key-points

📄 Loaded transcript (19221 characters)

📚 Extracting Books & Papers...
   No books & papers found in this video.

🛠️ Extracting Tools & Software...
   Found 12 items

💡 Extracting Key Points...
   Found 14 items

✓ Extraction complete
```

### View Extracted Data

```bash
# Open in VS Code (default)
ytc open VIDEO_ID --tools

# Open key points from most recent video
ytc open --last --key-points

# Open books extraction
ytc open VIDEO_ID --books
```

---

## Output Format

### JSON Structure

All extractions follow this structure:

```json
{
  "extracted_at": "2025-12-10T18:02:40.413245",
  "model": "claude-3-5-haiku-20241022",
  "video_id": "BFxSYP5IRjQ",
  "video_title": "Video Title",
  "count": 12,
  "items": [
    {
      "name": "Tool Name",
      "mentioned_at": "0:14",
      "timestamp_seconds": 14,
      "context": "Used for document parsing",
      "category": "framework"
    }
  ]
}
```

### Markdown Structure

```markdown
# Tools & Software Mentioned

**Video:** Video Title
**Video ID:** BFxSYP5IRjQ
**Extracted:** 2025-12-10T18:02:40
**Model:** claude-3-5-haiku-20241022

---

## 1. DPT (Document Pre-trained Transformer)

**Category:** framework
**Mentioned at:** [0:14](https://youtu.be/BFxSYP5IRjQ?t=14)

> Andrew Ng's pre-trained transformer model for document extraction.

---
```

### Key Points Grouping

Key points are automatically grouped by importance in the markdown:

```markdown
## Critical Insights
### 1. Financial document extraction has 68% error rate...

## Important Points
### 6. DPT successfully identified the NVIDIA logo...

## Notable Observations
### 10. Vision models are better but slower and more expensive...
```

---

## Use Cases

### Build a Reading List

```bash
# Extract books from multiple learning videos
ytc extract VIDEO_1 --books
ytc extract VIDEO_2 --books
ytc extract VIDEO_3 --books

# Open and compile your reading list
ytc open VIDEO_1 --books
```

### Create a Tool Comparison

```bash
# Extract tools from comparison videos
ytc extract comparison_video --tools --key-points

# Review what was discussed
ytc open comparison_video --tools
ytc open comparison_video --key-points
```

### Quick Video Notes

```bash
# Fetch and extract in one workflow
ytc fetch "https://youtu.be/VIDEO_ID"
ytc extract --last --key-points
ytc open --last --key-points
```

### Research Workflow

```bash
# After watching a video, extract everything
ytc extract VIDEO_ID --books --tools --key-points

# Get AI summary too
ytc ai VIDEO_ID --summarize --length medium

# Now you have:
# - summary_medium.md (overview)
# - books.md (reading list)
# - tools.md (software mentioned)
# - key_points.md (insights)
```

---

## Tips & Tricks

### Avoid Re-extraction

Extractions are cached. Running again shows existing data:

```bash
$ ytc extract VIDEO_ID --tools

✓ Extraction already exists:
  ./data/output/ai-processed/VIDEO_ID/tools.json

Use --overwrite to regenerate.
```

### Combine with Search

Use extracted data to find related videos:

```bash
# Extract tools from a video
ytc extract VIDEO_ID --tools

# Search your library for videos mentioning the same tools
ytc search "LangChain"
ytc search "ChromaDB"
```

### Export for Other Uses

JSON output is designed for automation:

```bash
# Use jq to query extracted data
cat data/output/ai-processed/VIDEO_ID/tools.json | jq '.items[].name'

# Get all critical key points
cat data/output/ai-processed/VIDEO_ID/key_points.json | jq '.items[] | select(.importance == "critical")'
```

---

## File Locations

Extractions are saved in:

```
data/output/ai-processed/
└── VIDEO_ID/
    ├── books.json
    ├── books.md
    ├── tools.json
    ├── tools.md
    ├── key_points.json
    ├── key_points.md
    └── summary_medium.md  (from ytc ai --summarize)
```

---

## Common Questions

### Q: What if no items are found?

**A:** Empty extractions are saved with "No items found" message. This is normal for videos that don't mention books, for example.

### Q: Can I extract from any video?

**A:** You need to fetch the video first with `ytc fetch`. Extraction requires the transcript to be in your library.

### Q: How accurate are the extractions?

**A:** Claude analyzes the transcript and extracts what's explicitly mentioned. Results are generally accurate but should be verified for critical use cases.

### Q: Can I add custom extraction types?

**A:** Currently supports books, tools, and key_points. Additional types (people, links, quotes) are planned for future releases.

---

## See Also

- [AI.md](./AI.md) - Generate AI summaries with `ytc ai`
- [OPEN.md](./OPEN.md) - Open extracted files with `ytc open`
- [FETCH.md](./FETCH.md) - Fetch videos before extraction
- [SEARCH.md](./SEARCH.md) - Search across your video library

---

**Shorthand:** `ytc extract --help` shows quick reference

**Phase:** AI Extraction (Phase 6 / v0.9.0)
