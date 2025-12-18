# ytc ai - AI-Powered Transcript Analysis

Use Claude AI to analyze, summarize, and ask questions about your video transcripts.

---

## Quick Syntax

```bash
ytc ai [VIDEO_ID] [OPTIONS]
```

**Examples:**
```bash
ytc ai VIDEO_ID --summarize                    # Get AI summary
ytc ai VIDEO_ID --summarize --length short     # Short summary
ytc ai VIDEO_ID --prompt "What are key points?" # Custom question
ytc ai --last --summarize                      # Summarize most recent
```

---

## Description

Leverage Claude AI to extract insights from your video transcripts. Ask questions, generate summaries, extract key concepts, and more—all without leaving the terminal.

**Features:**
- Generate automatic summaries of any length
- Ask custom questions about video content
- Extract key concepts and topics
- Works with your most recent video with `--last`
- Powered by Claude AI for intelligent analysis

---

## Options

### `--summarize`

Generate an AI summary of the video transcript.

**Default:** false (no summary generated)

**Tip:** Combine with `--length` to control summary size

```bash
ytc ai VIDEO_ID --summarize              # Generate summary
ytc ai VIDEO_ID --summarize --length medium   # Medium length
```

### `--length [short|medium|long]`

Control the length of AI-generated summaries.

**Options:**
- `short` - Key points only (2-3 sentences)
- `medium` - Balanced summary (1 paragraph, ~150 words)
- `long` - Detailed summary (2-3 paragraphs, ~500 words)

**Default:** `medium` (when --summarize used)

```bash
ytc ai VIDEO_ID --summarize --length short     # Quick summary
ytc ai VIDEO_ID --summarize --length long      # Detailed summary
```

### `--prompt TEXT`

Ask Claude a custom question or give an instruction about the transcript.

**Default:** false (no custom prompt)

```bash
ytc ai VIDEO_ID --prompt "What are the main topics?"
ytc ai VIDEO_ID --prompt "Explain the authentication flow discussed"
ytc ai VIDEO_ID --prompt "List all code examples mentioned"
```

### `--last`

Analyze the most recently fetched video (no VIDEO_ID needed).

**Default:** false (requires VIDEO_ID)

```bash
ytc ai --last --summarize              # Summarize most recent video
ytc ai --last --prompt "Summarize the key points"
```

---

## Examples

### Generate a Summary

```bash
$ ytc ai dQw4w9WgXcQ --summarize

🎬 YouTube Transcript Curator > ai
==================================================

🤖 Claude is analyzing your transcript...

📝 Summary:
This video discusses modern web development practices and frameworks.
The presenter covers React fundamentals, state management with Redux,
and best practices for building scalable applications. Key topics include
component composition, hooks, and testing strategies for production systems.
```

### Summary with Specific Length

#### Short Summary

```bash
$ ytc ai VIDEO_ID --summarize --length short

📝 Short Summary:
Modern web development with React, Redux, and testing best practices.
```

#### Long Summary

```bash
$ ytc ai VIDEO_ID --summarize --length long

📝 Detailed Summary:
This comprehensive video explores modern React development patterns.
The presenter begins with fundamental concepts including components,
JSX syntax, and the virtual DOM. They then dive into state management
using Redux, demonstrating how to structure stores, actions, and reducers.

The video covers advanced topics such as custom hooks for code reuse,
middleware for async operations, and error handling patterns. Best practices
for performance optimization include memoization with useMemo and useCallback,
and lazy loading components. The presenter emphasizes testing strategies,
including unit tests with Jest, component tests with React Testing Library,
and integration tests for complete workflows.

Finally, the video discusses deployment considerations, environment
configuration, and monitoring production React applications with error
tracking and performance metrics.
```

### Ask a Custom Question

```bash
$ ytc ai VIDEO_ID --prompt "What code examples are shown in this video?"

🤖 Claude is analyzing your transcript...

💬 Response:
The video demonstrates several code examples:

1. React Component with Hooks:
   - useState for managing component state
   - useEffect for side effects and lifecycle
   - Custom hooks for reusable logic

2. Redux Setup:
   - Creating a Redux store with createStore()
   - Defining actions and action creators
   - Writing reducers to update state

3. Testing Examples:
   - Jest test setup and assertions
   - React Testing Library component rendering
   - User interaction simulation with userEvent

4. API Integration:
   - Fetching data with useEffect
   - Error handling and loading states
   - Caching strategies with Redux
```

### Analyze Your Most Recent Video

```bash
$ ytc ai --last --summarize

🎬 YouTube Transcript Curator > ai
==================================================
📺 Most recent: JavaScript Promises and Async/Await
   Video ID: 9-Jl0dxWQs8

🤖 Claude is analyzing your transcript...

📝 Summary:
This video covers asynchronous JavaScript programming. It explains Promises
as objects representing eventual completion of async operations, with .then()
and .catch() methods for handling results. The presenter demonstrates how
async/await syntax provides cleaner handling of async code, avoiding "callback
hell" and making asynchronous code look synchronous. Examples include API calls,
file operations, and error handling with try/catch blocks.
```

### Complex Questions

```bash
$ ytc ai VIDEO_ID --prompt "Compare this approach to the alternative methods discussed"

💬 Response:
The video compares three approaches to async JavaScript:

1. Callbacks: Traditional but leads to deeply nested code
2. Promises: Better error handling with .then() and .catch()
3. Async/Await: Clearest syntax, treats async as sequential code

The presenter recommends async/await as the modern standard for new code.
```

---

## Use Cases

### Quick Learning Review

