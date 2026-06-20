#!/usr/bin/env python3
"""
harvest_sessions.py — Extract and annotate Claude Code session transcripts.

Reads ~/.claude/projects/<slug>/<session-id>.jsonl and all subagent JSONL files,
reconstructs conversation sequences, runs heuristic quality analysis, and writes
structured output to logs/raw/<session-id>/.

Run at session end to capture the latest turns. The --update flag re-harvests
sessions that were already processed (use after adding new turns to an ongoing
session).

Usage:
    python tools/harvest_sessions.py            # harvest most recent session
    python tools/harvest_sessions.py --update   # re-harvest most recent (new turns)
    python tools/harvest_sessions.py --all      # harvest all sessions
    python tools/harvest_sessions.py --all --update
    python tools/harvest_sessions.py --list
    python tools/harvest_sessions.py --session <id>

Output per session (logs/raw/<session-id>/):
    main_conversation.jsonl   Messages-API conversation (main session, non-sidechain)
    subagents/<id>.jsonl      One file per subagent conversation
    summary.yaml              Label template + auto-populated heuristic signals
    stats.json                Token counts, turn counts, timestamps

After harvesting:
    1. Review logs/raw/<session-id>/summary.yaml
    2. Copy to logs/labels/<session-id>.yaml
    3. Fill in: outcome, task_description, notes, which subagents to include
    4. Run: python tools/build_dataset.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
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


def claude_projects_dir() -> Path:
    return Path.home() / ".claude" / "projects"


def project_slug(root: Path) -> str:
    """C:\\Users\\rberr\\Desktop\\Texgraph -> c--Users-rberr-Desktop-Texgraph"""
    drive, rest = str(root).replace("\\", "/").split(":", 1)
    return drive.lower() + "-" + rest.replace("/", "-")


def session_dir(root: Path) -> Path:
    return claude_projects_dir() / project_slug(root)


# ---------------------------------------------------------------------------
# JSONL loading
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def messages_from_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    msgs = [r for r in records if r.get("type") in ("user", "assistant")]
    return sorted(msgs, key=lambda r: r.get("timestamp", ""))


def content_from_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    msg = record.get("message", {})
    content = msg.get("content", [])
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return content if isinstance(content, list) else []


# ---------------------------------------------------------------------------
# Conversation reconstruction (Messages API format)
# ---------------------------------------------------------------------------

def build_conversation(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Reconstruct a Messages-API-compatible conversation from JSONL records.
    Strips thinking signature fields (not transferable across sessions).
    Truncates large tool results to 8000 chars.
    """
    msgs = messages_from_records(records)
    conversation: list[dict[str, Any]] = []

    for record in msgs:
        role = record.get("message", {}).get("role")
        if role not in ("user", "assistant"):
            continue

        raw_content = content_from_record(record)
        clean: list[dict[str, Any]] = []

        for block in raw_content:
            btype = block.get("type")

            if btype == "thinking":
                clean.append({"type": "thinking", "thinking": block.get("thinking", "")})

            elif btype == "text":
                text = block.get("text", "").strip()
                if text:
                    clean.append({"type": "text", "text": text})

            elif btype == "tool_use":
                clean.append({
                    "type": "tool_use",
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "input": block.get("input", {}),
                })

            elif btype == "tool_result":
                result_content = block.get("content", "")
                if isinstance(result_content, list):
                    result_content = "\n".join(
                        b.get("text", "") for b in result_content if b.get("type") == "text"
                    )
                clean.append({
                    "type": "tool_result",
                    "tool_use_id": block.get("tool_use_id", ""),
                    "content": str(result_content)[:8000],
                })

        if clean:
            conversation.append({"role": role, "content": clean})

    return conversation


# ---------------------------------------------------------------------------
# Heuristic quality analysis
# ---------------------------------------------------------------------------

# Patterns that indicate a tool result contained an error
_ERROR_PATTERNS = re.compile(
    r"(Traceback \(most recent call last\)|Error:|Exception:|exit code [1-9]|"
    r"UnicodeDecodeError|ModuleNotFoundError|FileNotFoundError|KeyError|"
    r"AttributeError|PermissionError|is not recognized|cannot find|"
    r"failed with|FAILED|fatal:|ERROR\s)",
    re.IGNORECASE,
)

