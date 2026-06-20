"""HermesAdapter — production runtime (stub).

The publishing station runs its agents on **Hermes** (the OpenRouter-based agent
framework). This adapter is the seam: it must take a gated agent's system prompt,
the message history, and the tool schemas, and return a :class:`Turn`.

To finish it, the Hermes integration contract is needed:

  1. session / model selection (which OpenRouter model, credentials);
  2. how tools are declared to Hermes and how it signals a tool call;
  3. how a tool result is returned and the loop resumed;
  4. streaming token delivery (optional, for the chat UI).

Until that contract is wired, instantiating is fine (so wiring/imports stay green);
calling ``complete`` raises with a pointer to this contract. The DevAdapter unblocks
all development in the meantime.
"""
from __future__ import annotations

from backend.runtime.runtime import Turn

_CONTRACT = (
    "HermesAdapter is not yet wired. Provide the Hermes integration contract "
    "(session/model, tool declaration + tool-call signalling, tool-result resume, "
    "streaming) — see backend/runtime/adapters/hermes.py. Use DevAdapter meanwhile."
)


class HermesAdapter:
    def __init__(self, *, base_url: str | None = None, api_key: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def complete(self, *, system: str, messages: list[dict], tools: list[dict]) -> Turn:
        raise NotImplementedError(_CONTRACT)
