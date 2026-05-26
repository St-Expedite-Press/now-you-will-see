from __future__ import annotations

import argparse


def expand_pages(spec: str) -> list[int]:
    """Expand a page range spec like '7-10,14,18' into a flat list of integers."""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            if end < start:
                raise SystemExit(f"Invalid page range: {part}")
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    return pages


def _run(args: argparse.Namespace) -> int:
    print("printed,scan")
    for printed in expand_pages(args.printed):
        print(f"{printed},{printed + args.offset}")
    return 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("page-map", help="Map printed page numbers to scan page numbers via a fixed offset.")
    p.add_argument("--offset", type=int, required=True, help="scan = printed + offset")
    p.add_argument("--printed", required=True, help="Example: 7-10,14,18")
    p.set_defaults(func=_run)