# Patterns in thinking blocks suggesting self-correction
_CORRECTION_PATTERNS = re.compile(
    r"\b(wait,|actually,|i was wrong|let me reconsider|incorrect|"
    r"i made an error|that's wrong|no, actually|hmm,|hold on|"
    r"i need to reconsider|i realize i|i should have|mistake)\b",
    re.IGNORECASE,
)

# Patterns in the final user turn suggesting success vs correction
_AFFIRMATION_PATTERNS = re.compile(
    r"^(ok|okay|good|great|perfect|thanks|thank you|done|got it|"
    r"looks good|that works|excellent|nice|yes|yep|sure)",
    re.IGNORECASE,
)
_CORRECTION_RESPONSE_PATTERNS = re.compile(
    r"^(but|no,|wait|that's wrong|not quite|actually|that's not|"
    r"incorrect|i don't think|can you|instead|try|wrong)",
    re.IGNORECASE,
)


@dataclass
class TurnSignal:
    uuid: str
    timestamp: str
    turn_index: int
    tool_calls: list[str] = field(default_factory=list)
    tool_errors: list[str] = field(default_factory=list)
    retried_tools: list[str] = field(default_factory=list)
    has_thinking: bool = False
    thinking_has_correction: bool = False
    thinking_snippet: str = ""
    is_high_complexity: bool = False   # >5 tool calls
    is_flagged: bool = False
    flag_reasons: list[str] = field(default_factory=list)


@dataclass
class SessionAnalysis:
    total_user_turns: int = 0
    total_assistant_turns: int = 0
    total_tool_calls: int = 0
    unique_tools_used: list[str] = field(default_factory=list)
    tool_call_counts: dict[str, int] = field(default_factory=dict)
    error_turn_count: int = 0
    retry_count: int = 0
    high_complexity_turn_count: int = 0
    self_correction_count: int = 0
    thinking_turn_count: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    start_timestamp: str = ""
    end_timestamp: str = ""
    ai_titles: list[str] = field(default_factory=list)
    final_user_sentiment: str = ""   # affirmative | corrective | neutral | n/a
    turn_signals: list[TurnSignal] = field(default_factory=list)
    flagged_turns: list[str] = field(default_factory=list)
    auto_narrative: str = ""
    error_samples: list[str] = field(default_factory=list)


def _extract_tool_result_text(block: dict[str, Any]) -> str:
    content = block.get("content", "")
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
    return str(content)


