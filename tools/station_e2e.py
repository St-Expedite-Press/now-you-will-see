#!/usr/bin/env python3
"""station_e2e.py — drive the reference tenant through the station, end to end.

Walks fletcher-early-works across the station screens. For each stage it assembles
the *real* gated agent and runs a turn through the AgentRuntime in which a scripted
adapter (deterministic — no LLM) decides to call one of the stage's real tools; the
ToolCatalog then executes the actual ``texgraph`` CLI against the live project. It
also demonstrates gating refusal and walks the gate / hand-off chain against the
real PROMOTION.yaml files.

    python tools/station_e2e.py            # fast: verifies + coverage + gating + handoffs
    python tools/station_e2e.py --full     # also builds the interior proof PDF
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.env import repo_root
from backend.runtime import AgentRuntime, RunContext, ToolCatalog, assemble_agent
from backend.runtime.handoff import GateNotPassed, HandoffController
from backend.runtime.runtime import ToolCall, Turn

PROJECT = "fletcher-early-works"

# One representative real tool per stage (deterministic demo).
_SRC_PDF = "projects/fletcher-series/sources/raw/early_1913/fire_and_wine.pdf"
_VOL = "projects/fletcher-early-works/transcription/volumes/01_early_works"
PLAN: dict[str, tuple[str, list[str], bool]] = {
    "workspace": ("texgraph list", [], False),
    "sources": ("texgraph pdf info", [_SRC_PDF], False),
    "transcription": ("texgraph metadata", [_VOL, "--check"], False),
    "manuscript": ("texgraph verify-coverage", [], True),
    "interior": ("texgraph verify-coverage", [], True),
}


class ScriptedAdapter:
    """Deterministic stand-in for an LLM: returns pre-scripted turns."""

    def __init__(self, turns: list[Turn]) -> None:
        self.turns = list(turns)

    def complete(self, *, system, messages, tools):
        return self.turns.pop(0)


def _run_tool(catalog, agent, ctx, tool_id, extra=None, use_project=True):
    spec = catalog.get(tool_id)
    args = {"args": extra or []}
    if not use_project:
        args["project"] = False
    adapter = ScriptedAdapter([
        Turn(tool_calls=[ToolCall(id="c", name=spec.name, arguments=args)]),
        Turn(text="(done)"),
    ])
    return AgentRuntime(adapter, catalog=catalog).run(
        agent, [{"role": "user", "content": "run your stage check"}], ctx
    )


def main(full: bool = False) -> int:
    root = repo_root()
    catalog = ToolCatalog()
    ctx = RunContext(project_id=PROJECT, repo_root=root)
    handoff = HandoffController(root=root, catalog=catalog)
    order = handoff.order()

    print(f"\n=== STATION END-TO-END — tenant: {PROJECT} ===\n")

    # 1) Each screen's gated agent runs a real tool through the runtime.
    for stage in order:
        agent = assemble_agent(stage, PROJECT, root=root, catalog=catalog)
        print(f"── screen {agent.screen} · {agent.title}  [{stage}]")
        print(f"   scope: {agent.scope}")
        print(f"   gate:  {agent.gate or 'none'}   tools: {len(agent.tools)}")
        tool_id, extra, use_proj = PLAN[stage]
        res = _run_tool(catalog, agent, ctx, tool_id, extra, use_proj)
        for s in res.steps:
            mark = "REFUSED" if not s.allowed else ("ok" if s.result.ok else "FAIL")
            head = s.result.output.splitlines()[-1] if s.result.output else ""
            print(f"   tool [{mark}] {s.tool}  → {head[:70]}")
        print()

    # 2) Gating: the interior agent may NOT use a sources tool.
    print("── gating check: interior agent asked to `ingest rename` (a sources tool)")
    interior = assemble_agent("interior", PROJECT, root=root, catalog=catalog)
    spec = catalog.get("texgraph ingest rename")
    adapter = ScriptedAdapter([
        Turn(tool_calls=[ToolCall(id="x", name=spec.name, arguments={})]),
        Turn(text="(refused)"),
    ])
    res = AgentRuntime(adapter, catalog=catalog).run(
        interior, [{"role": "user", "content": "register a source"}], ctx
    )
    step = res.steps[0]
    print(f"   → allowed={step.allowed}  {step.result.output}\n")

    # 3) Hand-off chain against the real gates.
    print("── gate / hand-off chain (real PROMOTION.yaml state)")
    for stage in order:
        agent = assemble_agent(stage, PROJECT, root=root, catalog=catalog)
        passed = handoff.gate_passed(agent, PROJECT)
        print(f"   {stage:<14} gate {'PASSED ' if passed else 'pending'}  ({agent.gate or 'no gate'})")
    print()

    # 4) Full: the interior agent compiles the actual proof.
    if full:
        print("── interior agent compiles the proof (real build)…")
        spec = catalog.get("texgraph proof-build")
        adapter = ScriptedAdapter([
            Turn(tool_calls=[ToolCall(id="p", name=spec.name, arguments={})]),
            Turn(text="(built)"),
        ])
        res = AgentRuntime(adapter, catalog=catalog).run(
            interior, [{"role": "user", "content": "build the proof"}], ctx
        )
        s = res.steps[0]
        tail = "\n".join(s.result.output.splitlines()[-3:])
        print(f"   proof-build ok={s.result.ok}\n{tail}\n")

    print("=== end-to-end complete ===\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="also build the interior proof PDF")
    raise SystemExit(main(**vars(ap.parse_args())))
