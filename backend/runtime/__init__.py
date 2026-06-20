"""backend.runtime — the agent runtime.

Turns the framework's per-stage agent specs (framework/agents/<stage>/agent.yaml)
into live, gated specialist agents with real tool-calling. Provider-abstract: the
same runtime drives a dev adapter (OpenRouter/Anthropic) for building/testing and a
Hermes adapter in production.

  ToolCatalog      pipeline operations exposed as callable, schema'd tools
  GatedAgent       one stage's assembled agent (prompt + tools + skills + scope)
  assemble_agent   build a GatedAgent from a stage's agent.yaml
  AgentRuntime     the tool-call loop over a provider adapter
  HandoffController gate-approval → next stage seeded with prior io
"""
from backend.runtime.gated_agent import GatedAgent, assemble_agent
from backend.runtime.handoff import HandoffController
from backend.runtime.runtime import Adapter, AgentRuntime, Turn
from backend.runtime.tools import RunContext, ToolCatalog, ToolResult, ToolSpec

__all__ = [
    "ToolCatalog",
    "ToolSpec",
    "ToolResult",
    "RunContext",
    "GatedAgent",
    "assemble_agent",
    "AgentRuntime",
    "Adapter",
    "Turn",
    "HandoffController",
]
