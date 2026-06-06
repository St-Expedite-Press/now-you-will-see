#!/usr/bin/env python3
"""
task_logger.py — Model-agnostic task logging for fine-tuning dataset generation.

Records conversations from any agent framework into a universal format,
runs heuristic quality analysis at task-end, and generates label templates
for human annotation.

USAGE — end a task (most common invocation, called explicitly by user):
    python machinery/tools/task_logger.py end \\
        --description "Rename fletcher package to texgraph" \\
        --outcome success \\
        --notes "Completed flat merge; 9 modules moved; all tests pass" \\
        --tags tooling,refactor

USAGE — harvest most recent Claude Code session into a task:
    python machinery/tools/task_logger.py harvest
    python machinery/tools/task_logger.py harvest --session <session-id>
    python machinery/tools/task_logger.py harvest --session <session-id> --subagent <agent-id>

USAGE — list recorded tasks:
    python machinery/tools/task_logger.py list

USAGE — build dataset from labeled tasks:
    python machinery/tools/task_logger.py build
    python machinery/tools/task_logger.py build --output logs/dataset/ --split 0.9

PROGRAMMATIC USAGE — Anthropic API wrapper:
    from machinery.tools.task_logger import AnthropicLogger
    import anthropic

    logger = AnthropicLogger(task_description="Search for Fletcher references")
    client = logger.wrap(anthropic.Anthropic())

    # Use client.messages.create() normally — every call is logged
    response = client.messages.create(model="claude-sonnet-4-6", ...)

    # At task end:
    logger.end(outcome="success", notes="Found 8 files")

PROGRAMMATIC USAGE — OpenAI API wrapper:
    from machinery.tools.task_logger import OpenAILogger
    import openai

    logger = OpenAILogger(task_description="Generate poem scaffold")
    client = logger.wrap(openai.OpenAI())

    response = client.chat.completions.create(model="gpt-4o", ...)
    logger.end(outcome="success")

PROGRAMMATIC USAGE — Manual / custom framework:
    from machinery.tools.task_logger import Task

    task = Task.create(description="Run audit", framework="custom", model="my-model")
    task.log("user", [{"type": "text", "text": "Run the audit"}])
    task.log("assistant", [{"type": "text", "text": "Running..."}])
    task.end(outcome="success", notes="Clean audit")
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot locate repo root.")


def tasks_dir() -> Path:
    return repo_root() / "logs" / "tasks"


def dataset_dir() -> Path:
    return repo_root() / "logs" / "dataset"


# ---------------------------------------------------------------------------
# Universal message format
#
# All frameworks normalise to Anthropic Messages API block format.
# OpenAI and other formats are converted on ingestion.
#
# One JSON object per line in messages.jsonl:
# {
#   "role": "user" | "assistant" | "system",
#   "content": [{"type": "text", "text": "..."}, {"type": "tool_use", ...}, ...],
#   "timestamp": "ISO 8601",
#   "model": "claude-sonnet-4-6" | null,
#   "framework": "claude_code" | "anthropic" | "openai" | "langchain" | "custom",
#   "usage": {"input_tokens": N, "output_tokens": N, "cache_read_input_tokens": N},
#   "thinking": ""   ← extracted thinking text for analysis (not part of content)
# }
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_task_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Heuristic analysis (ported from harvest_sessions.py, framework-agnostic)
# ---------------------------------------------------------------------------

_ERROR_RE = re.compile(
    r"(Traceback \(most recent call last\)|(?<![A-Za-z])Error:|Exception:|"
    r"exit code [1-9]|UnicodeDecodeError|ModuleNotFoundError|FileNotFoundError|"
    r"PermissionError|is not recognized|cannot find|failed with|"
    r"FAILED|fatal:|(?<![A-Za-z])ERROR\s)",
    re.IGNORECASE,
)

_CORRECTION_RE = re.compile(
    r"\b(wait,|actually,|i was wrong|let me reconsider|incorrect|"
    r"i made an error|that['’]s wrong|no, actually|hmm,|hold on|"
    r"i need to reconsider|i realize i|i should have|mistake)\b",
    re.IGNORECASE,
)

_AFFIRM_RE = re.compile(
    r"^(ok|okay|good|great|perfect|thanks|thank you|done|got it|"
    r"looks good|that works|excellent|nice|yes|yep|sure)\b",
    re.IGNORECASE,
)

_CORRECT_RE = re.compile(
    r"^(but|no,|wait|that['’]s wrong|not quite|actually|that['’]s not|"
    r"incorrect|i don['’]t think|can you|instead|try again|wrong)\b",
    re.IGNORECASE,
)


@dataclass
class ToolErrorSignal:
    tool_name: str
    snippet: str


@dataclass
class TurnAnalysis:
    index: int
    role: str
    tool_calls: list[str] = field(default_factory=list)
    tool_errors: list[ToolErrorSignal] = field(default_factory=list)
    retried_tools: list[str] = field(default_factory=list)
    has_thinking: bool = False
    self_correction: bool = False
    correction_snippet: str = ""
    high_complexity: bool = False
    flagged: bool = False
    flag_reasons: list[str] = field(default_factory=list)


@dataclass
class TaskAnalysis:
    user_turns: int = 0
    assistant_turns: int = 0
    total_tool_calls: int = 0
    tool_counts: dict[str, int] = field(default_factory=dict)
    tool_error_count: int = 0
    retry_count: int = 0
    self_correction_count: int = 0
    thinking_turn_count: int = 0
    high_complexity_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    final_user_sentiment: str = "n/a"
    flagged_turns: list[TurnAnalysis] = field(default_factory=list)
    error_samples: list[str] = field(default_factory=list)
    narrative: str = ""


def analyze_messages(messages: list[dict[str, Any]]) -> TaskAnalysis:
    """Run heuristic analysis over a list of universal-format messages."""
    a = TaskAnalysis()
    tool_counts: Counter[str] = Counter()

    # Pre-scan: collect tool_use IDs that had error results
    error_tool_ids: set[str] = set()
    for msg in messages:
        if msg.get("role") == "user":
            for blk in msg.get("content", []):
                if blk.get("type") == "tool_result":
                    text = _block_text(blk)
                    if _ERROR_RE.search(text):
                        error_tool_ids.add(blk.get("tool_use_id", ""))

    # Token totals
    for msg in messages:
        u = msg.get("usage", {})
        a.input_tokens += u.get("input_tokens", 0)
        a.output_tokens += u.get("output_tokens", 0)
        a.cache_read_tokens += u.get("cache_read_input_tokens", 0)

    prev_asst_calls: list[tuple[str, str]] = []   # (tool_use_id, tool_name)
    prev_had_error = False

    for idx, msg in enumerate(messages):
        role = msg.get("role", "")
        content = msg.get("content", [])

        if role == "assistant":
            a.assistant_turns += 1
            ta = TurnAnalysis(index=idx, role="assistant")
            this_calls: list[tuple[str, str]] = []

            for blk in content:
                btype = blk.get("type")
                if btype == "thinking":
                    ta.has_thinking = True
                    a.thinking_turn_count += 1
                    thinking_text = blk.get("thinking", "")
                    if _CORRECTION_RE.search(thinking_text):
                        ta.self_correction = True
                        a.self_correction_count += 1
                        m = _CORRECTION_RE.search(thinking_text)
                        if m:
                            s = max(0, m.start() - 60)
                            e = min(len(thinking_text), m.end() + 100)
                            ta.correction_snippet = "..." + thinking_text[s:e].replace("\n", " ") + "..."
                elif btype == "tool_use":
                    tid = blk.get("id", "")
                    name = blk.get("name", "")
                    this_calls.append((tid, name))
                    tool_counts[name] += 1
                    a.total_tool_calls += 1

            ta.tool_calls = [n for _, n in this_calls]
            ta.high_complexity = len(this_calls) > 5
            if ta.high_complexity:
                a.high_complexity_count += 1
                ta.flagged = True
                ta.flag_reasons.append(f"high_complexity:{len(this_calls)}")
            if ta.self_correction:
                ta.flagged = True
                ta.flag_reasons.append("self_correction")

            if prev_had_error:
                prev_err_names = {n for tid, n in prev_asst_calls if tid in error_tool_ids}
                curr_names = {n for _, n in this_calls}
                for retried in prev_err_names & curr_names:
                    ta.retried_tools.append(retried)
                    a.retry_count += 1
                    ta.flagged = True
                    ta.flag_reasons.append(f"retry:{retried}")

            prev_asst_calls = this_calls
            prev_had_error = any(tid in error_tool_ids for tid, _ in this_calls)

            if ta.flagged:
                a.flagged_turns.append(ta)

        elif role == "user":
            a.user_turns += 1
            for blk in content:
                if blk.get("type") == "tool_result":
                    text = _block_text(blk)
                    if _ERROR_RE.search(text):
                        a.tool_error_count += 1
                        if a.flagged_turns:
                            ft = a.flagged_turns[-1]
                        else:
                            ft = TurnAnalysis(index=idx - 1, role="assistant")
                            ft.flagged = True
                            a.flagged_turns.append(ft)
                        m = _ERROR_RE.search(text)
                        snippet = text[max(0, m.start()-20):m.end()+80].replace("\n", " ")[:120] if m else ""
                        tool_name = ft.tool_calls[-1] if ft.tool_calls else "unknown"
                        ft.tool_errors.append(ToolErrorSignal(tool_name=tool_name, snippet=snippet))
                        if f"tool_error:{tool_name}" not in ft.flag_reasons:
                            ft.flag_reasons.append(f"tool_error:{tool_name}")
                        a.error_samples.append(snippet)

    # Final user sentiment
    last_user = next(
        (m for m in reversed(messages) if m.get("role") == "user"), None
    )
    if last_user:
        text = _first_text(last_user.get("content", [])).strip()
        if _AFFIRM_RE.match(text):
            a.final_user_sentiment = "affirmative"
        elif _CORRECT_RE.match(text):
            a.final_user_sentiment = "corrective"
        elif text:
            a.final_user_sentiment = "neutral"

    a.tool_counts = dict(tool_counts.most_common())

    # Narrative
    parts = [
        f"{a.user_turns} user / {a.assistant_turns} assistant turns.",
        f"{a.total_tool_calls} tool calls ({len(a.tool_counts)} tools).",
    ]
    if a.tool_error_count:
        parts.append(f"{a.tool_error_count} tool error(s).")
    if a.retry_count:
        parts.append(f"{a.retry_count} retry(s) after error.")
    if a.self_correction_count:
        parts.append(f"{a.self_correction_count} self-correction(s) in thinking.")
    if a.high_complexity_count:
        parts.append(f"{a.high_complexity_count} high-complexity turn(s) (>5 tools).")
    parts.append(f"Final user: {a.final_user_sentiment}.")
    parts.append(f"Tokens out={a.output_tokens} in={a.input_tokens} cache={a.cache_read_tokens}.")
    a.narrative = " ".join(parts)

    return a


def _block_text(blk: dict) -> str:
    c = blk.get("content", "")
    if isinstance(c, list):
        return "\n".join(b.get("text", "") for b in c if b.get("type") == "text")
    return str(c)


def _first_text(content: list[dict]) -> str:
    for blk in content:
        if blk.get("type") == "text":
            return blk.get("text", "")
    return ""


# ---------------------------------------------------------------------------
# Task: the core object
# ---------------------------------------------------------------------------

class Task:
    """A single unit of work — one task, one conversation, one label."""

    def __init__(
        self,
        task_id: str,
        description: str = "",
        framework: str = "custom",
        model: str = "",
        started_at: str = "",
    ) -> None:
        self.task_id = task_id
        self.description = description
        self.framework = framework
        self.model = model
        self.started_at = started_at or _now()
        self.ended_at: str = ""
        self.outcome: str = ""
        self.notes: str = ""
        self.tags: list[str] = []
        self.messages: list[dict[str, Any]] = []
        self._task_dir: Path | None = None

    @classmethod
    def create(
        cls,
        description: str = "",
        framework: str = "custom",
        model: str = "",
    ) -> "Task":
        return cls(
            task_id=_make_task_id(),
            description=description,
            framework=framework,
            model=model,
        )

    @classmethod
    def load(cls, task_dir: Path) -> "Task":
        """Load a task from its directory."""
        task_yaml = task_dir / "task.yaml"
        if not task_yaml.exists():
            raise FileNotFoundError(f"No task.yaml in {task_dir}")
        import yaml
        meta = yaml.safe_load(task_yaml.read_text(encoding="utf-8")) or {}
        t = cls(
            task_id=meta.get("task_id", task_dir.name),
            description=meta.get("description", ""),
            framework=meta.get("framework", "unknown"),
            model=meta.get("model", ""),
            started_at=meta.get("started_at", ""),
        )
        t.ended_at = meta.get("ended_at", "")
        t.outcome = meta.get("outcome", "")
        t.notes = meta.get("notes", "")
        t.tags = meta.get("tags", [])
        t._task_dir = task_dir
        msgs_path = task_dir / "messages.jsonl"
        if msgs_path.exists():
            with open(msgs_path, encoding="utf-8") as f:
                t.messages = [json.loads(l) for l in f if l.strip()]
        return t

    def log(
        self,
        role: str,
        content: list[dict] | str,
        *,
        model: str | None = None,
        usage: dict | None = None,
        thinking: str = "",
        timestamp: str = "",
    ) -> None:
        """Append a message in universal format."""
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": timestamp or _now(),
            "model": model or self.model,
            "framework": self.framework,
            "usage": usage or {},
            "thinking": thinking,
        })

    def end(
        self,
        outcome: str = "",
        description: str = "",
        notes: str = "",
        tags: list[str] | None = None,
    ) -> Path:
        """Finalise the task, run analysis, write to disk."""
        self.ended_at = _now()
        if outcome:
            self.outcome = outcome
        if description:
            self.description = description
        if notes:
            self.notes = notes
        if tags is not None:
            self.tags = tags
        return self.save()

    def save(self) -> Path:
        """Write messages.jsonl, task.yaml, analysis.yaml to disk."""
        td = tasks_dir()
        td.mkdir(parents=True, exist_ok=True)
        task_dir = td / self.task_id
        task_dir.mkdir(exist_ok=True)
        self._task_dir = task_dir

        # messages.jsonl
        (task_dir / "messages.jsonl").write_text(
            "\n".join(json.dumps(m, ensure_ascii=False) for m in self.messages),
            encoding="utf-8",
        )

        # analysis.yaml
        analysis = analyze_messages(self.messages)
        self._write_analysis(task_dir, analysis)

        # task.yaml
        self._write_task_yaml(task_dir, analysis)

        return task_dir

    def _write_task_yaml(self, task_dir: Path, analysis: TaskAnalysis) -> None:
        tool_counts_block = "\n".join(
            f"    {t}: {c}" for t, c in list(analysis.tool_counts.items())[:15]
        ) or "    {}"

        flagged_block_lines: list[str] = []
        for ft in analysis.flagged_turns:
            reasons = ", ".join(ft.flag_reasons)
            line = f"  - turn_index: {ft.index}\n    reasons: [{reasons}]"
            if ft.tool_errors:
                line += "\n    errors:\n" + "\n".join(
                    f"      - {json.dumps(e.snippet)}" for e in ft.tool_errors[:3]
                )
            if ft.correction_snippet:
                snip = ft.correction_snippet[:100].replace('"', "'")
                line += f"\n    thinking_snippet: \"{snip}\""
            flagged_block_lines.append(line)
        flagged_block = "\n".join(flagged_block_lines) or "  []"

        yaml_content = f"""\
