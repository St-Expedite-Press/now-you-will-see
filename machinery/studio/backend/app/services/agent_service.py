"""Agent service â€” bridges the FastAPI layer to the Anthropic API.

Streams token chunks via an async generator consumed by the WebSocket router.
Builds the system prompt from context files and injects collection state.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import AsyncIterator

from app.core.config import settings
from app.core.exceptions import AgentError
from app.models.agent import AgentChatRequest, AgentContext

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

_SYSTEM_PROMPT = """\
You are an expert poetry editor and LuaLaTeX/Texgraph assistant.
You help the user structure, edit, and compile poetry collections using the Texgraph pipeline.
When you suggest changes to YAML frontmatter or content files, output them as fenced code blocks.
When you propose structural changes (reordering sections, renaming slugs), include action chips
in your response as a JSON block with key "action_chips": [{label, action, payload}, ...].
Always be concise. The user is an experienced poet, not a LaTeX novice.
"""


def _load_context(ctx: AgentContext, workspace_root: Path) -> str:
    parts: list[str] = []
    if ctx.collection_yaml:
        parts.append(f"## collection.yaml\n```yaml\n{ctx.collection_yaml}\n```")
    if ctx.active_section_meta:
        parts.append(f"## Active section _meta.yaml\n```yaml\n{ctx.active_section_meta}\n```")
    if ctx.active_poem_content:
        parts.append(f"## Active poem\n```markdown\n{ctx.active_poem_content}\n```")
    if ctx.notes_md:
        parts.append(f"## NOTES.md\n{ctx.notes_md}")
    if ctx.recent_build_log:
        parts.append(f"## Recent build log (tail)\n```\n{ctx.recent_build_log}\n```")
    return "\n\n".join(parts)


async def stream_chat(request: AgentChatRequest) -> AsyncIterator[str]:
    """Yield token strings; raises AgentError on API failure."""
    try:
        import anthropic
    except ImportError as exc:
        raise AgentError("anthropic package not installed") from exc

    api_key = settings.anthropic_api_key
    if not api_key:
        raise AgentError("ANTHROPIC_API_KEY not set")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    context_block = _load_context(request.context, settings.workspace_root)
    system = _SYSTEM_PROMPT
    if context_block:
        system += f"\n\n---\n# Current project context\n\n{context_block}"

    messages = [{"role": m.role, "content": m.content} for m in request.messages if m.role != "system"]

    try:
        async with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
    except anthropic.APIError as exc:
        raise AgentError(str(exc)) from exc

