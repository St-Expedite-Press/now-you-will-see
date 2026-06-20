"""Domain exceptions raised by services; mapped to HTTP codes in main.py."""

from __future__ import annotations


class NotFoundError(Exception):
    """Resource not found."""


class ConflictError(Exception):
    """Resource already exists or state conflict."""


class ValidationError(Exception):
    """Invalid input data."""


class BuildError(Exception):
    """LuaLaTeX compilation failure."""


class AgentError(Exception):
    """Anthropic API / agent error."""
