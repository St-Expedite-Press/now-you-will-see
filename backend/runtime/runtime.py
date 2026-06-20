"""AgentRuntime — the provider-abstract tool-call loop.

An ``Adapter`` is any LLM provider that can take a system prompt, a message
history, and a set of tool schemas, and return a :class:`Turn` (final text and/or
tool-call requests). The runtime drives the loop: it offers the gated agent's tools,
**refuses any tool outside the agent's allow-list**, executes the rest via the
ToolCatalog, feeds results back, and repeats until the model returns final text.

Adapters live in ``backend.runtime.adapters`` (dev = OpenRouter/Anthropic for
building; hermes = production). Tests use a scripted fake adapter — no key required.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from backend.runtime.gated_agent import GatedAgent
from backend.runtime.tools import RunContext, ToolCatalog, ToolResult


@dataclass
class ToolCall:
    id: str
    name: str  # provider-facing tool name
    arguments: dict


@dataclass
class Turn:
    """One model turn: final text and/or a batch of tool-call requests."""
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class Adapter(Protocol):
    def complete(self, *, system: str, messages: list[dict], tools: list[dict]) -> Turn:
        """Return the model's next turn given the conversation and tool schemas."""
        ...


@dataclass
class Step:
    tool: str
    arguments: dict
    allowed: bool
    result: ToolResult


@dataclass
class RunResult:
    text: str
    steps: list[Step]
    messages: list[dict]


class AgentRuntime:
    def __init__(
        self,
        adapter: Adapter,
        catalog: ToolCatalog | None = None,
        *,
        max_steps: int = 8,
    ) -> None:
        self.adapter = adapter
        self.catalog = catalog or ToolCatalog()
        self.max_steps = max_steps

    def run(
        self,
        agent: GatedAgent,
        messages: list[dict],
        ctx: RunContext,
    ) -> RunResult:
        """Drive the tool-call loop for one user turn; return final text + transcript."""
        convo = list(messages)
        tool_schemas = [t.schema() for t in agent.tools]
        steps: list[Step] = []

        for _ in range(self.max_steps):
            turn = self.adapter.complete(
                system=agent.system_prompt, messages=convo, tools=tool_schemas
            )
            if not turn.tool_calls:
                convo.append({"role": "assistant", "content": turn.text})
                return RunResult(text=turn.text, steps=steps, messages=convo)

            convo.append(
                {
                    "role": "assistant",
                    "content": turn.text,
                    "tool_calls": [
                        {"id": c.id, "name": c.name, "arguments": c.arguments}
                        for c in turn.tool_calls
                    ],
                }
            )
            for call in turn.tool_calls:
                step = self._dispatch(agent, call, ctx)
                steps.append(step)
                convo.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "name": call.name,
                        "content": step.result.output,
                    }
                )

        # Ran out of steps without a final text turn.
        return RunResult(text="(stopped: tool-step limit reached)", steps=steps, messages=convo)

    def _dispatch(self, agent: GatedAgent, call: ToolCall, ctx: RunContext) -> Step:
        spec = self.catalog.by_provider_name(call.name)
        if spec is None:
            return Step(call.name, call.arguments, False,
                        ToolResult(False, f"unknown tool {call.name!r}", call.name))
        # Gating: refuse anything outside this stage agent's allow-list.
        if not agent.allows(spec.id):
            return Step(spec.id, call.arguments, False,
                        ToolResult(False,
                                   f"REFUSED: `{spec.id}` is not permitted for the "
                                   f"{agent.stage} stage.", spec.id))
        result = self.catalog.execute(spec.id, call.arguments, ctx)
        return Step(spec.id, call.arguments, True, result)
