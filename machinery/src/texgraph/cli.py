"""
Texgraph command-line interface.

Built with Typer and Rich.  Entry point is ``app`` which is registered as
the ``texgraph`` console script in ``pyproject.toml``.

Commands
--------
build
    Assemble Markdown + YAML into a LuaLaTeX document and compile to PDF.
watch
    Watch the content and template directories; rebuild on every file change.
new poem
    Scaffold a new Markdown poem file in the correct section subdirectory.
list
    List all projects declared in workspace.yaml.
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from texgraph import __version__
from texgraph.utils import poem_scaffold, slugify

app = typer.Typer(
    name="texgraph",
    help="Markdown → LuaLaTeX → PDF/X poetry-collection compiler.",
    add_completion=False,
    rich_markup_mode="rich",
)
new_app = typer.Typer(help="Scaffold new collection items.")
app.add_typer(new_app, name="new")

console = Console(stderr=True)


# ---------------------------------------------------------------------------
# Internal helper: resolve CollectionConfig from workspace or direct config
# ---------------------------------------------------------------------------

def _resolve_config(
    config: Path,
    project: Optional[str],
) -> "CollectionConfig":
    """Return a :class:`CollectionConfig` using workspace or direct-config logic.

    Resolution order:

    1. If *config* was explicitly set to something other than the default
       ``collection.yaml``, use it directly (backward-compatible override).
    2. Otherwise look for ``workspace.yaml`` in the current directory.
       - If found, load it and resolve *project* (or the default project).
    3. Fall back to loading *config* (``collection.yaml``) directly.
    """
    from texgraph.config import CollectionConfig
    from texgraph.workspace import find_workspace, load_workspace, resolve_project

    # Explicit --config override always wins
    config_is_default = (config == Path("collection.yaml"))
    if not config_is_default:
        return CollectionConfig.from_yaml(config)

    # Try workspace lookup
    workspace_path = find_workspace(Path.cwd())
    if workspace_path is not None:
        try:
            workspace = load_workspace(workspace_path)
            return resolve_project(workspace, project)
        except (KeyError, ValueError, FileNotFoundError) as exc:
            console.print(f"[red]Workspace error:[/red] {exc}")
            raise typer.Exit(code=1)

    # Fall back to direct collection.yaml
    return CollectionConfig.from_yaml(config)


# ---------------------------------------------------------------------------
# Version callback
# ---------------------------------------------------------------------------

def _version_callback(value: bool) -> None:
    if value:
        rprint(f"[bold cyan]texgraph[/bold cyan] v{__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Print the version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Texgraph — Markdown-to-LuaLaTeX-to-PDFx poetry collection compiler."""


# ---------------------------------------------------------------------------
# build command
# ---------------------------------------------------------------------------

