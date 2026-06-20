"""API seam to the gated runtime: list_stages, describe_agent, run_stage_turn."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"
if str(API) not in sys.path:
    sys.path.insert(0, str(API))

from app.services import runtime_service  # noqa: E402

from backend.runtime.runtime import ToolCall, Turn  # noqa: E402


class _FakeAdapter:
    def __init__(self, script):
        self.script = list(script)

    def complete(self, *, system, messages, tools):
        return self.script.pop(0)


def test_list_stages_exposes_screens():
    data = runtime_service.list_stages()
    stage_ids = set(data["stages"])
    assert {"workspace", "sources", "transcription", "interior"} <= stage_ids
    assert any(s["title"] == "Proof" for s in data["screens"])


def test_describe_agent_shape():
    d = runtime_service.describe_agent("interior", "demo")
    assert d["screen"] == 3
    assert "texgraph proof-build" in d["tools"]
    assert "typesetting" in d["skills"]
    assert d["gate"] and d["gate"].endswith("interior/PROMOTION.yaml")


def test_run_stage_turn_with_injected_adapter():
    out = runtime_service.run_stage_turn(
        "interior",
        "demo",
        [{"role": "user", "content": "what would you set the trim to?"}],
        adapter=_FakeAdapter([Turn(text="Royal 8vo on crème.")]),
    )
    assert out["text"] == "Royal 8vo on crème."
    assert out["steps"] == []


def test_run_stage_turn_refuses_out_of_scope_tool():
    out = runtime_service.run_stage_turn(
        "interior",
        "demo",
        [{"role": "user", "content": "register a source"}],
        adapter=_FakeAdapter([
            Turn(tool_calls=[ToolCall(id="1", name="texgraph_ingest_rename", arguments={})]),
            Turn(text="I can't do that here."),
        ]),
    )
    assert out["steps"][0]["allowed"] is False
    assert "REFUSED" in out["steps"][0]["output"]