```bash
# Fetch a new technical video
ytc fetch "https://youtu.be/VIDEO_ID"

# Get a quick summary
ytc ai --last --summarize --length short

# Ask follow-up questions
ytc ai VIDEO_ID --prompt "What are the prerequisites for this topic?"
```

### Research and Documentation

```bash
# Summarize multiple videos
ytc fetch "https://youtu.be/VIDEO_1"
ytc ai --last --summarize --length long > summary_1.txt

ytc fetch "https://youtu.be/VIDEO_2"
ytc ai --last --summarize --length long > summary_2.txt

# Compare summaries manually or with AI
```

### Concept Extraction

```bash
# Get key technical concepts from a video
ytc ai VIDEO_ID --prompt "List all technical concepts, libraries, and frameworks mentioned"

# Extract code patterns
ytc ai VIDEO_ID --prompt "What are the main design patterns shown in code examples?"

# Find prerequisites
ytc ai VIDEO_ID --prompt "What prior knowledge is needed to understand this content?"
```

### Content Organization

```bash
# Categorize video content
ytc ai VIDEO_ID --prompt "What category best describes this video? (e.g., tutorial, reference, opinion)"

# Extract main takeaways
ytc ai VIDEO_ID --prompt "What are the 3-5 most important takeaways from this video?"

# Identify target audience
ytc ai VIDEO_ID --prompt "Who is the intended audience for this content?"
```

---

## Tips & Tricks

### Summary Length Comparison

Different length options work best for different purposes:

```bash
# For quick note-taking during meetings
ytc ai VIDEO_ID --summarize --length short

# For general understanding and library notes
ytc ai VIDEO_ID --summarize --length medium

# For comprehensive documentation or teaching others
ytc ai VIDEO_ID --summarize --length long
```

### Effective Question Phrasing

Ask specific questions to get better answers:

```bash
# Good: Specific and focused
ytc ai VIDEO_ID --prompt "What authentication methods are compared?"

# Less helpful: Too vague
ytc ai VIDEO_ID --prompt "Tell me about the video"

# Good: Clear objective
ytc ai VIDEO_ID --prompt "Extract all shell commands shown in the terminal"

# Less helpful: Unclear
ytc ai VIDEO_ID --prompt "What commands?"
```

### Combining with Other Commands

```bash
# Get summary AND the transcript for reference
ytc ai VIDEO_ID --summarize
ytc open VIDEO_ID  # Keep transcript open in Code

# Search for specific topics after summary
ytc search "specific topic mentioned in summary"

# Compare summaries of related videos
ytc search "topic"  # Find related videos
ytc ai VIDEO_ID_1 --summarize --length medium > topic_v1.txt
ytc ai VIDEO_ID_2 --summarize --length medium > topic_v2.txt
```

### Creating Study Materials

```bash
# Generate summary
ytc ai VIDEO_ID --summarize --length long > study_guide.txt

# Extract key points
ytc ai VIDEO_ID --prompt "Create a bullet-point outline of key topics" >> study_guide.txt

# Get example code
ytc ai VIDEO_ID --prompt "Extract all code examples with explanations" >> study_guide.txt

# Identify practice questions
ytc ai VIDEO_ID --prompt "Generate 5 practice questions to test understanding" >> study_guide.txt
```

---

## Understanding Claude's Analysis

### Accuracy and Limitations

Claude analyzes the full transcript and provides:
- **Accurate:** Direct information from the video content
- **Intelligent:** Synthesizes information and finds connections
- **Contextual:** Understands technical and domain-specific content

However:
- Claude summarizes what's in the transcript (not the video visuals)
- Visual demonstrations aren't analyzed (only discussed in audio)
- Some nuance may be lost with very long transcripts

### Best Practices

```bash
# For technical content, be specific
ytc ai VIDEO_ID --prompt "List all npm packages mentioned with their purposes"

# For educational content, ask for structure
ytc ai VIDEO_ID --prompt "Create an outline showing learning progression"

# For reference material, extract what matters
ytc ai VIDEO_ID --prompt "Extract code snippets with line-by-line explanations"
```

---

## Common Questions

### Q: What model does this use?

**A:** YouTube Transcript Curator uses **Claude 3.5 Haiku** via the local Claude CLI. This provides:
- Fast analysis (perfect for transcripts)
- No API costs (uses your Pro/Max subscription)
- Privacy (processes locally on your machine)

### Q: Will this work without the Claude CLI?

**A:** You need either:
1. **Claude Pro or Max subscription** with `claude` command installed
2. Or configure API key in `.env` (requires Anthropic API credits)

To install Claude CLI, see [Claude's documentation](https://claude.ai/download)

### Q: How long does analysis take?

**A:** Typically 5-30 seconds depending on:
- Transcript length (long transcripts = more processing)
- Complexity of your question
- Your system's performance

### Q: Can I use this for commercial purposes?

**A:** Check Claude's terms of service regarding your use case. Personal analysis is permitted. For commercial applications, review Anthropic's usage policies.

### Q: What if the summary is inaccurate?

**A:** AI summaries are helpful overviews but should be verified:

```bash
# Cross-check important details
ytc open VIDEO_ID  # Read transcript yourself

# Ask Claude to clarify
ytc ai VIDEO_ID --prompt "Is X mentioned in the transcript? Provide exact quote if yes"
```

---

## See Also

- [OPEN.md](./OPEN.md) - Open transcripts for reference while reading AI analysis
- [SEARCH.md](./SEARCH.md) - Find related videos by topic
- [FETCH.md](./FETCH.md) - Download new videos to analyze
- [INFO.md](./INFO.md) - View video details with descriptions

---

**Shorthand:** `ytc ai --help` shows quick reference

**Phase:** AI integration (Phase 5) - First release with local Claude CLI support
