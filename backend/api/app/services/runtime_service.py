"""runtime_service — the API seam to the gated agent runtime.

Replaces the old single-prompt agent_service with per-stage gated agents: each
station screen gets the specialist agent assembled from its framework spec, with
real tool-calling and gating enforced by ``backend.runtime``.
"""
from __future__ import annotations

from typing import Any

import yaml

from backend.core.env import repo_root
from backend.runtime import AgentRuntime, RunContext, ToolCatalog, assemble_agent
from backend.runtime.adapters import DevAdapter


def list_stages() -> dict[str, Any]:
    """The station screens and their stages, from framework/pipeline.yaml."""
    pipeline = yaml.safe_load((repo_root() / "framework" / "pipeline.yaml").read_text(encoding="utf-8"))
    return {"screens": pipeline.get("screens", []), "stages": pipeline.get("stages", {})}


def describe_agent(stage: str, project_id: str | None = None) -> dict[str, Any]:
    """The gated agent's public shape: title, screen, tools, skills, gate, io."""
    agent = assemble_agent(stage, project_id)
    return {
        "stage": agent.stage,
        "screen": agent.screen,
        "title": agent.title,
        "module": agent.module,
        "tools": sorted(agent.tool_allow),
        "skills": agent.skills,
        "gate": agent.gate,
        "io": agent.io,
        "scope": str(agent.scope) if agent.scope else None,
    }


def run_stage_turn(
    stage: str,
    project_id: str | None,
    messages: list[dict],
    *,
    adapter: Any | None = None,
    catalog: ToolCatalog | None = None,
) -> dict[str, Any]:
    """Run one user turn for a stage's gated agent; return final text + tool transcript."""
    catalog = catalog or ToolCatalog()
    agent = assemble_agent(stage, project_id, catalog=catalog)
    runtime = AgentRuntime(adapter or DevAdapter(), catalog=catalog)
    convo = [{"role": m["role"], "content": m["content"]} for m in messages if m.get("role") != "system"]
    ctx = RunContext(project_id=project_id, repo_root=repo_root(), scope=agent.scope)
    result = runtime.run(agent, convo, ctx)
    return {
        "text": result.text,
        "steps": [
            {"tool": s.tool, "allowed": s.allowed, "ok": s.result.ok, "output": s.result.output}
            for s in result.steps
        ],
    }
