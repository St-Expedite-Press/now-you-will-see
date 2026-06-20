"""ToolCatalog — pipeline operations exposed as callable, schema'd tools.

Each tool corresponds to a ``texgraph <command>`` operation. A tool's id is the
command string (e.g. ``"texgraph proof-build"``); its provider-facing name is the
same with spaces/dashes turned into underscores. Execution shells out to the
installed ``texgraph`` CLI, scoped to the active project. Tests inject a fake
``runner`` so no real build is required.

The catalog is the *whole* surface; a GatedAgent is granted only a subset (its
``agent.yaml`` tool allow-list), and the runtime refuses any tool outside it.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class RunContext:
    """Where a tool may run and write."""
    project_id: str | None
    repo_root: Path
    scope: Path | None = None  # the stage's artifact_dir; informational guard


@dataclass
class ToolResult:
    ok: bool
    output: str
    tool: str


# A runner executes a fully-built argv and returns a ToolResult. Swapped in tests.
Runner = Callable[[list[str], RunContext], ToolResult]


def default_runner(argv: list[str], ctx: RunContext) -> ToolResult:
    """Run the installed ``texgraph`` CLI; capture trimmed combined output.

    Captures bytes and decodes UTF-8 explicitly — ``text=True`` defaults to cp1252
    on Windows and crashes on the CLI's unicode (rules, ✓, em dashes).
    """
    exe = shutil.which("texgraph") or "texgraph"
    proc = subprocess.run([exe, *argv], cwd=str(ctx.repo_root), capture_output=True)
    raw = (proc.stdout or b"") + (proc.stderr or b"")
    out = raw.decode("utf-8", errors="replace").strip()
    return ToolResult(ok=proc.returncode == 0, output=out[-4000:], tool=" ".join(argv[:2]))


def _provider_name(tool_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", tool_id.lower()).strip("_")


@dataclass
class ToolSpec:
    """A single callable pipeline tool.

    ``id`` is the ``texgraph <cmd>`` string. ``parameters`` is a JSON-schema
    properties dict. ``build_argv`` turns validated args + context into the CLI argv.
    """
    id: str
    summary: str
    parameters: dict = field(default_factory=dict)
    required: tuple[str, ...] = ()
    build_argv: Callable[[dict, RunContext], list[str]] | None = None

    @property
    def name(self) -> str:
        return _provider_name(self.id)

    @property
    def subcommand(self) -> list[str]:
        # "texgraph proof-build" -> ["proof-build"]; "texgraph pdf info" -> ["pdf","info"]
        return self.id.split()[1:]

    def schema(self) -> dict:
        """Provider tool-definition schema (Anthropic/OpenRouter-compatible)."""
        return {
            "name": self.name,
            "description": self.summary,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": list(self.required),
            },
        }

    def argv(self, args: dict, ctx: RunContext) -> list[str]:
        if self.build_argv is not None:
            return self.build_argv(args, ctx)
        return self._default_argv(args, ctx)

    def _default_argv(self, args: dict, ctx: RunContext) -> list[str]:
        argv = list(self.subcommand)
        for tok in args.get("args", []) or []:
            argv.append(str(tok))
        if ctx.project_id and args.get("project", True):
            argv += ["--project", ctx.project_id]
        return argv


# --- The catalog of pipeline tools (station-relevant subset) -------------------

_PROJECT_PARAMS = {
    "args": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Extra positional/flag arguments for the command.",
    }
}


def _build_tools() -> dict[str, ToolSpec]:
    specs = [
        ToolSpec("texgraph proof-build", "Build the interior proof PDF for the project (optionally a trim variant or print-ready PDF/X).", _PROJECT_PARAMS),
        ToolSpec("texgraph proof-preview", "Render the structurally important proof pages to PNG for visual review.", _PROJECT_PARAMS),
        ToolSpec("texgraph verify-coverage", "Prove every transcription poem maps 1:1 to a built reading poem.", _PROJECT_PARAMS),
        ToolSpec("texgraph build", "Render the collection to a full PDF.", _PROJECT_PARAMS),
        ToolSpec("texgraph audit", "Audit a transcription book directory for completeness and correctness.", _PROJECT_PARAMS),
        ToolSpec("texgraph scan", "Scan source PDFs for front/back-matter keyword signals.", _PROJECT_PARAMS),
        ToolSpec("texgraph metadata", "Generate or validate per-book book.json metadata.", _PROJECT_PARAMS),
        ToolSpec("texgraph plan", "Inspect project plan heading structure and index readiness.", _PROJECT_PARAMS),
        ToolSpec("texgraph page-map", "Map printed page numbers to scan page numbers via a fixed offset.", _PROJECT_PARAMS),
        ToolSpec("texgraph pdf info", "Inspect a source PDF's metadata (pages, encryption, edition).", _PROJECT_PARAMS),
        ToolSpec("texgraph pdf text", "Extract text from a source PDF page range.", _PROJECT_PARAMS),
        ToolSpec("texgraph pdf render", "Render source PDF pages to PNG.", _PROJECT_PARAMS),
        ToolSpec("texgraph archive files", "List files for an Internet Archive identifier.", _PROJECT_PARAMS),
        ToolSpec("texgraph archive download", "Download a file from the Internet Archive.", _PROJECT_PARAMS),
        ToolSpec("texgraph ingest rename", "Rename a source to its stable name and write its provenance record.", _PROJECT_PARAMS),
        ToolSpec("texgraph new poem", "Scaffold a new poem Markdown file.", _PROJECT_PARAMS),
        ToolSpec("texgraph list", "List registered projects.", {}),
        ToolSpec("texgraph watch", "Watch for changes and rebuild automatically.", _PROJECT_PARAMS),
        ToolSpec("texgraph verify", "Check that the upstream stage is complete before starting a stage.", _PROJECT_PARAMS),
        ToolSpec("texgraph promote", "Approve a pipeline stage by writing status: approved to its PROMOTION.yaml.", _PROJECT_PARAMS),
    ]
    return {s.id: s for s in specs}


class ToolCatalog:
    """The full set of pipeline tools, plus scoped execution."""

    def __init__(self, runner: Runner | None = None) -> None:
        self._specs = _build_tools()
        self._runner = runner or default_runner

    def get(self, tool_id: str) -> ToolSpec | None:
        # Accept both "texgraph verify sources" and "texgraph verify" (stage-suffixed).
        if tool_id in self._specs:
            return self._specs[tool_id]
        head = " ".join(tool_id.split()[:2])
        return self._specs.get(head)

    def specs_for(self, allow: list[str]) -> list[ToolSpec]:
        out: list[ToolSpec] = []
        seen: set[str] = set()
        for tid in allow:
            spec = self.get(tid)
            if spec and spec.id not in seen:
                out.append(spec)
                seen.add(spec.id)
        return out

    def by_provider_name(self, name: str) -> ToolSpec | None:
        for spec in self._specs.values():
            if spec.name == name:
                return spec
        return None

    def execute(self, tool_id: str, args: dict, ctx: RunContext) -> ToolResult:
        spec = self.get(tool_id)
        if spec is None:
            return ToolResult(ok=False, output=f"unknown tool {tool_id!r}", tool=tool_id)
        return self._runner(spec.argv(args or {}, ctx), ctx)
