#!/usr/bin/env python3
"""
build_dataset.py — Build Anthropic fine-tuning JSONL from labeled session logs.

Reads logs/labels/<session-id>.yaml for task outcomes and filters, then
converts the corresponding logs/raw/<session-id>/ conversation files into
Anthropic fine-tuning format.

Usage:
    python machinery/tools/build_dataset.py
    python machinery/tools/build_dataset.py --output logs/dataset/
    python machinery/tools/build_dataset.py --split 0.9
    python machinery/tools/build_dataset.py --include-failures
    python machinery/tools/build_dataset.py --only-subagents
    python machinery/tools/build_dataset.py --stats

Fine-tuning format (one JSON object per line):
    {"messages": [{"role": "user", "content": [...]}, {"role": "assistant", "content": [...]}]}

Each training example is a complete conversation (main session or subagent).
Examples with outcome=failure are excluded by default but can be included for
negative examples. Use --include-failures to include them tagged with metadata.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot locate repo root.")


# ---------------------------------------------------------------------------
# Label loading
# ---------------------------------------------------------------------------

def load_label(label_path: Path) -> dict[str, Any]:
    with open(label_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def label_outcome(label: dict[str, Any]) -> str:
    return str(label.get("outcome", "")).lower()


# ---------------------------------------------------------------------------
# Conversation loading
# ---------------------------------------------------------------------------

def load_conversation(jsonl_path: Path) -> list[dict[str, Any]]:
    messages = []
    with open(jsonl_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return messages


def conversation_is_valid(messages: list[dict[str, Any]]) -> bool:
    """A valid conversation has at least one user and one assistant turn."""
    roles = {m.get("role") for m in messages}
    return "user" in roles and "assistant" in roles


# ---------------------------------------------------------------------------
# Fine-tuning example construction
# ---------------------------------------------------------------------------

def make_example(
    messages: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one fine-tuning example. Optionally embed metadata as a comment."""
    example: dict[str, Any] = {"messages": messages}
    if metadata:
        example["_metadata"] = metadata  # non-standard; strip before submitting if needed
    return example


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------

