"""Agent runtime: assembly, gating enforcement, tool-call loop, handoff."""
from __future__ import annotations

from backend.core.env import repo_root
from backend.runtime import (
    AgentRuntime,
    HandoffController,
    RunContext,
    ToolCatalog,
    Turn,
    assemble_agent,
)
from backend.runtime.handoff import GateNotPassed
from backend.runtime.runtime import ToolCall


class FakeAdapter:
    """Returns scripted turns; records what it was offered."""

    def __init__(self, script: list[Turn]) -> None:
        self.script = list(script)
        self.offered_tools: list[list[str]] = []

    def complete(self, *, system, messages, tools):
        self.offered_tools.append([t["name"] for t in tools])
        return self.script.pop(0)


def _catalog_with_recorder():
    ran: list[list[str]] = []

    def runner(argv, ctx):
        from backend.runtime.tools import ToolResult

        ran.append(argv)
        return ToolResult(ok=True, output="ran " + " ".join(argv), tool=" ".join(argv[:2]))

    return ToolCatalog(runner=runner), ran


def _ctx():
    return RunContext(project_id="demo", repo_root=repo_root())


# --- assembly ------------------------------------------------------------------

def test_assemble_interior_agent():
    agent = assemble_agent("interior", "demo")
    assert agent.stage == "interior"
    assert agent.screen == 3
    assert "typesetting" in agent.skills
    assert "texgraph proof-build" in agent.tool_allow
    assert "gated specialist" in agent.system_prompt
    assert agent.scope is not None and agent.scope.name == "interior"


def test_agent_only_offered_its_tools():
    catalog, _ = _catalog_with_recorder()
    agent = assemble_agent("sources", "demo", catalog=catalog)
    adapter = FakeAdapter([Turn(text="hi")])
    AgentRuntime(adapter, catalog=catalog).run(agent, [{"role": "user", "content": "go"}], _ctx())
    offered = set(adapter.offered_tools[0])
    assert "texgraph_archive_files" in offered          # sources tool
    assert "texgraph_proof_build" not in offered        # interior tool — not offered


# --- gating + tool-call loop ---------------------------------------------------

def test_allowed_tool_executes():
    catalog, ran = _catalog_with_recorder()
    agent = assemble_agent("interior", "demo", catalog=catalog)
    adapter = FakeAdapter([
        Turn(tool_calls=[ToolCall(id="1", name="texgraph_proof_build", arguments={})]),
        Turn(text="proof built."),
    ])
    result = AgentRuntime(adapter, catalog=catalog).run(
        agent, [{"role": "user", "content": "build the proof"}], _ctx()
    )
    assert result.text == "proof built."
    assert result.steps[0].allowed is True
    assert ran and ran[0][0] == "proof-build"           # the CLI op actually ran


def test_out_of_scope_tool_is_refused():
    catalog, ran = _catalog_with_recorder()
    agent = assemble_agent("interior", "demo", catalog=catalog)   # interior may NOT ingest
    adapter = FakeAdapter([
        Turn(tool_calls=[ToolCall(id="1", name="texgraph_ingest_rename", arguments={})]),
        Turn(text="ok"),
    ])
    result = AgentRuntime(adapter, catalog=catalog).run(
        agent, [{"role": "user", "content": "rename a source"}], _ctx()
    )
    assert result.steps[0].allowed is False
    assert "REFUSED" in result.steps[0].result.output
    assert ran == []                                    # nothing executed


# --- handoff -------------------------------------------------------------------

def test_pipeline_order_and_next_stage():
    h = HandoffController()
    assert h.order()[:3] == ["workspace", "sources", "transcription"]
    assert h.next_stage("transcription") == "manuscript"
    assert h.next_stage("interior") is None


def test_handoff_advances_when_gate_passes():
    h = HandoffController()
    manuscript = assemble_agent("manuscript", "demo")   # gate is None -> passes implicitly
    handoff = h.advance(manuscript, "demo", prior_outputs={"reading_edition": "ready"})
    assert handoff is not None
    assert handoff.next_agent.stage == "interior"
    assert "reading_edition" in handoff.seed


def test_handoff_blocked_when_gate_missing():
    h = HandoffController()
    sources = assemble_agent("sources", "no-such-project")  # gate file absent -> not approved
    try:
        h.advance(sources, "no-such-project")
        raise AssertionError("expected GateNotPassed")
    except GateNotPassed:
        pass
