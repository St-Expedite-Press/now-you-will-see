"""Station end-to-end (fast): gated assembly, gating, and the gate chain against
the reference tenant. Tool execution is faked (no CLI / no LLM); the gate checks
read the real fletcher-early-works PROMOTION.yaml files.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from backend.core.env import repo_root
from backend.runtime import (
    AgentRuntime,
    HandoffController,
    RunContext,
    ToolCatalog,
    assemble_agent,
)
from backend.runtime.runtime import ToolCall, Turn
from backend.runtime.tools import ToolResult

PROJECT = "fletcher-early-works"


def _fake_catalog() -> ToolCatalog:
    return ToolCatalog(runner=lambda argv, ctx: ToolResult(True, "ran " + " ".join(argv), " ".join(argv[:2])))


class _Scripted:
    def __init__(self, turns):
        self.turns = list(turns)

    def complete(self, *, system, messages, tools):
        return self.turns.pop(0)


def test_all_station_agents_assemble_for_reference_tenant():
    for stage, screen in [("workspace", 0), ("sources", 1), ("transcription", 2), ("manuscript", 3), ("interior", 3)]:
        a = assemble_agent(stage, PROJECT)
        assert a.screen == screen
        assert a.tools, f"{stage} agent has no tools"
        if stage in {"sources", "transcription", "manuscript", "interior"}:
            assert a.scope is not None and a.scope.name == stage


def test_interior_agent_refuses_a_sources_tool():
    catalog = _fake_catalog()
    interior = assemble_agent("interior", PROJECT, catalog=catalog)
    adapter = _Scripted([
        Turn(tool_calls=[ToolCall(id="1", name="texgraph_ingest_rename", arguments={})]),
        Turn(text="can't here"),
    ])
    res = AgentRuntime(adapter, catalog=catalog).run(
        interior, [{"role": "user", "content": "register a source"}], RunContext(PROJECT, repo_root())
    )
    assert res.steps[0].allowed is False
    assert "REFUSED" in res.steps[0].result.output


def test_handoff_order_and_gates_match_reality():
    h = HandoffController()
    assert h.order() == ["workspace", "sources", "transcription", "manuscript", "interior"]
    root = repo_root()
    for stage in ("sources", "transcription", "interior"):
        agent = assemble_agent(stage, PROJECT)
        gate_file = root / agent.gate.replace("<project_id>", PROJECT)
        approved = gate_file.exists() and (
            yaml.safe_load(gate_file.read_text(encoding="utf-8")) or {}
        ).get("status") == "approved"
        assert h.gate_passed(agent, PROJECT) == approved
    # the editorial stage has no gate and passes implicitly
    assert h.gate_passed(assemble_agent("manuscript", PROJECT), PROJECT) is True
