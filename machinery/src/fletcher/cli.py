"""Fletcher — compatibility shim.

All commands have been merged into the unified `texgraph` CLI.
This module exists so that the `fletcher` entry point continues to work;
it delegates directly to the same Typer application.

Invoke as `texgraph` or `fletcher` — both expose the same command surface.
"""

from texgraph.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