def process_label(
    label: dict[str, Any],
    raw_dir: Path,
    include_failures: bool,
    only_subagents: bool,
) -> list[dict[str, Any]]:
    """Return a list of fine-tuning examples from one labeled session."""
    session_id = label.get("session_id", "")
    session_raw = raw_dir / session_id
    if not session_raw.exists():
        print(f"  [skip] raw data missing for {session_id}")
        return []

    examples: list[dict[str, Any]] = []
    outcome = label_outcome(label)

    # ---- Main session ----
    if not only_subagents and label.get("include_main_session"):
        main_jsonl = session_raw / "main_conversation.jsonl"
        if main_jsonl.exists():
            messages = load_conversation(main_jsonl)
            if conversation_is_valid(messages) and (outcome != "failure" or include_failures):
                examples.append(make_example(messages, metadata={
                    "session_id": session_id,
                    "source": "main",
                    "outcome": outcome,
                    "task_description": label.get("task_description", ""),
                    "job_type": label.get("job_type", ""),
                    "tags": label.get("tags", []),
                }))

    # ---- Subagents ----
    sa_dir = session_raw / "subagents"
    if sa_dir.exists():
        subagent_labels = {
            sa.get("agent_id", ""): sa
            for sa in label.get("subagents", [])
        }

        for sa_jsonl in sorted(sa_dir.glob("*.jsonl")):
            agent_id = sa_jsonl.stem
            sa_label = subagent_labels.get(agent_id, {})
            sa_outcome = str(sa_label.get("outcome", "")).lower()
            should_include = sa_label.get("include", False)

            if not should_include:
                continue
            if sa_outcome == "failure" and not include_failures:
                continue

            messages = load_conversation(sa_jsonl)
            if not conversation_is_valid(messages):
                continue

            # Find matching meta
            meta_file = session_raw / "subagents" / f"{agent_id}.meta.json" if False else None
            meta: dict[str, Any] = {
                "session_id": session_id,
                "agent_id": agent_id,
                "source": "subagent",
                "outcome": sa_outcome,
                "description": sa_label.get("description", ""),
                "agent_type": sa_label.get("agent_type", ""),
            }

            examples.append(make_example(messages, metadata=meta))

    return examples


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def print_stats(examples: list[dict[str, Any]]) -> None:
    total = len(examples)
    by_outcome: dict[str, int] = {}
    by_source: dict[str, int] = {}
    total_turns = 0

    for ex in examples:
        meta = ex.get("_metadata", {})
        outcome = meta.get("outcome", "unknown")
        source = meta.get("source", "unknown")
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
        by_source[source] = by_source.get(source, 0) + 1
        total_turns += len(ex.get("messages", []))

    print(f"\nDataset stats:")
    print(f"  Total examples:  {total}")
    print(f"  Total turns:     {total_turns}")
    print(f"  By outcome:      {by_outcome}")
    print(f"  By source:       {by_source}")
    print(f"  Avg turns/ex:    {total_turns / total:.1f}" if total else "  (no examples)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Anthropic fine-tuning JSONL from labeled session logs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--output", default="logs/dataset",
                        help="Output directory (default: logs/dataset)")
    parser.add_argument("--split", type=float, default=0.9,
                        help="Train/eval split fraction (default: 0.9)")
    parser.add_argument("--include-failures", action="store_true",
                        help="Include failure-labeled examples (default: excluded)")
    parser.add_argument("--only-subagents", action="store_true",
                        help="Only include subagent conversations")
    parser.add_argument("--no-metadata", action="store_true",
                        help="Strip _metadata fields from output (required for Anthropic submission)")
    parser.add_argument("--stats", action="store_true",
                        help="Print dataset stats and exit without writing files")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for train/eval split (default: 42)")
    args = parser.parse_args()

    root = repo_root()
    labels_dir = root / "logs" / "labels"
    raw_dir = root / "logs" / "raw"
    out_dir = root / Path(args.output)

    label_files = sorted(labels_dir.glob("*.yaml"))
    if not label_files:
        print(f"No label files found in {labels_dir}")
        print("Run harvest_sessions.py first, then fill in logs/labels/<session-id>.yaml")
        return 1

    print(f"Found {len(label_files)} label file(s).")

    all_examples: list[dict[str, Any]] = []

    for label_file in label_files:
        label = load_label(label_file)
        session_id = label.get("session_id", label_file.stem)
        print(f"\nProcessing: {session_id}")

        examples = process_label(
            label=label,
            raw_dir=raw_dir,
            include_failures=args.include_failures,
            only_subagents=args.only_subagents,
        )

        print(f"  → {len(examples)} example(s)")
        all_examples.extend(examples)

    if not all_examples:
        print("\nNo examples to write. Check that label files have include=true fields set.")
        return 0

    if args.stats:
        print_stats(all_examples)
        return 0

    # Strip metadata if requested
    if args.no_metadata:
        for ex in all_examples:
            ex.pop("_metadata", None)

    # Shuffle and split
    rng = random.Random(args.seed)
    rng.shuffle(all_examples)
    split_idx = int(len(all_examples) * args.split)
    train = all_examples[:split_idx]
    eval_ = all_examples[split_idx:]

    # Write
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "train.jsonl"
    eval_path = out_dir / "eval.jsonl"

    train_path.write_text(
        "\n".join(json.dumps(ex, ensure_ascii=False) for ex in train),
        encoding="utf-8",
    )
    eval_path.write_text(
        "\n".join(json.dumps(ex, ensure_ascii=False) for ex in eval_),
        encoding="utf-8",
    )

    print_stats(all_examples)
    print(f"\nWrote:")
    print(f"  train ({len(train)} examples): {train_path}")
    print(f"  eval  ({len(eval_)} examples): {eval_path}")
    print("\nNote: strip _metadata fields before submitting to Anthropic fine-tuning API.")
    print("  python machinery/tools/build_dataset.py --no-metadata")

    return 0


if __name__ == "__main__":
    sys.exit(main())
