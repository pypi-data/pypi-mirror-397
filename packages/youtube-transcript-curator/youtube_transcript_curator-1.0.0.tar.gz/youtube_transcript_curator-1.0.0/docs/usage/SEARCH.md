# ytc search - Search Across Transcripts

Find keywords across all your transcribed videos.

---

## Quick Syntax

```bash
ytc search "<KEYWORD>"
```

**Examples:**
```bash
ytc search "python"
ytc search "neural network" --context 2
ytc search "authentication" --count
```

---

## Description

Searches all transcript files in your library for a keyword and shows matching lines with context.

---

## Options

### `--context`

Show N lines before and after each match for context.

**Default:** 0 (show only the matching line)

```bash
ytc search "python"                  # Show only matching lines
ytc search "python" --context 1      # Show 1 line before/after
ytc search "python" --context 2      # Show 2 lines before/after
ytc search "python" --context 5      # Show 5 lines before/after
```

### `--count`

Show only the number of matches per video, not the actual matches.

**Default:** false (show all matches)

```bash
ytc search "python"              # Show all matching lines
ytc search "python" --count      # Show only match counts
```

### `--json`

Output results as JSON for programmatic use.

**Default:** false (human-readable format)

```bash
ytc search "python"              # Human readable
ytc search "python" --json       # JSON format
```

---

## Examples

### Basic: Search for Keyword

```bash
$ ytc search "authentication"

🎥 IdPtTBbYOtw - VS Code Live - v1.106 Release
   [00:45] Let's discuss authentication mechanisms...
   [05:30] Authentication is critical for security...
   [12:15] Different authentication methods...

🎥 S0dwRNwI050 - Monitor Your Robots from the Web
   [03:20] For authentication, use API keys...
```

### Search with Context

```bash
$ ytc search "JWT" --context 1

🎥 IdPtTBbYOtw - VS Code Live - v1.106 Release
   [03:15] Traditional sessions are stateless.
   [03:45] JWT tokens provide a better approach.  <-- MATCH
   [04:00] JWTs contain encoded information.
```

### Count Matches Only

```bash
$ ytc search "database" --count

🎥 S0dwRNwI050 - Monitor Your Robots
   3 matches

🎥 COKyFP_VNAs - How to create Web Dashboards
   5 matches

🎥 dQw4w9WgXcQ - Tech Talks Weekly
   0 matches
```

### JSON Output

```bash
$ ytc search "python" --json
{
  "IdPtTBbYOtw": {
    "title": "VS Code Live - v1.106 Release",
    "channel": "Visual Studio Code",
    "matches": [
      {
        "line_number": 45,
        "text": "[00:45] Python is a great language...",
        "context": []
      }
    ],
    "match_count": 1
  }
}
```

---

## Use Cases

### Research a Topic

```bash
# Find all mentions of machine learning
ytc search "machine learning" --context 2

# See how many videos discuss it
ytc search "machine learning" --count
```

### Find Related Videos

```bash
# Search for a concept
ytc search "REST API"

# Output shows which videos discuss it
# Use ytc open on those videos
ytc open IdPtTBbYOtw  # Open transcript
ytc open IdPtTBbYOtw --youtube  # Open on YouTube
```

### Quick Reference Finding

```bash
# Remember something was discussed but not the video?
ytc search "Kubernetes deployment"

# Find it quickly, then jump to the section
ytc open VIDEO_ID --youtube --time TIMESTAMP
```

### Batch Processing Results

```bash
# Get JSON of all JWT mentions
ytc search "JWT" --json > jwt_mentions.json

# Process with jq or other tools
cat jwt_mentions.json | jq '.[] | .matches | length'
```

---

## Search Tips

### Case-Insensitive

```bash
ytc search "Python"      # Finds "python", "PYTHON", etc.
ytc search "JWT"         # Finds "jwt", "Jwt", etc.
```

### Phrase Matching

```bash
ytc search "machine learning"        # Finds this exact phrase
ytc search "machine"                 # Also finds "machine learning"
```

### Special Characters

```bash
ytc search "async/await"             # Works fine
ytc search "C++"                     # Works fine
ytc search "100%"                    # Works fine
```

---

## Common Issues

### No matches found

**Problem:** `ytc search "keyword"` returns no results

**Solution 1:** Check spelling
```bash
ytc search "neural network"    # Correct spelling
ytc search "neural netowrk"    # Typo - no results
```

**Solution 2:** Try related terms
```bash
ytc search "TensorFlow"        # Try specific framework
ytc search "deep learning"     # Try broader term
```

**Solution 3:** Search might be too specific
```bash
# No results for exact phrase
ytc search "JWT token implementation"

# Try shorter phrase
ytc search "JWT"
```

### Too Many Results

**Problem:** `ytc search "the"` returns thousands of matches

**Solution:** Make search more specific
```bash
ytc search "the"              # Too broad - avoid
ytc search "The Construct"    # More specific
ytc search "REST API"         # More specific
```

### Use Context to Understand

```bash
# See surrounding lines to understand context
ytc search "database" --context 3

# Then open the full transcript if needed
ytc open VIDEO_ID
```

---

## Exporting Results

### Save to File

```bash
# Save human-readable results
ytc search "python" > python_mentions.txt

# Save as JSON
ytc search "python" --json > python_mentions.json
```

### Filter Results

```bash
# Count total mentions across all videos
ytc search "API" --count | grep matches | wc -l

# Find videos with the most mentions
ytc search "authentication" --count | sort -t: -k3 -rn | head -5
```

---

## See Also

- [LIST.md](./LIST.md) - Browse your library
- [OPEN.md](./OPEN.md) - Open videos or transcripts
- [FETCH.md](./FETCH.md) - Download transcripts

---

**Shorthand:** `ytc search --help` shows quick reference
