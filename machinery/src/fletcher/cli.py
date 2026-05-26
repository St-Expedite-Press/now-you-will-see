"""Fletcher editorial tools — unified CLI entry point."""

from __future__ import annotations

import argparse

from fletcher import archive, audit, metadata, pagemap, pdf, plan, scan


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fletcher",
        description="Fletcher scholarly edition tools: PDF inspection, transcription audit, metadata, and source acquisition.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pdf.register(sub)
    metadata.register(sub)
    audit.register(sub)
    pagemap.register(sub)
    plan.register(sub)
    scan.register(sub)
    archive.register(sub)

    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
