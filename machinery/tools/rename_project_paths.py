"""One-shot path rewrite for the Fletcher four-volume project split.

The single `fletcher-complete-original-collections` project was split into four
volume projects plus a shared `fletcher-series` root. Every in-file path that
referenced the old project must be repointed to where its target now lives:

* source PDFs (legacy ``ingest/raw`` and ``sources/``)  -> fletcher-series/sources
* series metadata (four_volume_order, PROJECT_PLAN)      -> fletcher-series
* each volume's transcription tree                       -> its volume project
* everything else (vol-1 transcription, manuscript, ...) -> fletcher-early-works

Replacements are ordered specific-first so the catch-all only sees what remains.
Run once from the repo root: ``python machinery/tools/rename_project_paths.py``.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTS = REPO_ROOT / "projects"

_OLD = "fletcher-complete-original-collections"

# (old, new) applied in order; specific paths before the catch-all.
REPLACEMENTS: list[tuple[str, str]] = [
    (f"{_OLD}/ingest/raw/", "fletcher-series/sources/raw/"),
    (f"{_OLD}/ingest/", "fletcher-series/sources/"),
    (f"{_OLD}/sources/", "fletcher-series/sources/"),
    (f"{_OLD}/transcription/metadata/four_volume_order",
     "fletcher-series/metadata/four_volume_order"),
    (f"{_OLD}/transcription/project_plan/PROJECT_PLAN",
     "fletcher-series/project_plan/PROJECT_PLAN"),
    (f"{_OLD}/transcription/volumes/02_dominant_works",
     "fletcher-dominant-works/transcription/volumes/02_dominant_works"),
    (f"{_OLD}/transcription/volumes/03_embattled_works",
     "fletcher-embattled-works/transcription/volumes/03_embattled_works"),
    (f"{_OLD}/transcription/volumes/04_falling_works",
     "fletcher-falling-works/transcription/volumes/04_falling_works"),
    # Catch-all: vol-1 transcription witnesses, manuscript/interior, project_id.
    (_OLD, "fletcher-early-works"),
]

_EXTS = {".md", ".yaml", ".yml", ".json", ".txt"}


def main() -> None:
    changed = 0
    for project in sorted(PROJECTS.glob("fletcher-*")):
        for f in project.rglob("*"):
            if not f.is_file() or f.suffix not in _EXTS or "/output/" in f.as_posix():
                continue
            text = f.read_text(encoding="utf-8")
            if _OLD not in text:
                continue
            new = text
            for old, repl in REPLACEMENTS:
                new = new.replace(old, repl)
            if new != text:
                f.write_text(new, encoding="utf-8")
                changed += 1
    print(f"Rewrote {changed} file(s).")


if __name__ == "__main__":
    main()