@app.command()
def build(
    config: Path = typer.Option(
        Path("collection.yaml"),
        "--config",
        "-c",
        help="Path to [bold]collection.yaml[/bold] (book metadata & settings).  "
             "When set, bypasses workspace lookup.",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project ID to build from [bold]workspace.yaml[/bold].  "
             "Uses the workspace default when omitted.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for compiled PDF and LaTeX files.  "
             "Overrides the value in collection.yaml.",
    ),
    draft: bool = typer.Option(
        False,
        "--draft",
        help="Draft mode: single lualatex run, skip PDF/X compliance metadata.",
    ),
    template: str = typer.Option(
        "collection.tex.jinja2",
        "--template",
        "-t",
        help="Name of the Jinja2 template to render.",
        show_default=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show lualatex log output after compilation.",
    ),
) -> None:
    """Build the full collection: parse → render → compile.

    Reads [bold]collection.yaml[/bold] for book metadata, parses all Markdown
    files in the content directory, renders a LuaLaTeX document via Jinja2
    templates, and compiles it to PDF using [italic]lualatex[/italic].

    In a workspace, resolves the project from [bold]workspace.yaml[/bold]
    unless [bold]--config[/bold] is given directly.

    Examples
    --------

        texgraph build

        texgraph build --project my-collection

        texgraph build --config my_book/collection.yaml --output dist/ --draft
    """
    # Lazy imports so the CLI starts fast even if deps are missing
    from texgraph.compiler import Compiler
    from texgraph.parser import PoetryParser
    from texgraph.renderer import LaTeXRenderer

    # --- Load config -------------------------------------------------------
    console.rule("[bold cyan]Texgraph Build[/bold cyan]")

    # If using direct --config, verify the file exists before proceeding
    config_is_default = (config == Path("collection.yaml"))
    if not config_is_default and not config.exists():
        console.print(f"[red]Error:[/red] config file not found: [bold]{config}[/bold]")
        raise typer.Exit(code=1)

    try:
        cfg = _resolve_config(config, project)
    except typer.Exit:
        raise
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    if draft:
        cfg.draft_mode = True
    if output:
        cfg.output_dir = str(output)

    console.print(
        f"  [bold]Collection:[/bold] {cfg.title}"
        + (f" — {cfg.subtitle}" if cfg.subtitle else "")
    )
    console.print(f"  [bold]Author:[/bold]     {cfg.author}")
    console.print(f"  [bold]Output:[/bold]     {cfg.resolved_output_dir}")
    if cfg.draft_mode:
        console.print("  [yellow]Draft mode enabled — single pass, no PDF/X metadata.[/yellow]")

    # --- Parse --------------------------------------------------------------
    parser = PoetryParser()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Parsing content…", total=None)
        try:
            sections = parser.scan_collection(cfg.resolved_content_dir)
        except FileNotFoundError as exc:
            console.print(f"[red]Parse error:[/red] {exc}")
            raise typer.Exit(code=1)
        progress.update(task, description="Parsing complete.")

    poem_count = sum(len(s.poems) for s in sections)
    console.print(
        f"  Parsed [bold]{poem_count}[/bold] poem(s) "
        f"across [bold]{len(sections)}[/bold] section(s)."
    )

    # --- Render -------------------------------------------------------------
    renderer = LaTeXRenderer()
    collection_data = {"config": cfg.as_dict(), "sections": sections}

    try:
        tex_source = renderer.render(collection_data, template_name=template)
    except Exception as exc:
        console.print(f"[red]Render error:[/red] {exc}")
        raise typer.Exit(code=1)

    out_dir = cfg.ensure_output_dir()
    tex_file = out_dir / f"{_slugify(cfg.title)}.tex"
    tex_file.write_text(tex_source, encoding="utf-8")
    console.print(f"  LaTeX written → [bold]{tex_file}[/bold]")

    # --- Compile ------------------------------------------------------------
    compiler = Compiler(lualatex_path=cfg.lualatex_path)

    if not compiler.check_available():
        console.print(
            f"[yellow]Warning:[/yellow] lualatex not found at "
            f"[bold]{cfg.lualatex_path}[/bold].  Skipping compilation."
        )
        console.print("  Install TeX Live or MiKTeX and ensure lualatex is on PATH.")
        raise typer.Exit(code=0)

    runs = 1 if cfg.draft_mode else 2
    console.print(f"  Compiling ({runs} lualatex run(s))…")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running lualatex…", total=None)
        result = compiler.compile(tex_file, out_dir, runs=runs, draft=cfg.draft_mode)
        progress.update(task, description="Compilation done.")

    if result.success:
        console.print(
            Panel(
                f"[bold green]Success![/bold green]  "
                f"PDF → [bold]{result.pdf_path}[/bold]",
                border_style="green",
            )
        )
    else:
        console.print(Panel("[bold red]Compilation failed.[/bold red]", border_style="red"))

    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for err in result.errors:
            console.print(f"  [red]✗[/red] {err}")

    if verbose and result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warn in result.warnings[:20]:  # cap at 20 to avoid flooding
            console.print(f"  [yellow]△[/yellow] {warn}")

    if verbose and result.log_path and result.log_path.exists():
        console.print(f"\n  Full log: [dim]{result.log_path}[/dim]")

    raise typer.Exit(code=0 if result.success else 1)


# ---------------------------------------------------------------------------
# watch command
# ---------------------------------------------------------------------------

