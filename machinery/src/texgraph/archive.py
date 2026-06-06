from __future__ import annotations

import argparse
import json
import shutil
import urllib.request
from pathlib import Path

from texgraph.env import resolve_in_repo

_BASE = "https://archive.org"


def _fetch_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))  # type: ignore[no-any-return]


def _list_files(args: argparse.Namespace) -> int:
    data = _fetch_json(f"{_BASE}/metadata/{args.identifier}")
    for item in data.get("files", []):  # type: ignore[union-attr]
        name = item.get("name", "")  # type: ignore[union-attr]
        if args.pattern and args.pattern.lower() not in name.lower():
            continue
        print(f"{name}\t{item.get('format', '')}\t{item.get('size', '')}")  # type: ignore[union-attr]
    return 0


def _download(args: argparse.Namespace) -> int:
    output = resolve_in_repo(args.output)
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    url = f"{_BASE}/download/{args.identifier}/{args.filename}"
    with urllib.request.urlopen(url, timeout=180) as response, output.open("wb") as target:
        shutil.copyfileobj(response, target)
    print(f"saved {output} ({output.stat().st_size} bytes)")
    return 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    arc_p = sub.add_parser("archive", help="Inspect or download Internet Archive source files.")
    arc_sub = arc_p.add_subparsers(dest="archive_command", required=True)

    files_p = arc_sub.add_parser("files", help="List files for an Internet Archive identifier.")
    files_p.add_argument("identifier")
    files_p.add_argument("--pattern", default=".pdf", help="Filter filenames (case-insensitive).")
    files_p.set_defaults(func=_list_files)

    dl_p = arc_sub.add_parser("download", help="Download one IA file into a repo-controlled path.")
    dl_p.add_argument("identifier")
    dl_p.add_argument("filename")
    dl_p.add_argument("output", help="Destination path inside the repo (e.g. raw/early_1913/fire_and_wine.pdf).")
    dl_p.set_defaults(func=_download)
