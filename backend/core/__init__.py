"""
Texgraph — Markdown-to-LuaLaTeX-to-PDFx poetry collection compiler.

This package provides a pipeline that:
  1. Parses Markdown files with YAML front matter (poems, prose, section metadata)
  2. Assembles them into a full LuaLaTeX document via Jinja2 templates
  3. Compiles the document to PDF/X-compliant output through lualatex subprocess calls

Typical entry point is the CLI:

    $ texgraph build --config collection.yaml --output dist/

Or use the Python API directly:

    from backend.core.config import CollectionConfig
    from backend.core.parser import PoetryParser
    from backend.core.renderer import LaTeXRenderer
    from backend.core.compiler import Compiler
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
