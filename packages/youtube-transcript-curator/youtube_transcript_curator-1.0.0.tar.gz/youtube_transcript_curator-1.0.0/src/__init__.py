"""YouTube Transcript Curator - Curate, organize, and explore YouTube transcripts."""

__version__ = "1.0.0"
__author__ = "Marius Giurgi"
__email__ = "marius.giurgi@gmail.com"
__license__ = "MIT"

# Import main CLI function for easy access
from src.cli.main import cli as main

__all__ = ["main", "__version__"]
