"""DevAdapter — drive the runtime with Anthropic (default) during development.

The client is imported lazily so the package imports without the dependency or a
key; failures surface only when you actually call the model. ``ToolSpec.schema()``
already emits Anthropic-shaped tool definitions, so translation is mostly mechanical.

OpenRouter (OpenAI-compatible, for Hermes parity) is a planned `provider="openrouter"`
branch; the Anthropic path is the working default today.
"""
from __future__ import annotations

import os

from backend.runtime.runtime import ToolCall, Turn


class DevAdapter:
    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
        max_tokens: int = 2048,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.max_tokens = max_tokens

    def complete(self, *, system: str, messages: list[dict], tools: list[dict]) -> Turn:
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - dep guard
            raise RuntimeError("anthropic package not installed (pip install -e '.[studio]')") from exc
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        client = anthropic.Anthropic(api_key=self.api_key)
        resp = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            tools=tools,
            messages=_to_anthropic(messages),
        )
        text_parts: list[str] = []
        calls: list[ToolCall] = []
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                calls.append(ToolCall(id=block.id, name=block.name, arguments=dict(block.input)))
        return Turn(text="".join(text_parts), tool_calls=calls)


def _to_anthropic(messages: list[dict]) -> list[dict]:
    """Translate the runtime's internal message list into Anthropic content blocks."""
    out: list[dict] = []
    for m in messages:
        role = m["role"]
        if role == "tool":
            out.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": m["tool_call_id"],
                    "content": m.get("content", ""),
                }],
            })
        elif role == "assistant" and m.get("tool_calls"):
            content: list[dict] = []
            if m.get("content"):
                content.append({"type": "text", "text": m["content"]})
            for c in m["tool_calls"]:
                content.append({
                    "type": "tool_use",
                    "id": c["id"],
                    "name": c["name"],
                    "input": c.get("arguments", {}),
                })
            out.append({"role": "assistant", "content": content})
        else:
            out.append({"role": role, "content": m.get("content", "")})
    return out
