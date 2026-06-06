from __future__ import annotations

import argparse
import json
import shutil

from texgraph.env import repo_root, resolve_in_repo, run_checked


def _require_binary(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise SystemExit(f"Required binary not found on PATH: {name}")
    return found


def _parse_pdfinfo(output: str) -> dict[str, str | int]:
    data: dict[str, str | int] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        if key == "pages":
            try:
                data[key] = int(value)
                continue
            except ValueError:
                pass
        data[key] = value
    return data


def _info(args: argparse.Namespace) -> int:
    _require_binary("pdfinfo")
    pdf = resolve_in_repo(args.pdf)
    result = run_checked(["pdfinfo", str(pdf)])
    if args.json:
        print(json.dumps(_parse_pdfinfo(result.stdout), indent=2, sort_keys=True))
    else:
        print(result.stdout, end="")
    return 0


def _text(args: argparse.Namespace) -> int:
    _require_binary("pdftotext")
    pdf = resolve_in_repo(args.pdf)
    command = ["pdftotext", "-f", str(args.first), "-l", str(args.last), "-layout", str(pdf), "-"]
    result = run_checked(command)
    if args.output:
        resolve_in_repo(args.output).write_text(result.stdout, encoding="utf-8")
    else:
        print(result.stdout, end="")
    return 0


def _render(args: argparse.Namespace) -> int:
    _require_binary("pdftoppm")
    pdf = resolve_in_repo(args.pdf)
    prefix_path = resolve_in_repo(args.prefix)
    prefix_path.parent.mkdir(parents=True, exist_ok=True)
    run_checked([
        "pdftoppm",
        "-f", str(args.first),
        "-l", str(args.last),
        "-png",
        "-r", str(args.dpi),
        str(pdf),
        str(prefix_path),
    ])
    created = sorted(prefix_path.parent.glob(f"{prefix_path.name}-*.png"))
    print(f"rendered={len(created)} prefix={prefix_path.relative_to(repo_root())}")
    return 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    pdf_p = sub.add_parser("pdf", help="PDF inspection and page rendering.")
    pdf_sub = pdf_p.add_subparsers(dest="pdf_command", required=True)

    info_p = pdf_sub.add_parser("info", help="Run pdfinfo; optionally output JSON.")
    info_p.add_argument("pdf")
    info_p.add_argument("--json", action="store_true")
    info_p.set_defaults(func=_info)

    text_p = pdf_sub.add_parser("text", help="Extract layout text for navigation/checking.")
    text_p.add_argument("pdf")
    text_p.add_argument("--first", type=int, required=True)
    text_p.add_argument("--last", type=int, required=True)
    text_p.add_argument("--output", help="Write output to this path instead of stdout.")
    text_p.set_defaults(func=_text)

    render_p = pdf_sub.add_parser("render", help="Render pages to PNG with pdftoppm.")
    render_p.add_argument("pdf")
    render_p.add_argument("--first", type=int, required=True)
    render_p.add_argument("--last", type=int, required=True)
    render_p.add_argument("--prefix", required=True, help="Output filename prefix (e.g. tmp_fw).")
    render_p.add_argument("--dpi", type=int, default=180)
    render_p.set_defaults(func=_render)
