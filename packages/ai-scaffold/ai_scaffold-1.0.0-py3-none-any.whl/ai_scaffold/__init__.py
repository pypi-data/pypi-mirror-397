"""
ai-scaffold
Generate real project files from AI-generated Markdown or JSON.
"""
__version__ = "1.0.0"
from .parser import parse_markdown, parse_json
from .generator import generate
__all__ = ["parse_markdown", "parse_json", "generate", "__version__"]