@app.command()
def watch(
    config: Path = typer.Option(
        Path("collection.yaml"),
        "--config",
        "-c",
        help="Path to [bold]collection.yaml[/bold].  When set, bypasses workspace lookup.",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project ID to watch from [bold]workspace.yaml[/bold].  "
             "Uses the workspace default when omitted.",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (overrides collection.yaml).",
    ),
    draft: bool = typer.Option(
        True,
        "--draft/--no-draft",
        help="Use draft mode for faster rebuilds (default: on).",
    ),
    debounce: float = typer.Option(
        1.5,
        "--debounce",
        help="Seconds to wait after a file change before rebuilding.",
        show_default=True,
    ),
) -> None:
    """Watch for file changes and rebuild automatically.

    Monitors the content directory, template directory, and
    [bold]collection.yaml[/bold] for modifications.  Triggers a [bold]build[/bold]
    whenever a [italic].md[/italic], [italic].yaml[/italic], or
    [italic].jinja2[/italic] file changes.

    In a workspace, resolves the project from [bold]workspace.yaml[/bold]
    unless [bold]--config[/bold] is given directly.

    Press [bold]Ctrl+C[/bold] to stop.

    Examples
    --------

        texgraph watch

        texgraph watch --project my-collection

        texgraph watch --no-draft --debounce 2.0
    """
    try:
        from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
        from watchdog.observers import Observer
    except ImportError:
        console.print("[red]watchdog is required for watch mode.[/red]  pip install watchdog")
        raise typer.Exit(code=1)

    config_is_default = (config == Path("collection.yaml"))
    if not config_is_default and not config.exists():
        console.print(f"[red]Config not found:[/red] {config}")
        raise typer.Exit(code=1)

    try:
        cfg = _resolve_config(config, project)
    except typer.Exit:
        raise
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    if output:
        cfg.output_dir = str(output)

    watch_dirs = [
        cfg.resolved_content_dir,
        cfg.project_root / "templates",
        cfg.project_root,
    ]
    existing_watch_dirs = [d for d in watch_dirs if d.exists()]

    console.rule("[bold cyan]Texgraph Watch[/bold cyan]")
    console.print(f"  Watching: {', '.join(str(d) for d in existing_watch_dirs)}")
    console.print("  Press [bold]Ctrl+C[/bold] to stop.\n")

    # State shared with the handler
    state: dict[str, float] = {"last_build": 0.0}

    def _trigger_build() -> None:
        now = time.monotonic()
        if now - state["last_build"] < debounce:
            return
        state["last_build"] = now
        console.print("\n[bold cyan]Change detected — rebuilding…[/bold cyan]")
        # Invoke build programmatically by reconstructing CLI args
        _run_build_programmatic(config=cfg.project_root / "collection.yaml", output=output, draft=draft)

    class _Handler(PatternMatchingEventHandler):  # type: ignore[misc]
        def __init__(self) -> None:
            super().__init__(
                patterns=["*.md", "*.yaml", "*.yml", "*.jinja2", "*.tex"],
                ignore_directories=True,
                case_sensitive=False,
            )

        def on_any_event(self, event: FileSystemEvent) -> None:
            _trigger_build()

    handler = _Handler()
    observer = Observer()
    for watch_dir in existing_watch_dirs:
        observer.schedule(handler, str(watch_dir), recursive=True)

    # Run an initial build using the fully resolved project config path
    _run_build_programmatic(config=cfg.project_root / "collection.yaml", output=output, draft=draft)

    observer.start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        console.print("\n[bold]Watch stopped.[/bold]")
    finally:
        observer.stop()
        observer.join()


# ---------------------------------------------------------------------------
# list command
# ---------------------------------------------------------------------------