def analyze_conversation(records: list[dict[str, Any]]) -> SessionAnalysis:
    """
    Run heuristic analysis over JSONL records and return a SessionAnalysis.

    Detects:
    - Tool errors (patterns in tool results)
    - Tool retries (same tool called back-to-back in same context)
    - High complexity turns (>5 tool calls in one assistant turn)
    - Self-corrections in thinking blocks
    - Final user sentiment (affirmative vs corrective)
    - Token usage
    """
    analysis = SessionAnalysis()

    # Token totals
    for record in records:
        usage = record.get("message", {}).get("usage", {})
        analysis.input_tokens += usage.get("input_tokens", 0)
        analysis.output_tokens += usage.get("output_tokens", 0)
        analysis.cache_read_tokens += usage.get("cache_read_input_tokens", 0)

    # AI titles (deduplicated)
    titles = [r.get("aiTitle", "") for r in records if r.get("type") == "ai-title" and r.get("aiTitle")]
    analysis.ai_titles = list(dict.fromkeys(titles))

    # Timestamps
    timestamps = [r.get("timestamp", "") for r in records if r.get("timestamp")]
    if timestamps:
        analysis.start_timestamp = min(timestamps)
        analysis.end_timestamp = max(timestamps)

    msgs = messages_from_records(records)
    if not msgs:
        return analysis

    tool_counts: Counter[str] = Counter()

    user_turns = [m for m in msgs if m.get("message", {}).get("role") == "user"]
    asst_turns = [m for m in msgs if m.get("message", {}).get("role") == "assistant"]
    analysis.total_user_turns = len(user_turns)
    analysis.total_assistant_turns = len(asst_turns)

    # First pass: collect error tool_use_ids from user turns so we can
    # cross-reference them with assistant turns for retry detection.
    error_tool_use_ids: set[str] = set()
    for record in msgs:
        if record.get("message", {}).get("role") != "user":
            continue
        for block in content_from_record(record):
            if block.get("type") == "tool_result":
                result_text = _extract_tool_result_text(block)
                if _ERROR_PATTERNS.search(result_text):
                    error_tool_use_ids.add(block.get("tool_use_id", ""))

    # Second pass: build per-turn signals.
    # Retry = same tool called in consecutive assistant turns where the
    # first turn's matching tool call had an error result.
    prev_asst_tool_calls: list[tuple[str, str]] = []  # [(tool_use_id, tool_name)]
    prev_had_error = False

    for turn_idx, record in enumerate(msgs):
        role = record.get("message", {}).get("role")
        content = content_from_record(record)
        ts = record.get("timestamp", "")
        uuid = record.get("uuid", "")

        if role == "assistant":
            signal = TurnSignal(uuid=uuid, timestamp=ts, turn_index=turn_idx)
            turn_tool_calls: list[tuple[str, str]] = []  # (id, name)

            for block in content:
                btype = block.get("type")

                if btype == "thinking":
                    signal.has_thinking = True
                    analysis.thinking_turn_count += 1
                    thinking_text = block.get("thinking", "")
                    if _CORRECTION_PATTERNS.search(thinking_text):
                        signal.thinking_has_correction = True
                        analysis.self_correction_count += 1
                        m = _CORRECTION_PATTERNS.search(thinking_text)
                        if m:
                            start = max(0, m.start() - 60)
                            end = min(len(thinking_text), m.end() + 100)
                            signal.thinking_snippet = "..." + thinking_text[start:end].replace("\n", " ") + "..."

                elif btype == "tool_use":
                    name = block.get("name", "")
                    tid = block.get("id", "")
                    turn_tool_calls.append((tid, name))
                    tool_counts[name] += 1
                    analysis.total_tool_calls += 1

            signal.tool_calls = [name for _, name in turn_tool_calls]
            signal.is_high_complexity = len(turn_tool_calls) > 5
            if signal.is_high_complexity:
                analysis.high_complexity_turn_count += 1
                signal.is_flagged = True
                signal.flag_reasons.append(f"high_complexity:{len(turn_tool_calls)}_tool_calls")

            if signal.thinking_has_correction:
                signal.is_flagged = True
                signal.flag_reasons.append("self_correction_in_thinking")

            # Retry: previous assistant turn had an error AND this turn calls
            # the same tool name again
            if prev_had_error:
                prev_errored_names = {
                    name for tid, name in prev_asst_tool_calls
                    if tid in error_tool_use_ids
                }
                current_names = {name for _, name in turn_tool_calls}
                retried = prev_errored_names & current_names
                for t in retried:
                    signal.retried_tools.append(t)
                    analysis.retry_count += 1
                    signal.is_flagged = True
                    signal.flag_reasons.append(f"retry_after_error:{t}")

            prev_asst_tool_calls = turn_tool_calls
            prev_had_error = any(tid in error_tool_use_ids for tid, _ in turn_tool_calls)
            analysis.turn_signals.append(signal)

        elif role == "user":
            # Scan tool results for errors; annotate the most recent assistant signal
            turn_had_error = False
            for block in content:
                if block.get("type") == "tool_result":
                    result_text = _extract_tool_result_text(block)
                    if _ERROR_PATTERNS.search(result_text):
                        analysis.error_turn_count += 1
                        turn_had_error = True
                        if analysis.turn_signals:
                            sig = analysis.turn_signals[-1]
                            tid = block.get("tool_use_id", "")
                            matching_tool = next(
                                (name for i, name in enumerate(sig.tool_calls) if i == 0),
                                "unknown",
                            )
                            m = _ERROR_PATTERNS.search(result_text)
                            snippet = result_text[max(0, m.start()-20):m.end()+80].replace("\n", " ") if m else ""
                            sig.tool_errors.append(f"{matching_tool}: {snippet[:120]}")
                            sig.is_flagged = True
                            sig.flag_reasons.append(f"tool_error:{matching_tool}")
                            analysis.error_samples.append(snippet[:120])

    # Final user sentiment
    last_user = next(
        (m for m in reversed(msgs) if m.get("message", {}).get("role") == "user"),
        None,
    )
    if last_user:
        content = content_from_record(last_user)
        text = next((b.get("text", "") for b in content if b.get("type") == "text"), "")
        text = text.strip()
        if _AFFIRMATION_PATTERNS.match(text):
            analysis.final_user_sentiment = "affirmative"
        elif _CORRECTION_RESPONSE_PATTERNS.match(text):
            analysis.final_user_sentiment = "corrective"
        elif text:
            analysis.final_user_sentiment = "neutral"
        else:
            analysis.final_user_sentiment = "n/a"

    analysis.tool_call_counts = dict(tool_counts.most_common())
    analysis.unique_tools_used = list(tool_counts.keys())
    analysis.flagged_turns = [s.uuid for s in analysis.turn_signals if s.is_flagged]

    # Auto narrative
    parts: list[str] = []
    parts.append(f"{analysis.total_user_turns} user turns, {analysis.total_assistant_turns} assistant turns.")
    parts.append(f"{analysis.total_tool_calls} tool calls across {len(analysis.unique_tools_used)} tools.")
    if analysis.error_turn_count:
        parts.append(f"{analysis.error_turn_count} tool error(s) detected.")
    if analysis.retry_count:
        parts.append(f"{analysis.retry_count} tool retry(s) detected.")
    if analysis.self_correction_count:
        parts.append(f"{analysis.self_correction_count} self-correction(s) in thinking.")
    if analysis.high_complexity_turn_count:
        parts.append(f"{analysis.high_complexity_turn_count} high-complexity turn(s) (>5 tool calls).")
    if analysis.final_user_sentiment:
        parts.append(f"Final user response: {analysis.final_user_sentiment}.")
    parts.append(f"Tokens: {analysis.output_tokens} out / {analysis.input_tokens} in / {analysis.cache_read_tokens} cache-read.")
    analysis.auto_narrative = " ".join(parts)

    return analysis


