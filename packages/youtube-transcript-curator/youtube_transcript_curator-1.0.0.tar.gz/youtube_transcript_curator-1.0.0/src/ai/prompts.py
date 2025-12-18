"""Extraction prompt templates and JSON parsing for AI processing."""

import json
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Supported extraction types
EXTRACTION_TYPES = ['books', 'tools', 'key_points']

# Prompt templates for each extraction type
EXTRACTION_PROMPTS: Dict[str, str] = {
    "books": """Extract all books, papers, articles, and written resources mentioned in this transcript.

For each item, provide:
1. title: Full title of the book/paper
2. author: Author name(s) if mentioned (use "Unknown" if not stated)
3. mentioned_at: Timestamp in MM:SS format where it was mentioned
4. timestamp_seconds: The timestamp converted to total seconds
5. context: 1-2 sentences explaining why/how it was mentioned
6. type: One of "book", "paper", "article", "blog_post"

Return ONLY a valid JSON array. No explanation, no markdown formatting.
Example format:
[
  {
    "title": "Book Title",
    "author": "Author Name",
    "mentioned_at": "5:43",
    "timestamp_seconds": 343,
    "context": "Recommended for learning distributed systems.",
    "type": "book"
  }
]

If no books/papers are mentioned, return an empty array: []

Transcript:
""",

    "tools": """Extract all tools, software, libraries, frameworks, apps, and services mentioned in this transcript.

For each item, provide:
1. name: Name of the tool/software
2. mentioned_at: Timestamp in MM:SS format where it was mentioned
3. timestamp_seconds: The timestamp converted to total seconds
4. context: 1-2 sentences explaining why/how it was mentioned
5. category: One of "library", "framework", "app", "service", "database", "language", "platform", "cli"
6. url: Official URL if mentioned (use null if not mentioned)

Return ONLY a valid JSON array. No explanation, no markdown formatting.
Example format:
[
  {
    "name": "LangChain",
    "mentioned_at": "3:22",
    "timestamp_seconds": 202,
    "context": "Used for building RAG pipelines.",
    "category": "framework",
    "url": null
  }
]

If no tools are mentioned, return an empty array: []

Transcript:
""",

    "key_points": """Extract the key insights, main takeaways, and important concepts from this transcript.

For each key point, provide:
1. point: A clear, concise statement of the insight (1-2 sentences)
2. mentioned_at: Timestamp in MM:SS format where this was discussed
3. timestamp_seconds: The timestamp converted to total seconds
4. context: Additional context or supporting details
5. importance: One of "critical", "important", "notable"

Return ONLY a valid JSON array. No explanation, no markdown formatting.
Aim for 5-15 key points depending on video length.
Example format:
[
  {
    "point": "No single document parser works perfectly for all use cases.",
    "mentioned_at": "8:15",
    "timestamp_seconds": 495,
    "context": "The speaker tested 5 different parsers and found each had trade-offs.",
    "importance": "critical"
  }
]

Transcript:
"""
}


def get_extraction_prompt(extraction_type: str) -> str:
    """
    Get the prompt template for a given extraction type.

    Args:
        extraction_type: One of 'books', 'tools', 'key_points'

    Returns:
        Prompt template string

    Raises:
        ValueError: If extraction_type is not recognized
    """
    if extraction_type not in EXTRACTION_PROMPTS:
        raise ValueError(
            f"Unknown extraction type: {extraction_type}. "
            f"Must be one of: {list(EXTRACTION_PROMPTS.keys())}"
        )
    return EXTRACTION_PROMPTS[extraction_type]


def parse_timestamp_to_seconds(timestamp: str) -> int:
    """
    Convert timestamp string to total seconds.

    Args:
        timestamp: Timestamp in format "MM:SS" or "HH:MM:SS"

    Returns:
        Total seconds as integer
    """
    if not timestamp:
        return 0

    parts = timestamp.split(':')
    try:
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return 0
    except (ValueError, IndexError):
        return 0


