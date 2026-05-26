#!/usr/bin/env python3
"""
ontology_check.py — Flag repo changes that may require ONTOLOGY.md updates.

Compares the current git state against a stored baseline (or HEAD~1) and
categorizes changed files by ontology impact. Exits 0 if no review needed,
exits 1 if ONTOLOGY.md review is recommended.

Usage:
    python machinery/tools/ontology_check.py
    python machinery/tools/ontology_check.py --since <git-ref>
    python machinery/tools/ontology_check.py --save-baseline
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


# ── Tracked file categories ────────────────────────────────────────────────

TRACKED: dict[str, list[str]] = {
    "schema": [
        "pyproject.toml",
        "workspace.example.yaml",
        "machinery/src/texgraph/config.py",
        "machinery/src/texgraph/parser.py",
    ],
    "commands": [
        "machinery/src/texgraph/cli.py",
        "pyproject.toml",
    ],
    "structure": [
        "AGENTS.md",
        "ONTOLOGY.md",
        "*/AGENTS.md",
        ".gitignore",
    ],
    "skills": [
        "*/skills/*/SKILL.md",
    ],
    "infrastructure": [
        "machinery/src/texgraph/*.py",
        "machinery/src/fletcher/*.py",
        "machinery/studio/backend/app/routers/*.py",
    ],
    "dependencies": [
        "requirements.txt",
        "machinery/studio/requirements-studio.txt",
        "machinery/studio/backend/requirements.txt",
    ],
}

REVIEW_NOTES: dict[str, str] = {
    "schema": "Data Schemas section (collection.yaml fields, front matter, workspace format)",
    "commands": "Command Surface section (CLI commands, flags, Studio API routes)",
    "structure": "Directory Taxonomy and Pipeline Architecture sections",
    "skills": "Content-type routing table (skills listed per stage)",
    "infrastructure": "Command Surface and Key Invariants sections",
    "dependencies": "Dependency Map section (Python packages, external binaries)",
}


# ── Helpers ────────────────────────────────────────────────────────────────

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot locate repo root — no pyproject.toml found.")


def _baseline_path(root: Path) -> Path:
    return root / ".ontology-baseline"


def _current_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root), capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def _changed_files(root: Path, since: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", since, "HEAD"],
        cwd=str(root), capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        # Fallback: compare staged + unstaged changes against HEAD
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(root), capture_output=True, text=True, check=False,
        )
        lines = []
        for line in result.stdout.splitlines():
            if line.strip():
                lines.append(line[3:].strip())
        return lines
    return [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]


def _matches(path: str, pattern: str) -> bool:
    return Path(path).match(pattern)


def _categorize(changed: list[str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {cat: [] for cat in TRACKED}
    for path in changed:
        for cat, patterns in TRACKED.items():
            for pattern in patterns:
                if _matches(path, pattern):
                    if path not in hits[cat]:
                        hits[cat].append(path)
                    break
    return {k: v for k, v in hits.items() if v}


# ── Commands ───────────────────────────────────────────────────────────────

def save_baseline(root: Path) -> int:
    head = _current_head(root)
    _baseline_path(root).write_text(head + "\n", encoding="utf-8")
    print(f"Baseline saved: {head[:12]}")
    return 0


def check(root: Path, since: str | None) -> int:
    baseline_file = _baseline_path(root)

    if since:
        ref = since
    elif baseline_file.exists():
        ref = baseline_file.read_text(encoding="utf-8").strip()
    else:
        ref = "HEAD~1"

    changed = _changed_files(root, ref)

    if not changed:
        print("No changes detected since baseline.")
        return 0

    categories = _categorize(changed)

    if not categories:
        print(f"{len(changed)} file(s) changed — no ONTOLOGY.md-tracked areas affected.")
        for f in changed:
            print(f"  {f}")
        return 0

    # Report
    print(f"ONTOLOGY.md REVIEW RECOMMENDED\n")
    print(f"{len(changed)} file(s) changed since {ref[:12]}:\n")

    for cat, paths in categories.items():
        print(f"  [{cat.upper()}]")
        for p in paths:
            print(f"    {p}")
    print()

    print("Sections to review:")
    for cat in categories:
        print(f"  - {REVIEW_NOTES[cat]}")

    print()
    uncategorized = [f for f in changed if not any(f in v for v in categories.values())]
    if uncategorized:
        print(f"Other changes ({len(uncategorized)} files — no direct ONTOLOGY impact):")
        for f in uncategorized:
            print(f"  {f}")
        print()

    print("When review is complete:")
    print("  python machinery/tools/ontology_check.py --save-baseline")
    return 1


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for ONTOLOGY.md-relevant repo changes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--since",
        metavar="GIT-REF",
        help="Compare from this git ref (default: stored baseline or HEAD~1).",
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save current HEAD as new baseline and exit.",
    )
    args = parser.parse_args()

    root = _repo_root()

    if args.save_baseline:
        return save_baseline(root)

    return check(root, args.since)


if __name__ == "__main__":
    sys.exit(main())