@app.command("list")
def list_projects(
    workspace_file: Optional[Path] = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Path to [bold]workspace.yaml[/bold].  "
             "Defaults to auto-discovery from the current directory.",
    ),
) -> None:
    """List all projects declared in [bold]workspace.yaml[/bold].

    Displays each project's ID, relative path, and description in a table.
    Searches upward from the current directory for [bold]workspace.yaml[/bold]
    unless [bold]--workspace[/bold] is given.

    Examples
    --------

        texgraph list

        texgraph list --workspace /path/to/workspace.yaml
    """
    from texgraph.workspace import find_workspace, load_workspace

    if workspace_file is not None:
        if not workspace_file.exists():
            console.print(
                f"[red]Error:[/red] workspace file not found: [bold]{workspace_file}[/bold]"
            )
            raise typer.Exit(code=1)
        resolved_workspace = workspace_file
    else:
        resolved_workspace = find_workspace(Path.cwd())
        if resolved_workspace is None:
            console.print(
                "[red]Error:[/red] No [bold]workspace.yaml[/bold] found.  "
                "Run from a workspace directory or use [bold]--workspace[/bold]."
            )
            raise typer.Exit(code=1)

    try:
        workspace = load_workspace(resolved_workspace)
    except (ValueError, Exception) as exc:
        console.print(f"[red]Workspace error:[/red] {exc}")
        raise typer.Exit(code=1)

    projects = workspace.list_projects()

    console.rule("[bold cyan]Texgraph Workspace Projects[/bold cyan]")
    console.print(f"  Workspace: [dim]{resolved_workspace}[/dim]\n")

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("ID", style="bold", no_wrap=True)
    table.add_column("Path", style="dim")
    table.add_column("Description")
    table.add_column("Default", justify="center")

    for ref in projects:
        is_default = ref.id == workspace.default_project
        default_marker = "[bold green]yes[/bold green]" if is_default else ""
        table.add_row(ref.id, ref.path, ref.description, default_marker)

    console.print(table)

    if not projects:
        console.print("  [yellow]No projects found in workspace.yaml.[/yellow]")


# ---------------------------------------------------------------------------
# new poem command
# ---------------------------------------------------------------------------