def parse_claude_json_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse JSON from Claude's response.

    Handles various response formats:
    - Clean JSON array
    - JSON wrapped in markdown code blocks
    - JSON with surrounding text/explanation

    Args:
        response: Raw response string from Claude

    Returns:
        List of dictionaries parsed from JSON

    Raises:
        ValueError: If JSON cannot be parsed from response
    """
    if not response or not response.strip():
        return []

    response = response.strip()

    # Try 1: Direct parsing (clean JSON)
    try:
        result = json.loads(response)
        if isinstance(result, list):
            return result
        # If it's a dict with an items/results key, extract that
        if isinstance(result, dict):
            for key in ['items', 'results', 'data', 'books', 'tools', 'key_points']:
                if key in result and isinstance(result[key], list):
                    return result[key]
        return []
    except json.JSONDecodeError:
        pass

    # Try 2: Extract from markdown code block
    code_block_patterns = [
        r'```json\s*\n?([\s\S]*?)\n?```',  # ```json ... ```
        r'```\s*\n?([\s\S]*?)\n?```',       # ``` ... ```
    ]

    for pattern in code_block_patterns:
        match = re.search(pattern, response)
        if match:
            try:
                result = json.loads(match.group(1).strip())
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                continue

    # Try 3: Find JSON array anywhere in response
    # Look for outermost [ ... ] with balanced brackets
    bracket_start = response.find('[')
    if bracket_start != -1:
        # Find matching closing bracket
        depth = 0
        for i, char in enumerate(response[bracket_start:], bracket_start):
            if char == '[':
                depth += 1
            elif char == ']':
                depth -= 1
                if depth == 0:
                    try:
                        result = json.loads(response[bracket_start:i + 1])
                        if isinstance(result, list):
                            return result
                    except json.JSONDecodeError:
                        break
                    break

    # Try 4: Simple regex for array
    array_match = re.search(r'\[[\s\S]*\]', response)
    if array_match:
        try:
            result = json.loads(array_match.group(0))
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # If we get here, we couldn't parse JSON
    logger.warning(f"Could not parse JSON from response: {response[:200]}...")
    raise ValueError(
        f"Could not parse JSON from Claude response. "
        f"Response preview: {response[:100]}..."
    )


def validate_extraction_items(
    items: List[Dict[str, Any]],
    extraction_type: str
) -> List[Dict[str, Any]]:
    """
    Validate and normalize extracted items.

    Args:
        items: List of extracted items from Claude
        extraction_type: Type of extraction ('books', 'tools', 'key_points')

    Returns:
        List of validated items (invalid items are logged and skipped)
    """
    # Required fields for each extraction type
    required_fields = {
        'books': ['title'],
        'tools': ['name'],
        'key_points': ['point']
    }

    # Optional fields with defaults
    defaults = {
        'books': {
            'author': 'Unknown',
            'mentioned_at': '0:00',
            'timestamp_seconds': 0,
            'context': '',
            'type': 'book'
        },
        'tools': {
            'mentioned_at': '0:00',
            'timestamp_seconds': 0,
            'context': '',
            'category': 'tool',
            'url': None
        },
        'key_points': {
            'mentioned_at': '0:00',
            'timestamp_seconds': 0,
            'context': '',
            'importance': 'notable'
        }
    }

    if extraction_type not in required_fields:
        raise ValueError(f"Unknown extraction type: {extraction_type}")

    validated = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            logger.warning(f"Skipping non-dict item at index {i}: {item}")
            continue

        # Check required fields
        missing = [f for f in required_fields[extraction_type] if f not in item or not item[f]]
        if missing:
            logger.warning(
                f"Skipping item missing required fields {missing}: "
                f"{str(item)[:100]}..."
            )
            continue

        # Apply defaults for missing optional fields
        for field, default in defaults[extraction_type].items():
            if field not in item or item[field] is None:
                item[field] = default

        # Normalize timestamp_seconds if missing but mentioned_at exists
        if item.get('timestamp_seconds', 0) == 0 and item.get('mentioned_at'):
            item['timestamp_seconds'] = parse_timestamp_to_seconds(item['mentioned_at'])

        validated.append(item)

    return validated


def get_extraction_type_display_name(extraction_type: str) -> str:
    """Get human-readable display name for extraction type."""
    display_names = {
        'books': 'Books & Papers',
        'tools': 'Tools & Software',
        'key_points': 'Key Points'
    }
    return display_names.get(extraction_type, extraction_type.replace('_', ' ').title())


def get_extraction_type_emoji(extraction_type: str) -> str:
    """Get emoji for extraction type."""
    emojis = {
        'books': '📚',
        'tools': '🛠️',
        'key_points': '💡'
    }
    return emojis.get(extraction_type, '📋')
