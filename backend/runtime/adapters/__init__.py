"""Provider adapters for the AgentRuntime.

- ``DevAdapter`` — Anthropic / OpenRouter, for building and testing the system now.
- ``HermesAdapter`` — the production runtime; a documented stub until the Hermes
  integration contract is wired.
"""
from backend.runtime.adapters.dev import DevAdapter
from backend.runtime.adapters.hermes import HermesAdapter

__all__ = ["DevAdapter", "HermesAdapter"]