@new_app.command("poem")
def new_poem(
    title: str = typer.Argument(..., help="Title of the new poem."),
    section: str = typer.Option(
        "",
        "--section",
        "-s",
        help="Target section sub-directory name (e.g. [bold]01_poems[/bold]).  "
             "Defaults to the first section found in content/.",
    ),
    config: Path = typer.Option(
        Path("collection.yaml"),
        "--config",
        "-c",
        help="Path to [bold]collection.yaml[/bold].  When set, bypasses workspace lookup.",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project ID from [bold]workspace.yaml[/bold] that determines the content dir.  "
             "Uses the workspace default when omitted.",
    ),
    poem_type: str = typer.Option(
        "poem",
        "--type",
        help="Block type: [bold]poem[/bold] or [bold]prose[/bold].",
        show_default=True,
    ),
    open_editor: bool = typer.Option(
        False,
        "--open",
        help="Open the new file in \\$EDITOR after creation.",
    ),
) -> None:
    """Scaffold a new poem Markdown file in the collection.

    Creates a ``.md`` file with YAML front matter pre-filled from the
    provided [bold]TITLE[/bold] and places it in the appropriate section
    sub-directory of the content folder.

    In a workspace, resolves the project from [bold]workspace.yaml[/bold]
    unless [bold]--config[/bold] is given directly.

    Examples
    --------

        texgraph new poem "The Raven"

        texgraph new poem "The Raven" --project my-collection

        texgraph new poem "Ode to Autumn" --section 02_odes --type prose
    """
    config_is_default = (config == Path("collection.yaml"))
    if not config_is_default and not config.exists():
        console.print(f"[red]Config not found:[/red] {config}")
        raise typer.Exit(code=1)

    try:
        cfg = _resolve_config(config, project)
    except typer.Exit:
        raise
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    content_dir = cfg.resolved_content_dir
    content_dir.mkdir(parents=True, exist_ok=True)

    # Resolve target section directory
    if section:
        target_dir = content_dir / section
    else:
        # Use the first existing section sub-directory, or content_dir itself
        sub_dirs = sorted(
            [d for d in content_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
            if content_dir.exists() else []
        )
        target_dir = sub_dirs[0] if sub_dirs else content_dir

    target_dir.mkdir(parents=True, exist_ok=True)

    # Build filename from title
    filename = _slugify(title) + ".md"
    dest = target_dir / filename

    if dest.exists():
        console.print(f"[yellow]File already exists:[/yellow] {dest}")
        raise typer.Exit(code=1)

    # Write the scaffolded file
    content = _poem_scaffold(title=title, poem_type=poem_type)
    dest.write_text(content, encoding="utf-8")

    console.print(
        Panel(
            f"[bold green]Created:[/bold green] [bold]{dest}[/bold]",
            border_style="green",
        )
    )

    # Optionally open in $EDITOR
    if open_editor:
        import os
        editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
        if editor:
            import subprocess as _sp
            _sp.run([editor, str(dest)])
        else:
            console.print("[yellow]$EDITOR not set — skipping.[/yellow]")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

import re  # noqa: E402

def _slugify(text: str) -> str:
    return slugify(text)


def _poem_scaffold(title: str, poem_type: str = "poem") -> str:
    return poem_scaffold(title, poem_type)


def _run_build_programmatic(
    config: Path,
    output: Optional[Path],
    draft: bool,
) -> None:
    """Re-invoke the build logic without spawning a subprocess."""
    # We call the underlying functions directly to avoid process overhead
    from texgraph.compiler import Compiler
    from texgraph.config import CollectionConfig
    from texgraph.parser import PoetryParser
    from texgraph.renderer import LaTeXRenderer

    try:
        cfg = CollectionConfig.from_yaml(config)
    except ValueError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        return

    if draft:
        cfg.draft_mode = True
    if output:
        cfg.output_dir = str(output)

    try:
        parser = PoetryParser()
        sections = parser.scan_collection(cfg.resolved_content_dir)
    except FileNotFoundError as exc:
        console.print(f"[red]Parse error:[/red] {exc}")
        return

    renderer = LaTeXRenderer()
    collection_data = {"config": cfg.as_dict(), "sections": sections}
    try:
        tex_source = renderer.render(collection_data)
    except Exception as exc:
        console.print(f"[red]Render error:[/red] {exc}")
        return

    out_dir = cfg.ensure_output_dir()
    tex_file = out_dir / f"{_slugify(cfg.title)}.tex"
    tex_file.write_text(tex_source, encoding="utf-8")

    compiler = Compiler(lualatex_path=cfg.lualatex_path)
    if not compiler.check_available():
        console.print("[yellow]lualatex not found — skipping compilation.[/yellow]")
        return

    runs = 1 if cfg.draft_mode else 2
    result = compiler.compile(tex_file, out_dir, runs=runs, draft=cfg.draft_mode)

    if result.success:
        console.print(f"[green]Built:[/green] {result.pdf_path}")
    else:
        console.print("[red]Build failed.[/red]")
        for err in result.errors[:5]:
            console.print(f"  [red]✗[/red] {err}")


# ---------------------------------------------------------------------------
# Entry point guard (for direct `python -m texgraph.cli` invocation)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# studio command
# ---------------------------------------------------------------------------

@app.command()
def studio(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        help="Bind address for the Studio server.",
        show_default=True,
    ),
    port: int = typer.Option(
        8765,
        "--port",
        help="Port for the Studio server.",
        show_default=True,
    ),
    no_open: bool = typer.Option(
        False,
        "--no-open",
        help="Do not open the browser automatically.",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        help="Enable uvicorn auto-reload (development only).",
    ),
) -> None:
    """Launch Texgraph Studio — local FastAPI + React GUI.

    Starts a uvicorn server hosting the Studio backend and opens the
    application in the default system browser.

    Examples
    --------

        texgraph studio

        texgraph studio --port 8080 --no-open
    """
    try:
        import uvicorn
    except ImportError:
        console.print(
            "[red]uvicorn is required for Texgraph Studio.[/red]\n"
            "  Install it:  pip install -r machinery/studio/requirements-studio.txt"
        )
        raise typer.Exit(code=1)

    url = f"http://{host}:{port}"
    console.rule("[bold cyan]Texgraph Studio[/bold cyan]")
    console.print(f"  Listening on [bold]{url}[/bold]")
    console.print("  Press [bold]Ctrl+C[/bold] to stop.\n")

    if not no_open:
        import threading, webbrowser
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        app_dir=str(Path(__file__).parents[2] / "studio" / "backend"),
        log_level="warning",
    )


if __name__ == "__main__":
    app()