# Task: {self.task_id}
# Framework: {self.framework}
# Generated: {_now()}
#
# SECTION 1 — METADATA (edit freely)
# SECTION 2 — AUTO SIGNALS (regenerated on each save, do not edit)
# SECTION 3 — LABEL (fill in for dataset inclusion)
#
# When ready to include in dataset:
#   python machinery/tools/task_logger.py build

# =============================================================================
# 1. METADATA
# =============================================================================
task_id: "{self.task_id}"
framework: "{self.framework}"
model: "{self.model}"
started_at: "{self.started_at}"
ended_at: "{self.ended_at}"

# =============================================================================
# 2. AUTO SIGNALS (do not edit — regenerated each save)
# =============================================================================
auto:
  narrative: "{analysis.narrative}"
  turns:
    user: {analysis.user_turns}
    assistant: {analysis.assistant_turns}
    thinking_present: {analysis.thinking_turn_count}
    high_complexity: {analysis.high_complexity_count}
  tools:
    total_calls: {analysis.total_tool_calls}
    unique_tools: {len(analysis.tool_counts)}
    call_counts:
{tool_counts_block}
  quality:
    tool_errors: {analysis.tool_error_count}
    retries: {analysis.retry_count}
    self_corrections: {analysis.self_correction_count}
    final_user_sentiment: "{analysis.final_user_sentiment}"
  tokens:
    input: {analysis.input_tokens}
    output: {analysis.output_tokens}
    cache_read: {analysis.cache_read_tokens}
  flagged_turns:
{flagged_block}