# ---------------------------------------------------------------------------
# Summary YAML generation
# ---------------------------------------------------------------------------

def _indent(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def _yaml_list(items: list[Any], indent: int = 2) -> str:
    if not items:
        return "[]"
    pad = " " * indent
    return "\n" + "\n".join(f"{pad}- {json.dumps(item)}" for item in items)


def write_summary(
    session_id: str,
    analysis: SessionAnalysis,
    subagent_meta: list[dict[str, Any]],
    out_dir: Path,
) -> None:
    """Write the summary.yaml label template with auto-populated signal fields."""
    date = analysis.start_timestamp[:10] if analysis.start_timestamp else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ai_title = analysis.ai_titles[0] if analysis.ai_titles else ""

    # Format flagged turns block
    flagged_lines: list[str] = []
    for sig in analysis.turn_signals:
        if sig.is_flagged:
            reasons = ", ".join(sig.flag_reasons)
            line = f"  - uuid: \"{sig.uuid}\"\n    reasons: [{reasons}]"
            if sig.tool_errors:
                line += f"\n    errors:\n" + "\n".join(f"      - {json.dumps(e)}" for e in sig.tool_errors[:3])
            if sig.thinking_snippet:
                snippet = sig.thinking_snippet[:100].replace('"', "'")
                line += f"\n    thinking_snippet: \"{snippet}\""
            flagged_lines.append(line)
    flagged_block = "\n".join(flagged_lines) if flagged_lines else "  []"

    # Format subagent entries
    sa_lines: list[str] = []
    for m in subagent_meta:
        aid = m.get("agent_id", "")
        desc = m.get("description", "").replace('"', "'")
        atype = m.get("agentType", "")
        turns = m.get("turn_count", "?")
        sa_ana = m.get("analysis")
        sa_narrative = sa_ana.auto_narrative if sa_ana else ""
        sa_errors = sa_ana.error_turn_count if sa_ana else 0
        block = (
            f"  - agent_id: \"{aid}\"\n"
            f"    description: \"{desc}\"\n"
            f"    agent_type: \"{atype}\"\n"
            f"    turns: {turns}\n"
            f"    auto_narrative: \"{sa_narrative}\"\n"
            f"    tool_errors: {sa_errors}\n"
            f"    # success | partial | failure\n"
            f"    outcome: \"\"\n"
            f"    include: false"
        )
        sa_lines.append(block)
    sa_block = "\n".join(sa_lines) if sa_lines else "  []"

    tool_counts_yaml = "\n".join(
        f"    {tool}: {count}"
        for tool, count in list(analysis.tool_call_counts.items())[:15]
    ) or "    {}"

    summary = f"""\
# Session label: {session_id}
# Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
#
# WORKFLOW:
#   1. Review auto_signals below — they are regenerated each harvest, do not edit them
#   2. Fill in the HUMAN ANNOTATION section
#   3. Copy this file to logs/labels/{session_id}.yaml
#   4. Run: python tools/build_dataset.py

session_id: "{session_id}"
date: "{date}"
ai_title: "{ai_title}"

# =============================================================================
# AUTO SIGNALS (regenerated each harvest — do not edit)
# =============================================================================
auto_signals:
  narrative: "{analysis.auto_narrative}"
  turns:
    user: {analysis.total_user_turns}
    assistant: {analysis.total_assistant_turns}
    thinking_present: {analysis.thinking_turn_count}
    high_complexity: {analysis.high_complexity_turn_count}
  tools:
    total_calls: {analysis.total_tool_calls}
    unique_count: {len(analysis.unique_tools_used)}
    call_counts:
{tool_counts_yaml}
  quality_signals:
    tool_errors: {analysis.error_turn_count}
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
# HUMAN ANNOTATION (fill these in)
# =============================================================================

# What was the primary task? One sentence.
task_description: ""

# success | partial | failure
# success  = goal achieved, output correct and complete
# partial  = progress made, incomplete or one element wrong
# failure  = did not achieve goal, wrong output, hallucinated, or abandoned
outcome: ""

# Pipeline stage or job type
# e.g.: tooling, pipeline/ingest, pipeline/transcribe, conversation, research
job_type: ""

# Include the main session conversation in the dataset?
# (subagents are controlled individually below)
include_main_session: false

# Free-form notes — explain what went right/wrong, what a better approach
# would have been, anything that should inform fine-tuning
notes: ""

# Tags for filtering downstream
# e.g.: [multi-step, file-edit, search, debugging, refactor, scaffold]
tags: []

# =============================================================================
# SUBAGENTS
# =============================================================================
subagents:
{sa_block}
"""

    (out_dir / "summary.yaml").write_text(summary, encoding="utf-8")

    # Also write stats.json with just the numbers
    stats = {
        "session_id": session_id,
        "date": date,
        "ai_title": ai_title,
        "turns": {"user": analysis.total_user_turns, "assistant": analysis.total_assistant_turns},
        "tokens": {"input": analysis.input_tokens, "output": analysis.output_tokens, "cache_read": analysis.cache_read_tokens},
        "tool_errors": analysis.error_turn_count,
        "retries": analysis.retry_count,
        "self_corrections": analysis.self_correction_count,
        "high_complexity_turns": analysis.high_complexity_turn_count,
        "flagged_turn_count": len(analysis.flagged_turns),
        "final_user_sentiment": analysis.final_user_sentiment,
        "subagent_count": len(subagent_meta),
    }
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Harvest one session
# ---------------------------------------------------------------------------

def harvest_session(session_id: str, src_dir: Path, logs_raw: Path) -> None:
    main_jsonl = src_dir / f"{session_id}.jsonl"
    if not main_jsonl.exists():
        print(f"  [skip] no JSONL: {main_jsonl.name}")
        return

    out_dir = logs_raw / session_id
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  loading {main_jsonl.name} ...", end=" ", flush=True)
    records = load_jsonl(main_jsonl)
    print(f"{len(records)} records")

    # Main conversation (non-sidechain only)
    main_records = [r for r in records if not r.get("isSidechain")]
    conv = build_conversation(main_records)
    (out_dir / "main_conversation.jsonl").write_text(
        "\n".join(json.dumps(m, ensure_ascii=False) for m in conv),
        encoding="utf-8",
    )

    # Analyze main conversation
    analysis = analyze_conversation(main_records)

    # Subagents
    subagent_dir = src_dir / session_id / "subagents"
    subagent_meta: list[dict[str, Any]] = []

    if subagent_dir.exists():
        sa_out_dir = out_dir / "subagents"
        sa_out_dir.mkdir(exist_ok=True)

        seen_ids: set[str] = set()

        for meta_file in sorted(subagent_dir.glob("*.meta.json")):
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            agent_id = meta_file.stem.replace(".meta", "").replace("agent-", "")
            meta["agent_id"] = agent_id
            seen_ids.add(agent_id)

            sa_jsonl = subagent_dir / f"agent-{agent_id}.jsonl"
            if sa_jsonl.exists():
                sa_records = load_jsonl(sa_jsonl)
                sa_conv = build_conversation(sa_records)
                (sa_out_dir / f"{agent_id}.jsonl").write_text(
                    "\n".join(json.dumps(m, ensure_ascii=False) for m in sa_conv),
                    encoding="utf-8",
                )
                meta["turn_count"] = len(sa_conv)
                meta["analysis"] = analyze_conversation(sa_records)

            subagent_meta.append(meta)

        for sa_jsonl in sorted(subagent_dir.glob("agent-*.jsonl")):
            agent_id = sa_jsonl.stem.replace("agent-", "")
            if agent_id not in seen_ids:
                sa_records = load_jsonl(sa_jsonl)
                sa_conv = build_conversation(sa_records)
                (sa_out_dir / f"{agent_id}.jsonl").write_text(
                    "\n".join(json.dumps(m, ensure_ascii=False) for m in sa_conv),
                    encoding="utf-8",
                )
                sa_analysis = analyze_conversation(sa_records)
                subagent_meta.append({
                    "agent_id": agent_id,
                    "description": "",
                    "agentType": "",
                    "turn_count": len(sa_conv),
                    "analysis": sa_analysis,
                })

    write_summary(session_id, analysis, subagent_meta, out_dir)

    flags = len(analysis.flagged_turns)
    print(
        f"  turns={analysis.total_user_turns} "
        f"tools={analysis.total_tool_calls} "
        f"errors={analysis.error_turn_count} "
        f"retries={analysis.retry_count} "
        f"corrections={analysis.self_correction_count} "
        f"flagged={flags} "
        f"sentiment={analysis.final_user_sentiment}"
    )
    print(f"  subagents={len(subagent_meta)}  out -> logs/raw/{session_id}/")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def list_sessions(src_dir: Path) -> list[str]:
    return [p.stem for p in sorted(src_dir.glob("*.jsonl"))]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Harvest and annotate Claude Code session transcripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--session", metavar="ID", help="Harvest a specific session.")
    parser.add_argument("--all", action="store_true", help="Harvest all sessions.")
    parser.add_argument("--update", action="store_true",
                        help="Re-harvest sessions already in logs/raw/ (pick up new turns).")
    parser.add_argument("--list", action="store_true",
                        help="List available sessions and exit.")
    args = parser.parse_args()

    root = repo_root()
    src_dir = session_dir(root)
    logs_raw = root / "logs" / "raw"
    logs_raw.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        print(f"ERROR: session directory not found: {src_dir}")
        return 1

    sessions = list_sessions(src_dir)

    if args.list:
        print(f"Sessions for {project_slug(root)}:")
        for s in sessions:
            done = "+" if (logs_raw / s).exists() else " "
            size_mb = round((src_dir / f"{s}.jsonl").stat().st_size / 1_048_576, 2)
            print(f"  [{done}] {s}  ({size_mb} MB)")
        return 0

    if not sessions:
        print("No sessions found.")
        return 0

    if args.session:
        target = [args.session]
    elif args.all:
        target = sessions
    else:
        target = [sessions[-1]]

    if not args.update:
        target = [s for s in target if not (logs_raw / s).exists()]

    if not target:
        print("Nothing new to harvest. Use --update to re-process existing sessions.")
        return 0

    for session_id in target:
        print(f"\nHarvesting: {session_id}")
        harvest_session(session_id, src_dir, logs_raw)

    print("\nDone.")
    print("Next: copy logs/raw/<id>/summary.yaml to logs/labels/<id>.yaml, fill in outcome + notes.")
    print("Then: python tools/build_dataset.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
