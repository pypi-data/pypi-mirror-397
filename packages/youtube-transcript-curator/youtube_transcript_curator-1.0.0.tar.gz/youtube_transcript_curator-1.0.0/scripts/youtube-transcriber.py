#!/usr/bin/env python3
"""Entry point for YouTube Transcript Curator CLI."""

import sys
from pathlib import Path

# Add project root to path (for src module imports)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.main import cli

if __name__ == '__main__':
    cli(obj={})