# =============================================================================
# 3. LABEL (fill these in to include in the dataset)
# =============================================================================

# One sentence: what was this task?
description: "{self.description}"

# success | partial | failure
#   success  = goal achieved, output correct and complete
#   partial  = progress made but incomplete or one element wrong
#   failure  = did not achieve goal, wrong output, or abandoned
outcome: "{self.outcome}"

# pipeline/ingest | pipeline/transcribe | tooling | research | conversation | etc.
job_type: ""

# Include this task's conversation in the fine-tuning dataset?
include: false

# What went right, what went wrong, what a better approach would have been.
# This is the most valuable field for fine-tuning quality.
notes: "{self.notes}"

# Tags for downstream filtering
tags: {json.dumps(self.tags)}
"""
        (task_dir / "task.yaml").write_text(yaml_content, encoding="utf-8")

    def _write_analysis(self, task_dir: Path, analysis: TaskAnalysis) -> None:
        data = {
            "narrative": analysis.narrative,
            "user_turns": analysis.user_turns,
            "assistant_turns": analysis.assistant_turns,
            "total_tool_calls": analysis.total_tool_calls,
            "tool_counts": analysis.tool_counts,
            "tool_errors": analysis.tool_error_count,
            "retries": analysis.retry_count,
            "self_corrections": analysis.self_correction_count,
            "flagged_count": len(analysis.flagged_turns),
            "final_user_sentiment": analysis.final_user_sentiment,
            "tokens": {
                "input": analysis.input_tokens,
                "output": analysis.output_tokens,
                "cache_read": analysis.cache_read_tokens,
            },
        }
        (task_dir / "analysis.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Claude Code adapter
# ---------------------------------------------------------------------------

def _claude_slug(root: Path) -> str:
    drive, rest = str(root).replace("\\", "/").split(":", 1)
    return drive.lower() + "-" + rest.replace("/", "-")


def _claude_session_dir(root: Path) -> Path:
    return Path.home() / ".claude" / "projects" / _claude_slug(root)


def _load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def _normalise_claude_content(content: list | str) -> list[dict]:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if not isinstance(content, list):
        return []
    clean = []
    for blk in content:
        btype = blk.get("type")
        if btype == "thinking":
            clean.append({"type": "thinking", "thinking": blk.get("thinking", "")})
        elif btype == "text":
            t = blk.get("text", "").strip()
            if t:
                clean.append({"type": "text", "text": t})
        elif btype == "tool_use":
            clean.append({
                "type": "tool_use",
                "id": blk.get("id", ""),
                "name": blk.get("name", ""),
                "input": blk.get("input", {}),
            })
        elif btype == "tool_result":
            rc = blk.get("content", "")
            if isinstance(rc, list):
                rc = "\n".join(b.get("text", "") for b in rc if b.get("type") == "text")
            clean.append({
                "type": "tool_result",
                "tool_use_id": blk.get("tool_use_id", ""),
                "content": str(rc)[:8000],
            })
    return clean


def harvest_claude_session(
    session_id: str | None = None,
    subagent_id: str | None = None,
    description: str = "",
) -> Task:
    """
    Convert a Claude Code JSONL session (or subagent) into a Task.

    If session_id is None, uses the most recent session for this project.
    If subagent_id is given, loads only that subagent's conversation.
    """
    root = repo_root()
    src = _claude_session_dir(root)

    if not src.exists():
        raise RuntimeError(f"Claude Code session directory not found: {src}")

    sessions = sorted(p.stem for p in src.glob("*.jsonl"))
    if not sessions:
        raise RuntimeError("No sessions found.")

    sid = session_id or sessions[-1]
    main_jsonl = src / f"{sid}.jsonl"
    if not main_jsonl.exists():
        raise RuntimeError(f"Session not found: {sid}")

    if subagent_id:
        sa_path = src / sid / "subagents" / f"agent-{subagent_id}.jsonl"
        if not sa_path.exists():
            raise RuntimeError(f"Subagent not found: {subagent_id}")
        meta_path = sa_path.with_suffix("").with_suffix(".meta.json")
        sa_desc = description
        sa_model = ""
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            sa_desc = sa_desc or meta.get("description", "")
        records = _load_jsonl(sa_path)
        framework = "claude_code_subagent"
        task_id = f"{sid[:8]}--{subagent_id[:8]}"
    else:
        records = [r for r in _load_jsonl(main_jsonl) if not r.get("isSidechain")]
        framework = "claude_code"
        task_id = sid
        sa_desc = description

    # Infer model from first assistant record
    model = ""
    for r in records:
        if r.get("type") == "assistant":
            model = r.get("message", {}).get("model", "")
            if model:
                break

    # Start time
    timestamps = [r.get("timestamp", "") for r in records if r.get("timestamp")]
    started = min(timestamps) if timestamps else _now()

    task = Task(
        task_id=task_id,
        description=sa_desc,
        framework=framework,
        model=model,
        started_at=started,
    )

    # Convert records to universal format
    msg_records = [r for r in records if r.get("type") in ("user", "assistant")]
    msg_records.sort(key=lambda r: r.get("timestamp", ""))

    for record in msg_records:
        msg = record.get("message", {})
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue
        raw_content = msg.get("content", [])
        if isinstance(raw_content, str):
            raw_content = [{"type": "text", "text": raw_content}]

        content = _normalise_claude_content(raw_content)
        usage = msg.get("usage", {})
        thinking = ""
        for blk in raw_content:
            if blk.get("type") == "thinking":
                thinking = blk.get("thinking", "")
                break

        task.log(
            role=role,
            content=content,
            model=msg.get("model", ""),
            usage={
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
            },
            thinking=thinking,
            timestamp=record.get("timestamp", ""),
        )

    return task


def list_claude_sessions() -> list[dict[str, Any]]:
    """Return metadata for all Claude Code sessions for this project."""
    root = repo_root()
    src = _claude_session_dir(root)
    if not src.exists():
        return []
    result = []
    for p in sorted(src.glob("*.jsonl")):
        size_mb = round(p.stat().st_size / 1_048_576, 2)
        already = (tasks_dir() / p.stem).exists()
        # Peek at ai-title
        title = ""
        try:
            records = _load_jsonl(p)
            titles = [r.get("aiTitle", "") for r in records if r.get("type") == "ai-title" and r.get("aiTitle")]
            title = titles[0] if titles else ""
        except Exception:
            pass
        result.append({"session_id": p.stem, "size_mb": size_mb, "title": title, "harvested": already})
    return result


def list_claude_subagents(session_id: str) -> list[dict[str, Any]]:
    root = repo_root()
    src = _claude_session_dir(root) / session_id / "subagents"
    if not src.exists():
        return []
    result = []
    for f in sorted(src.glob("agent-*.jsonl")):
        agent_id = f.stem.replace("agent-", "")
        meta_f = f.with_suffix("").with_suffix(".meta.json")
        desc, atype = "", ""
        if meta_f.exists():
            m = json.loads(meta_f.read_text(encoding="utf-8"))
            desc, atype = m.get("description", ""), m.get("agentType", "")
        result.append({"agent_id": agent_id, "description": desc, "agent_type": atype})
    return result


# ---------------------------------------------------------------------------
# Anthropic API wrapper
# ---------------------------------------------------------------------------

class AnthropicLogger:
    """
    Wrap an anthropic.Anthropic client to auto-log every messages.create() call.

    Usage:
        logger = AnthropicLogger(task_description="Search repo for patterns")
        client = logger.wrap(anthropic.Anthropic())
        response = client.messages.create(...)
        logger.end(outcome="success", notes="Found 3 matches")
    """

    def __init__(self, task_description: str = "", model: str = "") -> None:
        self.task = Task.create(
            description=task_description,
            framework="anthropic",
            model=model,
        )

    def wrap(self, client: Any) -> Any:
        """Return a wrapped client that logs all messages.create() calls."""
        logger_task = self.task

        class _Messages:
            def __init__(self, original: Any) -> None:
                self._orig = original

            def create(self, **kwargs: Any) -> Any:
                # Log the incoming user/system messages
                for msg in kwargs.get("messages", []):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        content = [{"type": "text", "text": content}]
                    logger_task.log(
                        role=role,
                        content=content,
                        model=kwargs.get("model", ""),
                        timestamp=_now(),
                    )

                response = self._orig.create(**kwargs)

                # Log the assistant response
                model_name = getattr(response, "model", kwargs.get("model", ""))
                usage_obj = getattr(response, "usage", None)
                usage = {}
                if usage_obj:
                    usage = {
                        "input_tokens": getattr(usage_obj, "input_tokens", 0),
                        "output_tokens": getattr(usage_obj, "output_tokens", 0),
                        "cache_read_input_tokens": getattr(usage_obj, "cache_read_input_tokens", 0),
                    }
                content_blocks = []
                thinking = ""
                for blk in getattr(response, "content", []):
                    btype = getattr(blk, "type", "")
                    if btype == "thinking":
                        thinking = getattr(blk, "thinking", "")
                        content_blocks.append({"type": "thinking", "thinking": thinking})
                    elif btype == "text":
                        content_blocks.append({"type": "text", "text": getattr(blk, "text", "")})
                    elif btype == "tool_use":
                        content_blocks.append({
                            "type": "tool_use",
                            "id": getattr(blk, "id", ""),
                            "name": getattr(blk, "name", ""),
                            "input": getattr(blk, "input", {}),
                        })

                logger_task.log(
                    role="assistant",
                    content=content_blocks,
                    model=model_name,
                    usage=usage,
                    thinking=thinking,
                    timestamp=_now(),
                )

                return response

        class _WrappedClient:
            def __init__(self, orig: Any) -> None:
                self.messages = _Messages(orig.messages)
                self._orig = orig

            def __getattr__(self, name: str) -> Any:
                return getattr(self._orig, name)

        return _WrappedClient(client)

    def end(
        self,
        outcome: str = "",
        notes: str = "",
        tags: list[str] | None = None,
    ) -> Path:
        return self.task.end(outcome=outcome, notes=notes, tags=tags or [])


# ---------------------------------------------------------------------------
# OpenAI API wrapper
# ---------------------------------------------------------------------------

class OpenAILogger:
    """
    Wrap an openai.OpenAI client to auto-log every chat.completions.create() call.

    Normalises OpenAI format to Anthropic Messages API block format.

    Usage:
        logger = OpenAILogger(task_description="Generate poem outline")
        client = logger.wrap(openai.OpenAI())
        response = client.chat.completions.create(...)
        logger.end(outcome="success")
    """

    def __init__(self, task_description: str = "", model: str = "") -> None:
        self.task = Task.create(
            description=task_description,
            framework="openai",
            model=model,
        )

    @staticmethod
    def _openai_msg_to_blocks(msg: dict) -> list[dict]:
        role = msg.get("role", "")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", []) or []

        blocks: list[dict] = []
        if isinstance(content, str) and content:
            blocks.append({"type": "text", "text": content})
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    blocks.append({"type": "text", "text": part.get("text", "")})

        for tc in tool_calls:
            fn = tc.get("function", {}) if isinstance(tc, dict) else {}
            blocks.append({
                "type": "tool_use",
                "id": tc.get("id", "") if isinstance(tc, dict) else getattr(tc, "id", ""),
                "name": fn.get("name", "") if isinstance(fn, dict) else getattr(fn, "name", ""),
                "input": _safe_json(fn.get("arguments", "{}") if isinstance(fn, dict) else getattr(fn, "arguments", "{}")),
            })

        # Tool result messages
        if role == "tool":
            blocks = [{
                "type": "tool_result",
                "tool_use_id": msg.get("tool_call_id", ""),
                "content": str(content)[:8000],
            }]

        return blocks

    def wrap(self, client: Any) -> Any:
        logger_task = self.task
        openai_to_blocks = self._openai_msg_to_blocks

        class _Completions:
            def __init__(self, orig: Any) -> None:
                self._orig = orig

            def create(self, **kwargs: Any) -> Any:
                for msg in kwargs.get("messages", []):
                    role = msg.get("role", "user")
                    if role == "assistant":
                        continue  # log from response instead
                    blocks = openai_to_blocks(msg)
                    if blocks:
                        logger_task.log(role="user" if role in ("user", "tool", "system") else role,
                                        content=blocks, model=kwargs.get("model", ""), timestamp=_now())

                response = self._orig.create(**kwargs)

                # Log assistant response
                choices = getattr(response, "choices", [])
                usage_obj = getattr(response, "usage", None)
                usage = {}
                if usage_obj:
                    usage = {
                        "input_tokens": getattr(usage_obj, "prompt_tokens", 0),
                        "output_tokens": getattr(usage_obj, "completion_tokens", 0),
                        "cache_read_input_tokens": 0,
                    }
                model_name = getattr(response, "model", kwargs.get("model", ""))
                for choice in choices:
                    msg_obj = getattr(choice, "message", None)
                    if msg_obj is None:
                        continue
                    msg_dict = {
                        "role": getattr(msg_obj, "role", "assistant"),
                        "content": getattr(msg_obj, "content", "") or "",
                        "tool_calls": getattr(msg_obj, "tool_calls", []) or [],
                    }
                    blocks = openai_to_blocks(msg_dict)
                    if blocks:
                        logger_task.log(role="assistant", content=blocks, model=model_name,
                                        usage=usage, timestamp=_now())

                return response

        class _Chat:
            def __init__(self, orig: Any) -> None:
                self.completions = _Completions(orig.completions)

        class _WrappedClient:
            def __init__(self, orig: Any) -> None:
                self.chat = _Chat(orig.chat)
                self._orig = orig

            def __getattr__(self, name: str) -> Any:
                return getattr(self._orig, name)

        return _WrappedClient(client)

    def end(self, outcome: str = "", notes: str = "", tags: list[str] | None = None) -> Path:
        return self.task.end(outcome=outcome, notes=notes, tags=tags or [])


def _safe_json(s: str | Any) -> Any:
    if isinstance(s, str):
        try:
            return json.loads(s)
        except Exception:
            return s
    return s


# ---------------------------------------------------------------------------
# Dataset builder (reads tasks/*, outputs train.jsonl + eval.jsonl)
# ---------------------------------------------------------------------------

def build_dataset(
    output_dir: Path | None = None,
    split: float = 0.9,
    include_failures: bool = False,
    no_metadata: bool = False,
    seed: int = 42,
) -> tuple[int, int]:
    """Build fine-tuning JSONL from all tasks marked include: true."""
    import yaml as _yaml

    td = tasks_dir()
    out = output_dir or dataset_dir()
    out.mkdir(parents=True, exist_ok=True)

    examples: list[dict] = []

    for task_dir in sorted(td.iterdir()):
        task_yaml = task_dir / "task.yaml"
        if not task_yaml.exists():
            continue

        meta = _yaml.safe_load(task_yaml.read_text(encoding="utf-8")) or {}
        outcome = str(meta.get("outcome", "")).lower()
        include = meta.get("include", False)

        if not include:
            continue
        if outcome == "failure" and not include_failures:
            continue

        msgs_path = task_dir / "messages.jsonl"
        if not msgs_path.exists():
            continue

        messages = [json.loads(l) for l in msgs_path.read_text(encoding="utf-8").splitlines() if l.strip()]

        # Build Messages-API-compatible conversation
        conv = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", [])
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            conv.append({"role": role, "content": content})

        example: dict[str, Any] = {"messages": conv}
        if not no_metadata:
            example["_metadata"] = {
                "task_id": meta.get("task_id", task_dir.name),
                "framework": meta.get("framework", ""),
                "model": meta.get("model", ""),
                "outcome": outcome,
                "description": meta.get("description", ""),
                "job_type": meta.get("job_type", ""),
                "tags": meta.get("tags", []),
                "notes": meta.get("notes", ""),
            }

        examples.append(example)

    if not examples:
        return 0, 0

    rng = random.Random(seed)
    rng.shuffle(examples)
    split_idx = int(len(examples) * split)
    train, eval_ = examples[:split_idx], examples[split_idx:]

    (out / "train.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in train), encoding="utf-8"
    )
    (out / "eval.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in eval_), encoding="utf-8"
    )
    return len(train), len(eval_)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_end(args: argparse.Namespace) -> int:
    """End a task: harvest most recent Claude Code session and mark it complete."""
    print("Harvesting most recent Claude Code session...")
    try:
        task = harvest_claude_session(
            session_id=getattr(args, "session", None),
            description=args.description or "",
        )
    except Exception as e:
        print(f"ERROR harvesting session: {e}")
        return 1

    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    task_dir = task.end(
        outcome=args.outcome or "",
        description=args.description or task.description,
        notes=args.notes or "",
        tags=tags,
    )

    print(f"Task saved: {task_dir}")
    print(f"  ID:          {task.task_id}")
    print(f"  Framework:   {task.framework}")
    print(f"  Outcome:     {task.outcome or '(not set)'}")
    print(f"  Messages:    {len(task.messages)}")

    with open(task_dir / "analysis.json", encoding="utf-8") as f:
        a = json.load(f)
    print(f"  Narrative:   {a['narrative']}")
    print()
    print(f"Edit task.yaml to set 'include: true' when ready to add to dataset.")
    print(f"Then: python machinery/tools/task_logger.py build")
    return 0


def cmd_harvest(args: argparse.Namespace) -> int:
    """Harvest a Claude Code session into a task (no end marker, no outcome)."""
    sid = getattr(args, "session", None)
    agent_id = getattr(args, "subagent", None)
    try:
        task = harvest_claude_session(
            session_id=sid,
            subagent_id=agent_id,
            description=getattr(args, "description", "") or "",
        )
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

    task_dir = task.save()
    print(f"Harvested -> {task_dir}")
    with open(task_dir / "analysis.json", encoding="utf-8") as f:
        a = json.load(f)
    print(f"  {a['narrative']}")
    print(f"  Flagged turns: {a['flagged_count']}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    """List tasks and Claude Code sessions."""
    td = tasks_dir()
    print("=== Recorded tasks ===")
    if td.exists():
        for task_dir in sorted(td.iterdir()):
            ty = task_dir / "task.yaml"
            if not ty.exists():
                continue
            try:
                import yaml as _yaml
                meta = _yaml.safe_load(ty.read_text(encoding="utf-8")) or {}
                inc = "+" if meta.get("include") else " "
                outcome = meta.get("outcome", "")[:7] or "unlabeled"
                desc = (meta.get("description", "") or "")[:50]
                fw = meta.get("framework", "")[:15]
                print(f"  [{inc}] {task_dir.name[:36]}  {outcome:9}  {fw:16}  {desc}")
            except Exception:
                print(f"  [ ] {task_dir.name}  (unreadable)")
    else:
        print("  (none)")

    print()
    print("=== Claude Code sessions ===")
    for s in list_claude_sessions():
        done = "+" if s["harvested"] else " "
        title = (s["title"] or "")[:50]
        print(f"  [{done}] {s['session_id']}  {s['size_mb']:5.1f} MB  {title}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Build fine-tuning dataset from labeled tasks."""
    out = Path(args.output) if getattr(args, "output", None) else dataset_dir()
    split = float(getattr(args, "split", 0.9))
    n_train, n_eval = build_dataset(
        output_dir=out,
        split=split,
        include_failures=getattr(args, "include_failures", False),
        no_metadata=getattr(args, "no_metadata", False),
    )
    if n_train + n_eval == 0:
        print("No labeled tasks found. Edit task.yaml files and set 'include: true'.")
        return 1
    print(f"Dataset written to {out}/")
    print(f"  train.jsonl: {n_train} examples")
    print(f"  eval.jsonl:  {n_eval} examples")
    print()
    print("Strip _metadata before submitting to Anthropic:")
    print("  python machinery/tools/task_logger.py build --no-metadata")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Model-agnostic task logger for fine-tuning data collection.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="command", required=True)

    # end
    end_p = sub.add_parser("end", help="End a task: harvest + mark complete.")
    end_p.add_argument("--session", help="Claude Code session ID (default: most recent)")
    end_p.add_argument("--description", "-d", default="", help="One-sentence task description")
    end_p.add_argument("--outcome", "-o", default="", choices=["success", "partial", "failure", ""],
                       help="Task outcome")
    end_p.add_argument("--notes", "-n", default="", help="What went right/wrong")
    end_p.add_argument("--tags", "-t", default="", help="Comma-separated tags")

    # harvest
    h_p = sub.add_parser("harvest", help="Harvest a session without ending it.")
    h_p.add_argument("--session", help="Claude Code session ID (default: most recent)")
    h_p.add_argument("--subagent", help="Subagent ID (harvest only this subagent)")
    h_p.add_argument("--description", "-d", default="")

    # list
    sub.add_parser("list", help="List tasks and sessions.")

    # build
    b_p = sub.add_parser("build", help="Build fine-tuning dataset.")
    b_p.add_argument("--output", default="", help="Output directory")
    b_p.add_argument("--split", type=float, default=0.9, help="Train/eval split (default: 0.9)")
    b_p.add_argument("--include-failures", action="store_true")
    b_p.add_argument("--no-metadata", action="store_true",
                     help="Strip _metadata fields (required for Anthropic submission)")

    args = p.parse_args()

    dispatch = {
        "end": cmd_end,
        "harvest": cmd_harvest,
        "list": cmd_list,
        "build": cmd_build,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
