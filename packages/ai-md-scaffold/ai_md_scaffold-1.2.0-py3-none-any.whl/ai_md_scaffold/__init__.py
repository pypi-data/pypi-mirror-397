"""
ai-md-scaffold

Generate real project files from AI-generated Markdown.
"""

__version__ = "1.2.0"

from .parser import parse_markdown
from .generator import generate

__all__ = ["parse_markdown", "generate", "__version__"]
