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

from backend.core import __version__
from backend.core.utils import poem_scaffold, slugify

app = typer.Typer(
    help="Markdown -> LuaLaTeX -> PDF/X poetry-collection compiler and editorial toolkit.",
    add_completion=False,
    rich_markup_mode="rich",
)
new_app = typer.Typer(help="Scaffold new collection items.")
app.add_typer(new_app, name="new")
modules_app = typer.Typer(help="Inspect canonical pipeline modules.")
app.add_typer(modules_app, name="modules")
migrate_app = typer.Typer(help="Run compatibility migrations.")
app.add_typer(migrate_app, name="migrate")

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
    from backend.core.config import CollectionConfig
    from backend.core.workspace import find_workspace, load_workspace, resolve_project

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
    """Build the full collection: parse -> render -> compile.

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
    from backend.core.compiler import Compiler
    from backend.core.parser import PoetryParser
    from backend.core.renderer import LaTeXRenderer

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
        except (FileNotFoundError, ValueError) as exc:
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
    tex_dir = out_dir / "tex"
    tex_dir.mkdir(exist_ok=True)
    tex_file = tex_dir / f"{_slugify(cfg.title)}.tex"
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
# proof-build command
# ---------------------------------------------------------------------------

@app.command(name="proof-build")
def proof_build(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project ID from [bold]workspace.yaml[/bold].",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Style sheet to render (e.g. [bold]interior/collection_hardcover.yaml[/bold]). "
             "Defaults to the project's collection.yaml.  Variants write to "
             "[bold]output/proof-<name>/[/bold] so they don't clobber each other.",
    ),
    print_ready: bool = typer.Option(
        False,
        "--print-ready",
        help="Produce a vendor-upload PDF/X (loads pdfx, even page count) into "
             "[bold]output/print/<name>/[/bold] instead of a review proof.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show lualatex log output after compilation.",
    ),
) -> None:
    """Build the proof-draft artifact tree from the interior manuscript.

    Each content unit — frontmatter pages, section title pages, dedications,
    poems, and backmatter chapters — is rendered as its own [bold].tex[/bold]
    fragment under [bold]interior/output/proof/tex/<section>/[/bold].

    A shared [bold]preamble.tex[/bold] and a master document that assembles all
    fragments via [bold]\\\\input{}[/bold] are also written.  The master is
    compiled to produce [bold]interior/output/proof/<slug>.pdf[/bold].

    Fragment artifacts are retained for later operation; the PDF is gitignored.

    Examples
    --------

        texgraph proof-build --project fletcher-early-works
    """
    from backend.core.compiler import Compiler
    from backend.core.parser import PoetryParser
    from backend.core.renderer import LaTeXRenderer

    console.rule("[bold cyan]Texgraph Proof Build[/bold cyan]")

    try:
        cfg = _resolve_config(config or Path("collection.yaml"), project)
    except typer.Exit:
        raise
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    cfg.draft_mode = not print_ready  # print-ready keeps full PDF/X compile

    # Variant style sheets (hardcover, softcover) render through this same
    # pipeline into a distinct output dir so the trade proof is never clobbered.
    variant = ""
    if config is not None and Path(config).stem not in ("collection", ""):
        variant = Path(config).stem.removeprefix("collection_")

    interior_root = cfg.project_root
    project_root = interior_root.parent
    if print_ready:
        # Vendor-upload PDF/X output, kept apart from review proofs.
        proof_out = interior_root / "output" / "print" / (variant or "default")
    else:
        proof_out = interior_root / "output" / (f"proof-{variant}" if variant else "proof")
    tex_out = proof_out / "tex"
    tex_out.mkdir(parents=True, exist_ok=True)

    console.print(
        f"  [bold]Collection:[/bold] {cfg.title}"
        + (f" — {cfg.subtitle}" if cfg.subtitle else "")
    )
    console.print(f"  [bold]Author:[/bold]      {cfg.author}")
    console.print(f"  [bold]Proof draft output:[/bold] {proof_out}")

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
        except (FileNotFoundError, ValueError) as exc:
            console.print(f"[red]Parse error:[/red] {exc}")
            raise typer.Exit(code=1)
        progress.update(task, description="Parsing complete.")

    unit_count = sum(len(s.poems) for s in sections)
    console.print(
        f"  Parsed [bold]{unit_count}[/bold] unit(s) "
        f"across [bold]{len(sections)}[/bold] section(s)."
    )

    # --- Render fragments ---------------------------------------------------
    renderer = LaTeXRenderer()
    raw_config = cfg.as_dict()

    frontmatter_paths: list[str] = []
    main_sections: list[dict] = []
    backmatter_paths: list[str] = []
    fragment_count = 0
    errors: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Rendering fragments…", total=None)

        for section in sections:
            section_type = section.meta.get("type", "section")
            section_dir = tex_out / section.path.name
            section_dir.mkdir(exist_ok=True)

            # For main-matter sections, create a per-section bucket; its keyed
            # notes section (if any) is rendered after the poems below.
            section_title = str(section.meta.get("title") or "")
            if section_type not in ("frontmatter", "backmatter"):
                main_sections.append({
                    "title": section_title,
                    "paths": [],
                    "notes_path": None,
                })

            prev_part = ""
            for poem in section.poems:
                current_part = str(poem.meta.get("part") or "")
                include_part_heading = bool(current_part and current_part != prev_part)
                if current_part:
                    prev_part = current_part

                frag_name = poem.path.stem
                frag_path = section_dir / f"{frag_name}.tex"
                rel_input = f"{section.path.name}/{frag_name}"

                try:
                    frag_src = renderer.render_fragment(
                        poem, section, raw_config,
                        include_part_heading=include_part_heading,
                    )
                except Exception as exc:
                    errors.append(f"{rel_input}: {exc}")
                    continue

                frag_path.write_text(frag_src, encoding="utf-8")
                fragment_count += 1

                if section_type == "frontmatter":
                    frontmatter_paths.append(rel_input)
                elif section_type == "backmatter":
                    backmatter_paths.append(rel_input)
                else:
                    main_sections[-1]["paths"].append(rel_input)

            # Keyed back-matter notes for this book (only if a poem carries notes).
            if section_type not in ("frontmatter", "backmatter") and section_title:
                try:
                    notes_src = renderer.render_notes_section(
                        section_title, section.poems, raw_config
                    )
                except Exception as exc:
                    errors.append(f"{section.path.name}/_notes: {exc}")
                    notes_src = None
                if notes_src:
                    (section_dir / "_notes.tex").write_text(notes_src, encoding="utf-8")
                    fragment_count += 1
                    main_sections[-1]["notes_path"] = f"{section.path.name}/_notes"

        progress.update(task, description="Fragments done.")

    if errors:
        console.print(f"[red]{len(errors)} fragment render error(s):[/red]")
        for e in errors[:10]:
            console.print(f"  [red]✗[/red] {e}")
        raise typer.Exit(code=1)

    console.print(f"  Rendered [bold]{fragment_count}[/bold] fragment(s).")

    # --- Preamble -----------------------------------------------------------
    preamble_path = tex_out / "preamble.tex"
    preamble_path.write_text(
        renderer.render_proof_preamble(raw_config, print_ready=print_ready),
        encoding="utf-8",
    )

    # --- Master document ----------------------------------------------------
    slug = _slugify(cfg.title)
    master_path = tex_out / f"{slug}.tex"

    # PDF/X metadata sidecar read by the pdfx package (matches \jobname).
    if print_ready:
        xmp = (
            f"\\Title{{{cfg.title}}}\n"
            f"\\Author{{{cfg.author}}}\n"
            f"\\Language{{{cfg.language or 'en-US'}}}\n"
            f"\\Keywords{{}}\n"
            f"\\Subject{{}}\n"
        )
        (tex_out / f"{slug}.xmpdata").write_text(xmp, encoding="utf-8")
    master_path.write_text(
        renderer.render_proof_master(
            raw_config, frontmatter_paths, main_sections, backmatter_paths
        ),
        encoding="utf-8",
    )
    try:
        proof_display = proof_out.relative_to(project_root)
        tex_display = tex_out.relative_to(project_root)
    except ValueError:
        proof_display = proof_out
        tex_display = tex_out
    console.print(
        f"  preamble -> [bold]{tex_display}/preamble.tex[/bold]\n"
        f"  master   -> [bold]{tex_display}/{slug}.tex[/bold]"
    )

    # --- Compile master (2 passes for TOC) ----------------------------------
    compiler = Compiler(lualatex_path=cfg.lualatex_path)

    if not compiler.check_available():
        console.print("[yellow]Warning:[/yellow] lualatex not found — skipping compilation.")
        raise typer.Exit(code=0)

    console.print("  Compiling master (2 lualatex passes for TOC)…")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running lualatex…", total=None)
        # draft=False so the compiler runs 2 passes; pdfx is skipped because
        # cfg.draft_mode=True means the template omits \usepackage{pdfx}
        result = compiler.compile(master_path, proof_out, runs=2, draft=False)
        progress.update(task, description="Compilation done.")

    if result.success:
        rel_pdf = result.pdf_path.relative_to(project_root)
        console.print(
            Panel(
                f"[bold green]Success![/bold green]  PDF → [bold]{result.pdf_path}[/bold]\n"
                f"\n[dim]draft_proof_pdf path:  {rel_pdf}[/dim]",
                border_style="green",
            )
        )
    else:
        console.print(Panel("[bold red]Proof build failed.[/bold red]", border_style="red"))
        for err in result.errors:
            console.print(f"  [red]✗[/red] {err}")

    if verbose and result.warnings:
        for warn in result.warnings[:20]:
            console.print(f"  [yellow]△[/yellow] {warn}")

    if verbose and result.log_path and result.log_path.exists():
        console.print(f"\n  Full log: [dim]{result.log_path}[/dim]")

    raise typer.Exit(code=0 if result.success else 1)


@app.command(name="proof-preview")
def proof_preview(
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Project ID from [bold]workspace.yaml[/bold]."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Style sheet whose proof to preview (e.g. "
             "[bold]interior/collection_royal.yaml[/bold]).  Must match the "
             "sheet passed to [bold]proof-build[/bold]; previews the matching "
             "[bold]output/proof-<name>/[/bold] tree.  Defaults to the trade proof.",
    ),
    pages: Optional[str] = typer.Option(
        None, "--pages",
        help="Extra pages to render, e.g. [bold]40,120-122[/bold].",
    ),
    sample: int = typer.Option(
        0, "--sample",
        help="Also render every Nth page (0 = off) to spot-check body poems.",
    ),
    dpi: int = typer.Option(150, "--dpi", help="Render resolution."),
) -> None:
    """Render the structurally important proof pages to PNG for visual review.

    Closes the gap between "the build succeeded" and "the book is right": instead
    of inferring layout from the generated [bold].tex[/bold], this renders the
    actual leaves a reviewer must eyeball — every book title page and part
    divider (from the [bold].toc[/bold]), the introduction, each per-volume notes
    section, plus any [bold]--pages[/bold] and an optional [bold]--sample[/bold]
    stride — into [bold]interior/output/proof/preview/[/bold].

    Run [bold]proof-build[/bold] first.  Requires [bold]pdftoppm[/bold] (poppler).
    """
    import shutil
    import subprocess

    from backend.core.pagemap import expand_pages

    console.rule("[bold cyan]Texgraph Proof Preview[/bold cyan]")

    for tool in ("pdftoppm", "pdftotext"):
        if not shutil.which(tool):
            console.print(f"[red]{tool} not found on PATH.[/red]  Install poppler-utils.")
            raise typer.Exit(code=1)

    try:
        cfg = _resolve_config(config or Path("collection.yaml"), project)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    # Resolve the variant proof dir the same way proof-build writes it, so a
    # variant style sheet previews its own tree rather than the trade proof.
    variant = ""
    if config is not None and Path(config).stem not in ("collection", ""):
        variant = Path(config).stem.removeprefix("collection_")
    proof_out = cfg.project_root / "output" / (f"proof-{variant}" if variant else "proof")
    slug = _slugify(cfg.title)
    pdf = proof_out / f"{slug}.pdf"
    if not pdf.exists():
        console.print(f"[red]Proof PDF not found:[/red] {pdf}\n  Run proof-build first.")
        raise typer.Exit(code=1)

    # Structural pages are detected by content: title pages, part dividers, and
    # centered short poems carry only a few words, unlike dense body or notes
    # pages.  pdftotext splits on form feeds, one chunk per *physical* page —
    # the index pdftoppm needs (the printed folio in the TOC is not the same).
    # Capture bytes and decode explicitly: text=True defaults to cp1252 on
    # Windows and crashes on the UTF-8 in the OCR/typeset text layer.
    proc = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True
    )
    physical_pages = proc.stdout.decode("utf-8", errors="replace").split("\f")
    total = len(physical_pages)

    labelled: dict[int, str] = {1: "opening"}
    for i, ptext in enumerate(physical_pages, start=1):
        compact = " ".join(ptext.split())
        if 0 < len(compact) <= 70:  # sparse leaf = structural page or short poem
            labelled[i] = compact[:54]
    if pages:
        for p in expand_pages(pages):
            labelled.setdefault(p, "requested")
    if sample > 0:
        for p in range(sample, total + 1, sample):
            labelled.setdefault(p, "sample")

    preview_dir = proof_out / "preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for old in preview_dir.glob("page-*.png"):
        old.unlink()

    rendered = 0
    for page in sorted(labelled):
        if page > total:
            continue
        prefix = preview_dir / f"page-{page:04d}"
        result = subprocess.run(
            ["pdftoppm", "-f", str(page), "-l", str(page), "-png", "-r", str(dpi),
             "-singlefile", str(pdf), str(prefix)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            continue
        rendered += 1
        console.print(f"  p.{page:>4}  [dim]{labelled[page]}[/dim]")

    console.print(
        f"\n  Rendered [bold]{rendered}[/bold] page(s) -> "
        f"[bold]{preview_dir.relative_to(cfg.project_root.parent)}[/bold]"
    )


@app.command(name="verify-coverage")
def verify_coverage(
    project: Optional[str] = typer.Option(
        None, "--project", "-p", help="Project ID from [bold]workspace.yaml[/bold]."
    ),
) -> None:
    """Prove every transcription poem reaches the reading edition (1:1).

    Checks the ``source:`` links from reading poems to their documentary
    witnesses: no broken links, no two readers sharing a witness, and — the
    point — no transcription poem left unbuilt.  Exits non-zero on any gap, so
    it can gate CI and guarantee no poem is ever silently dropped.
    """
    from backend.core.coverage import check_source_coverage
    from backend.core.env import repo_root

    console.rule("[bold cyan]Texgraph Source Coverage[/bold cyan]")

    try:
        cfg = _resolve_config(Path("collection.yaml"), project)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=1)

    rep = check_source_coverage(cfg.resolved_content_dir, repo_root())
    console.print(
        f"  reading poems: [bold]{rep.reading_poems}[/bold]   "
        f"transcription witnesses: [bold]{rep.transcription_poems}[/bold]"
    )

    def _show(label: str, items: list[str], style: str) -> None:
        if items:
            console.print(f"  [{style}]{label}: {len(items)}[/{style}]")
            for it in items[:25]:
                console.print(f"    [{style}]•[/{style}] {it}")

    _show("UNREFERENCED transcription poems (would be unbuilt)", rep.unreferenced, "red")
    _show("BROKEN source links", rep.broken_source, "red")
    _show("DUPLICATE witnesses", rep.duplicate_source, "red")
    _show("poems missing a source field (warning)", rep.missing_source, "yellow")

    if rep.ok:
        console.print("\n  [green]✓ Complete[/green] — every transcription poem maps to a built reading poem.")
        raise typer.Exit(code=0)
    console.print(f"\n  [red]✗ {rep.problems} coverage problem(s).[/red]")
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# modules commands
# ---------------------------------------------------------------------------


@modules_app.command("list")
def modules_list() -> None:
    """List canonical modules and their legacy aliases."""
    from backend.core.modules import load_modules

    console.rule("[bold cyan]Texgraph Modules[/bold cyan]")
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Module", style="bold", no_wrap=True)
    table.add_column("Path")
    table.add_column("Upstream")
    table.add_column("Legacy aliases")
    table.add_column("Source", style="dim")

    for module in load_modules():
        table.add_row(
            module.id,
            module.path,
            ", ".join(module.upstream),
            ", ".join(module.legacy_aliases),
            module.source,
        )
    console.print(table)


@modules_app.command("verify")
def modules_verify(
    module_name: str = typer.Argument(..., metavar="MODULE", help="Module id or legacy alias."),
) -> None:
    """Verify a module registry entry and alias resolution."""
    from backend.core.modules import get_module, load_modules, upstream_for

    try:
        module = get_module(module_name)
    except KeyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    aliases_seen: dict[str, str] = {}
    issues: list[str] = []
    for item in load_modules():
        for alias in item.aliases:
            normalized = alias.lower().replace("_", "-")
            owner = aliases_seen.setdefault(normalized, item.id)
            if owner != item.id:
                issues.append(f"alias '{alias}' is shared by {owner} and {item.id}")

    if module.upstream:
        try:
            upstream_for(module.id)
        except KeyError as exc:
            issues.append(str(exc))

    console.rule(f"[bold cyan]Texgraph Module Verify - {module_name}[/bold cyan]")
    console.print(f"  Module:   [bold]{module.id}[/bold]")
    console.print(f"  Path:     {module.path}")
    console.print(f"  Aliases:  {', '.join(module.legacy_aliases) or '(none)'}")
    console.print(f"  Upstream: {', '.join(module.upstream) or '(none)'}")

    if issues:
        console.print(f"\n[bold red]FAILED[/bold red] {len(issues)} issue(s):")
        for issue in issues:
            console.print(f"  [red]x[/red] {issue}")
        raise typer.Exit(code=1)

    console.print("\n[bold green]OK[/bold green] module registry entry is valid.")


# ---------------------------------------------------------------------------
# migrate commands
# ---------------------------------------------------------------------------


@migrate_app.command("modules")
def migrate_modules(
    project: str = typer.Option(..., "--project", "-p", help="Project ID from workspace.yaml."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print planned moves without changing files."),
    apply: bool = typer.Option(False, "--apply", help="Apply the module directory migration."),
) -> None:
    """Migrate legacy project stage directories to canonical module directories."""
    from backend.core.modules import apply_module_migration, plan_module_migration

    if dry_run == apply:
        console.print("[red]Choose exactly one:[/red] --dry-run or --apply")
        raise typer.Exit(code=1)

    try:
        plan = plan_module_migration(project, Path.cwd())
    except (FileNotFoundError, KeyError, ValueError) as exc:
        console.print(f"[red]Migration error:[/red] {exc}")
        raise typer.Exit(code=1)

    console.rule("[bold cyan]Texgraph Module Migration[/bold cyan]")
    console.print(f"  Project:   [bold]{plan.project_id}[/bold]")
    console.print(f"  Root:      [dim]{plan.project_root}[/dim]")
    console.print(f"  Workspace: [dim]{plan.workspace_path}[/dim]\n")

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("From")
    table.add_column("To")
    table.add_column("Action")
    table.add_column("Reason")
    for step in plan.steps:
        table.add_row(step.old_name, step.new_name, step.action, step.reason)
    console.print(table)

    if plan.workspace_project_path != plan.updated_workspace_project_path:
        console.print(
            f"\n  workspace path: [bold]{plan.workspace_project_path}[/bold] -> "
            f"[bold]{plan.updated_workspace_project_path}[/bold]"
        )

    if plan.conflicts:
        console.print("\n[bold red]Refusing migration due to conflicts:[/bold red]")
        for conflict in plan.conflicts:
            console.print(f"  [red]x[/red] {conflict}")
        raise typer.Exit(code=1)

    if dry_run:
        console.print("\n[yellow]Dry run only.[/yellow] No files changed.")
        raise typer.Exit(code=0)

    try:
        apply_module_migration(plan)
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)
    console.print("\n[bold green]Applied.[/bold green] Module directories migrated.")


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
    from backend.core.workspace import find_workspace, load_workspace

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
    from backend.core.compiler import Compiler
    from backend.core.config import CollectionConfig
    from backend.core.parser import PoetryParser
    from backend.core.renderer import LaTeXRenderer

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
    tex_dir = out_dir / "tex"
    tex_dir.mkdir(exist_ok=True)
    tex_file = tex_dir / f"{_slugify(cfg.title)}.tex"
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
            "  Install it:  pip install -r backend/api/requirements-studio.txt"
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


# ---------------------------------------------------------------------------
# pdf sub-app  (pdf info / pdf text / pdf render)
# ---------------------------------------------------------------------------

_pdf_app = typer.Typer(help="PDF inspection and page rendering.  Requires poppler-utils.")
app.add_typer(_pdf_app, name="pdf")


@_pdf_app.command("info")
def pdf_info(
    pdf: Path = typer.Argument(..., help="Path to the PDF file."),
    as_json: bool = typer.Option(False, "--json", help="Output parsed metadata as JSON."),
) -> None:
    """Show PDF metadata via pdfinfo."""
    import json as _json
    import shutil
    import subprocess

    if not shutil.which("pdfinfo"):
        console.print("[red]pdfinfo not found on PATH.[/red]  Install poppler-utils.")
        raise typer.Exit(code=1)
    from backend.core.env import resolve_in_repo
    result = subprocess.run(
        ["pdfinfo", str(resolve_in_repo(pdf))],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if as_json:
        data: dict[str, str | int] = {}
        for line in result.stdout.splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            k = k.strip().lower().replace(" ", "_")
            v = v.strip()
            if k == "pages":
                try:
                    data[k] = int(v)
                    continue
                except ValueError:
                    pass
            data[k] = v
        print(_json.dumps(data, indent=2, sort_keys=True))
    else:
        print(result.stdout, end="")


@_pdf_app.command("text")
def pdf_text(
    pdf: Path = typer.Argument(..., help="Path to the PDF file."),
    first: int = typer.Option(..., "--first", "-f", help="First page number."),
    last: int = typer.Option(..., "--last", "-l", help="Last page number."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file instead of stdout."),
) -> None:
    """Extract layout text from a page range via pdftotext."""
    import shutil
    import subprocess

    if not shutil.which("pdftotext"):
        console.print("[red]pdftotext not found on PATH.[/red]  Install poppler-utils.")
        raise typer.Exit(code=1)
    from backend.core.env import resolve_in_repo
    result = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(resolve_in_repo(pdf)), "-"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    text = result.stdout.decode("utf-8", errors="replace")
    if output:
        resolve_in_repo(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


@_pdf_app.command("render")
def pdf_render(
    pdf: Path = typer.Argument(..., help="Path to the PDF file."),
    first: int = typer.Option(..., "--first", "-f", help="First page number."),
    last: int = typer.Option(..., "--last", "-l", help="Last page number."),
    prefix: Path = typer.Option(..., "--prefix", help="Output filename prefix (e.g. tmp_fw)."),
    dpi: int = typer.Option(180, "--dpi", help="Render resolution (DPI).", show_default=True),
) -> None:
    """Render PDF pages to PNG images via pdftoppm."""
    import shutil
    import subprocess

    if not shutil.which("pdftoppm"):
        console.print("[red]pdftoppm not found on PATH.[/red]  Install poppler-utils.")
        raise typer.Exit(code=1)
    from backend.core.env import repo_root, resolve_in_repo
    prefix_path = resolve_in_repo(prefix)
    prefix_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-f", str(first), "-l", str(last), "-png", "-r", str(dpi),
         str(resolve_in_repo(pdf)), str(prefix_path)],
        cwd=str(repo_root()), check=True,
    )
    created = sorted(prefix_path.parent.glob(f"{prefix_path.name}-*.png"))
    print(f"rendered={len(created)} prefix={prefix_path.relative_to(repo_root())}")


# ---------------------------------------------------------------------------
# archive sub-app  (archive files / archive download)
# ---------------------------------------------------------------------------

_archive_app = typer.Typer(help="Internet Archive source acquisition.")
app.add_typer(_archive_app, name="archive")

_IA_BASE = "https://archive.org"


@_archive_app.command("files")
def archive_files(
    identifier: str = typer.Argument(..., help="Internet Archive identifier."),
    pattern: str = typer.Option(".pdf", "--pattern", help="Filter filenames (case-insensitive)."),
) -> None:
    """List files available for an Internet Archive identifier."""
    import json as _json
    import urllib.request

    with urllib.request.urlopen(f"{_IA_BASE}/metadata/{identifier}", timeout=60) as resp:
        data = _json.loads(resp.read().decode("utf-8"))
    for item in data.get("files", []):
        name = item.get("name", "")
        if pattern and pattern.lower() not in name.lower():
            continue
        print(f"{name}\t{item.get('format', '')}\t{item.get('size', '')}")


@_archive_app.command("download")
def archive_download(
    identifier: str = typer.Argument(..., help="Internet Archive identifier."),
    filename: str = typer.Argument(..., help="Filename within the IA item."),
    output: Path = typer.Argument(..., help="Destination path inside the repo."),
) -> None:
    """Download one file from Internet Archive into the repo."""
    import shutil
    import urllib.request

    from backend.core.env import resolve_in_repo
    dest = resolve_in_repo(output)
    if dest.exists():
        console.print(f"[red]Refusing to overwrite existing file:[/red] {dest}")
        raise typer.Exit(code=1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{_IA_BASE}/download/{identifier}/{filename}"
    with urllib.request.urlopen(url, timeout=180) as resp, dest.open("wb") as target:
        shutil.copyfileobj(resp, target)
    print(f"saved {dest} ({dest.stat().st_size} bytes)")


# ---------------------------------------------------------------------------
# audit command
# ---------------------------------------------------------------------------

@app.command()
def audit(
    volume: Path = typer.Argument(
        ...,
        help="Book directory to audit (e.g. volumes/01_early/books/02_city).",
    ),
    as_json: bool = typer.Option(False, "--json", help="Output results as JSON."),
) -> None:
    """Audit a transcription book directory for completeness and correctness."""
    import json as _json

    from backend.core.audit import audit_book
    from backend.core.env import resolve_in_repo

    result = audit_book(resolve_in_repo(volume))
    if as_json:
        print(_json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"volume={result['volume']}")
        print(f"poem_count={result['poem_count']}")
        print(f"statuses={result['statuses']}")
        for key in ["issues", "forbidden_hits", "unchecked", "temporary_renders"]:
            values = result[key]
            print(f"{key}={len(values)}")
            for v in values:
                print(f"  {v}")
    bad = any(result[k] for k in ["issues", "forbidden_hits", "unchecked", "temporary_renders"])
    raise typer.Exit(code=1 if bad else 0)


# ---------------------------------------------------------------------------
# metadata command
# ---------------------------------------------------------------------------

@app.command()
def metadata(
    target: Path = typer.Argument(..., help="Book, books, volume, or volumes directory."),
    write: bool = typer.Option(False, "--write", help="Write book.json files."),
    check: bool = typer.Option(False, "--check", help="Check book.json files for staleness."),
    as_json: bool = typer.Option(False, "--json", help="Print generated metadata as JSON."),
) -> None:
    """Generate or validate per-book book.json metadata."""
    import json as _json

    from backend.core.env import repo_root, resolve_in_repo
    from backend.core.metadata import book_dirs, build_metadata

    tgt = resolve_in_repo(target)
    books = book_dirs(tgt)
    if not books:
        console.print(f"[red]No book.md files found under:[/red] {tgt.relative_to(repo_root())}")
        raise typer.Exit(code=1)

    all_meta = [build_metadata(b) for b in books]

    if write:
        for book, meta in zip(books, all_meta, strict=True):
            out = book / "book.json"
            out.write_text(_json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    issues: list[str] = []
    if check:
        root = repo_root()
        for book, meta in zip(books, all_meta, strict=True):
            path = book / "book.json"
            if not path.exists():
                issues.append(f"{book.relative_to(root)}: missing book.json")
            elif _json.loads(path.read_text(encoding="utf-8-sig")) != meta:
                issues.append(f"{book.relative_to(root)}: book.json stale or inconsistent")

    if as_json:
        print(_json.dumps(all_meta, indent=2, ensure_ascii=False))
    else:
        print(f"books={len(books)}")
        if write:
            print("wrote=book.json")
        if check:
            print(f"issues={len(issues)}")
            for issue in issues:
                print(f"  {issue}")

    raise typer.Exit(code=1 if issues else 0)


# ---------------------------------------------------------------------------
# page-map command
# ---------------------------------------------------------------------------

@app.command("page-map")
def page_map(
    offset: int = typer.Option(..., "--offset", help="scan = printed + offset"),
    printed: str = typer.Option(..., "--printed", help='Page range spec, e.g. "7-10,14,18".'),
) -> None:
    """Map printed page numbers to scan page numbers via a fixed offset."""
    from backend.core.pagemap import expand_pages

    try:
        pages = expand_pages(printed)
    except SystemExit as exc:
        console.print(f"[red]Invalid page range:[/red] {exc}")
        raise typer.Exit(code=1)
    print("printed,scan")
    for p in pages:
        print(f"{p},{p + offset}")


# ---------------------------------------------------------------------------
# plan command
# ---------------------------------------------------------------------------

@app.command()
def plan(
    document: Path = typer.Argument(..., help="Markdown project plan file."),
    check: bool = typer.Option(False, "--check", help="Fail on missing index/appendices or stale tokens."),
) -> None:
    """Inspect project plan heading structure and index readiness."""
    import re as _re

    from backend.core.env import resolve_in_repo
    from backend.core.plan import headings

    path = resolve_in_repo(document)
    if not path.exists():
        console.print(f"[red]Missing document:[/red] {path}")
        raise typer.Exit(code=1)

    rows = headings(path)

    if not check:
        for level, title, anchor in rows:
            print("  " * (level - 1) + f"- [{title}](#{anchor})")
        raise typer.Exit(code=0)

    text = path.read_text(encoding="utf-8-sig")
    issues: list[str] = []
    if not rows:
        issues.append("no markdown headings found")
    if "# Index" not in text:
        issues.append("missing '# Index' section")
    if "# Appendix" not in text and "## Appendix" not in text:
        issues.append("missing appendix headings")
    _stale_re = _re.compile(r"(?:cite[^\n]{0,40}turn\d+)|turn\d+(?:view|search|news|reddit)\d+")
    if stale := _stale_re.findall(text):
        issues.append(f"stale citation tokens found: {len(stale)}")
    anchors = [a for _, _, a in rows]
    for dup in sorted({a for a in anchors if anchors.count(a) > 1}):
        issues.append(f"duplicate heading anchor: {dup}")
    if issues:
        for issue in issues:
            print(f"ISSUE: {issue}")
        raise typer.Exit(code=1)
    print(f"ok headings={len(rows)}")


# ---------------------------------------------------------------------------
# scan command
# ---------------------------------------------------------------------------

@app.command()
def scan(
    target: Path = typer.Argument(..., help="Book, volume, or volumes directory."),
    output: Path = typer.Option(..., "--output", "-o", help="Markdown output path."),
    front_pages: int = typer.Option(25, "--front-pages", help="Pages to scan at front of source.", show_default=True),
    back_pages: int = typer.Option(12, "--back-pages", help="Pages to scan at back of source.", show_default=True),
) -> None:
    """Scan source PDFs for front/back matter keyword signals."""
    from backend.core.env import resolve_in_repo
    from backend.core.metadata import book_dirs, build_metadata
    from backend.core.scan import _write_markdown, scan_book

    tgt = resolve_in_repo(target)
    books = book_dirs(tgt)
    results = [scan_book(build_metadata(b), front_pages, back_pages) for b in books]
    _write_markdown(results, resolve_in_repo(output))
    print(f"books={len(results)} output={output}")


# ---------------------------------------------------------------------------
# Internal helper: resolve project stage root (projects/<id>/)
# ---------------------------------------------------------------------------

def _resolve_stage_root(project: Optional[str]) -> Path:
    """Return ``projects/<id>/`` — the stage root containing ingest/, proof/, etc.

    Resolves through workspace.yaml.  The workspace stores paths to the
    typeset directory (``projects/<id>/typeset``); the stage root is one
    level up.
    """
    from backend.core.modules import LEGACY_MODULE_MIGRATION, load_modules
    from backend.core.workspace import find_workspace, load_workspace

    workspace_path = find_workspace(Path.cwd())
    if workspace_path is None:
        console.print(
            "[red]No workspace.yaml found.[/red]  "
            "Run from a workspace directory or use --workspace."
        )
        raise typer.Exit(code=1)

    workspace = load_workspace(workspace_path)
    effective_id = project or workspace.default_project
    if not effective_id:
        console.print(
            "[red]No project specified and no default_project in workspace.yaml.[/red]  "
            "Use --project <id>."
        )
        raise typer.Exit(code=1)

    try:
        ref = workspace.get_project(effective_id)
    except KeyError as exc:
        console.print(f"[red]Project not found:[/red] {exc}")
        raise typer.Exit(code=1)

    # ref.path is relative to workspace root, pointing at the typeset dir.
    # Stage root is one level above.
    resolved_ref = (workspace_path.parent / ref.path).resolve()
    module_dir_names = {module.path for module in load_modules()} | set(LEGACY_MODULE_MIGRATION)
    stage_root = resolved_ref.parent if resolved_ref.name in module_dir_names else resolved_ref
    return stage_root


# ---------------------------------------------------------------------------
# verify command
# ---------------------------------------------------------------------------

@app.command()
def verify(
    stage: str = typer.Argument(
        ...,
        help="Stage to verify preconditions for "
             "(transcribe | proof | typeset | final | covers).",
    ),
    project: Optional[str] = typer.Option(
        None, "--project", "-p",
        help="Project ID from workspace.yaml.  Uses default when omitted.",
    ),
) -> None:
    """Check that the upstream stage is complete before starting STAGE.

    Reads the upstream PROMOTION.yaml and verifies all required fields.
    Exits 0 when preconditions pass; exits 1 with a report when they do not.

    Examples
    --------

        texgraph verify transcribe

        texgraph verify proof --project my-collection
    """
    from backend.core.modules import get_module, upstream_for, valid_module_aliases
    from backend.core.promotions import verify_stage

    console.rule(f"[bold cyan]Texgraph Verify — {stage}[/bold cyan]")

    try:
        module = get_module(stage)
    except KeyError:
        console.print(
            f"[red]Unknown stage:[/red] '{stage}'  "
            f"Valid: {', '.join(valid_module_aliases())}"
        )
        raise typer.Exit(code=1)
    upstream = upstream_for(module.id)
    if not upstream:
        console.print(f"[red]Module has no upstream gate:[/red] '{module.id}'")
        raise typer.Exit(code=1)

    stage_root = _resolve_stage_root(project)

    console.print(f"  Project root:   [dim]{stage_root}[/dim]")
    console.print(f"  Module:         [bold]{module.id}[/bold]")
    if module.id != stage:
        console.print(f"  Alias:          [dim]{stage}[/dim]")
    console.print(
        "  Checking:       "
        + ", ".join(f"[bold]{item.path}/PROMOTION.yaml[/bold]" for item in upstream)
    )
    console.print()

    ok, issues = verify_stage(stage_root, module.id)

    if ok:
        console.print(
            f"[bold green]OK[/bold green]  "
            f"{', '.join(item.path for item in upstream)}/PROMOTION.yaml passes all preconditions.  "
            f"[bold]{module.id}[/bold] is unlocked."
        )
        raise typer.Exit(code=0)

    console.print(f"[bold red]BLOCKED[/bold red]  {len(issues)} issue(s) must be resolved:\n")
    for issue in issues:
        console.print(f"  [red]x[/red] {issue}")
    console.print()
    console.print(
        f"Resolve the issues above, then re-run:  "
        f"[bold]texgraph verify {module.id}[/bold]"
    )
    raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# promote command
# ---------------------------------------------------------------------------

@app.command()
def promote(
    stage: str = typer.Argument(
        ...,
        help="Module to promote (e.g. sources, transcription, interior).",
    ),
    project: Optional[str] = typer.Option(
        None, "--project", "-p",
        help="Project ID from workspace.yaml.  Uses default when omitted.",
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y",
        help="Skip the confirmation prompt.",
    ),
) -> None:
    """Approve a pipeline module by writing status: approved to its PROMOTION.yaml.

    The PROMOTION.yaml must already exist (written by the module's commands or
    created manually).  This command flips status to approved so downstream
    modules can proceed.

    Examples
    --------

        texgraph promote sources --project my-collection

        texgraph promote interior --yes
    """
    from backend.core.modules import get_module, valid_module_aliases
    from backend.core.promotions import promotion_path, read_promotion, write_promotion

    console.rule(f"[bold cyan]Texgraph Promote — {stage}[/bold cyan]")

    try:
        module = get_module(stage)
    except KeyError:
        console.print(
            f"[red]Unknown module:[/red] '{stage}'  "
            f"Valid: {', '.join(valid_module_aliases())}"
        )
        raise typer.Exit(code=1)

    stage_root = _resolve_stage_root(project)
    promo = read_promotion(stage_root, module.id)

    if promo is None:
        console.print(
            f"[red]{module.path}/PROMOTION.yaml not found.[/red]\n"
            f"Complete {module.id} work first, then create the PROMOTION.yaml "
            f"before running promote."
        )
        raise typer.Exit(code=1)

    if promo.get("status") == "approved":
        console.print(
            f"[yellow]{module.path}/PROMOTION.yaml is already approved.[/yellow]"
        )
        raise typer.Exit(code=0)

    promo_file = promotion_path(stage_root, module.id)
    console.print(f"  Module:   [bold]{module.id}[/bold]")
    console.print(f"  File:     [dim]{promo_file}[/dim]")
    console.print(f"  Status:   {promo.get('status', '(unset)')} -> [bold green]approved[/bold green]")
    console.print()

    if not yes:
        confirmed = typer.confirm(f"Approve {module.id}?")
        if not confirmed:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=0)

    promo["status"] = "approved"
    write_promotion(stage_root, module.id, promo)
    console.print(f"\n[bold green]Promoted.[/bold green]  {promo_file} updated.")


# ---------------------------------------------------------------------------
# ingest sub-app
# ---------------------------------------------------------------------------

_ingest_app = typer.Typer(help="Ingest stage tools: source intake and registration.")
app.add_typer(_ingest_app, name="ingest")


@_ingest_app.command("rename")
def ingest_rename(
    file: Path = typer.Argument(..., help="Source file to ingest (will be moved, not copied)."),
    author: str = typer.Option(..., "--author", "-a", help="Author slug (e.g. gould-fletcher)."),
    year: int = typer.Option(..., "--year", "-y", help="Original publication year (4-digit)."),
    title: str = typer.Option(..., "--title", "-t", help="Title slug (e.g. irradiations-sand-and-spray)."),
    source: str = typer.Option(
        "upload",
        "--source", "-s",
        help="Source slug: archive-org | hathitrust | gutenberg | scan | upload | url",
        show_default=True,
    ),
    project: Optional[str] = typer.Option(
        None, "--project", "-p",
        help="Project ID from workspace.yaml.  Uses default when omitted.",
    ),
    pages: Optional[int] = typer.Option(
        None, "--pages",
        help="Page count (optional; can be recorded later via pdfinfo).",
    ),
    rights: str = typer.Option(
        "unknown",
        "--rights",
        help="Rights status: public_domain | cc_by | licensed | unknown",
        show_default=True,
    ),
    access_confirmed: bool = typer.Option(
        False, "--access-confirmed",
        help="Confirm rights/access have been verified.",
    ),
    notes: str = typer.Option("", "--notes", help="Optional provenance notes."),
) -> None:
    """Move a source file into the project and register it under the stable naming schema.

    The file is MOVED (not copied) to ``projects/<id>/sources/raw/<stable_name>.<ext>``.
    A provenance record is written alongside it.  The project's
    ``sources/PROMOTION.yaml`` is created or updated with the new source entry
    (status: pending — run ``texgraph promote sources`` after all sources are registered
    and access is confirmed).

    Stable naming schema: <author>_<year>_<title>_<source>.<ext>

    Examples
    --------

        texgraph ingest rename irradiations.pdf \\
            --author gould-fletcher --year 1913 \\
            --title irradiations-sand-and-spray \\
            --source archive-org --pages 120 \\
            --rights public_domain --access-confirmed

        texgraph ingest rename manuscript.docx \\
            --author smith --year 2024 --title collected-poems \\
            --source upload --access-confirmed
    """
    import hashlib
    from datetime import datetime, timezone

    from backend.core.promotions import read_promotion, write_promotion
    from backend.core.utils import slugify

    console.rule("[bold cyan]Texgraph Ingest Rename[/bold cyan]")

    # --- Validate source file -----------------------------------------------
    file = file.resolve()
    if not file.exists():
        console.print(f"[red]File not found:[/red] {file}")
        raise typer.Exit(code=1)
    if not file.is_file():
        console.print(f"[red]Not a file:[/red] {file}")
        raise typer.Exit(code=1)

    # --- Build stable name --------------------------------------------------
    author_slug = slugify(author)
    title_slug = slugify(title)
    source_slug = slugify(source)
    ext = file.suffix.lower()
    stable_name = f"{author_slug}_{year}_{title_slug}_{source_slug}{ext}"

    # --- Resolve project stage root -----------------------------------------
    stage_root = _resolve_stage_root(project)
    raw_dir = stage_root / "sources" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / stable_name

    if dest.exists():
        console.print(
            f"[red]Destination already exists:[/red] {dest}\n"
            f"  Delete it first or choose a different stable name."
        )
        raise typer.Exit(code=1)

    # --- Compute checksum before moving ------------------------------------
    console.print(f"  Source:    [dim]{file}[/dim]")
    console.print(f"  Dest:      [bold]{dest.relative_to(stage_root)}[/bold]")

    sha256 = hashlib.sha256()
    with file.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha256.update(chunk)
    checksum = sha256.hexdigest()

    # --- Move file ----------------------------------------------------------
    shutil.move(str(file), str(dest))
    console.print(f"  Moved.     sha256={checksum[:16]}…")

    # --- Write provenance file ---------------------------------------------
    ingested_at = datetime.now(timezone.utc).isoformat()
    provenance_path = raw_dir / (stable_name + ".provenance.yaml")
    provenance: dict = {
        "stable_name": stable_name,
        "original_name": file.name,
        "source_type": source_slug,
        "rights": rights,
        "access_confirmed": access_confirmed,
        "checksum_sha256": checksum,
        "ingested_at": ingested_at,
        "notes": notes,
    }
    if pages is not None:
        provenance["page_count"] = pages

    import yaml as _yaml
    provenance_path.write_text(
        _yaml.dump(provenance, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    console.print(f"  Provenance: {provenance_path.relative_to(stage_root)}")

    # --- Update sources/PROMOTION.yaml -------------------------------------
    existing = read_promotion(stage_root, "sources") or {}
    sources: list[dict] = existing.get("sources") or []

    # Remove any prior entry with the same stable_name (idempotent re-run)
    sources = [s for s in sources if s.get("stable_name") != stable_name]

    source_entry: dict = {
        "stable_name": stable_name,
        "stable_path": str(dest.relative_to(stage_root)),
        "format": ext.lstrip("."),
        "checksum_sha256": checksum,
        "access_confirmed": access_confirmed,
        "provenance_ref": str(provenance_path.relative_to(stage_root)),
    }
    if pages is not None:
        source_entry["page_count"] = pages

    sources.append(source_entry)

    promotion: dict = {
        "stage": "sources",
        "project_id": stage_root.name,
        "status": existing.get("status", "pending"),
        "naming_schema_version": 1,
        "sources": sources,
    }
    if "approved_at" in existing:
        promotion["approved_at"] = existing["approved_at"]

    promo_path = write_promotion(stage_root, "sources", promotion)
    console.print(f"  Promotion:  {promo_path.relative_to(stage_root)}")

    # --- Summary ------------------------------------------------------------
    access_note = (
        "[green]access confirmed[/green]"
        if access_confirmed
        else "[yellow]access NOT confirmed[/yellow] — set --access-confirmed when verified"
    )
    console.print(
        f"\n[bold green]Registered:[/bold green] {stable_name}\n"
        f"  Rights: {rights}  |  {access_note}\n"
        f"  Status: [yellow]pending[/yellow] — run [bold]texgraph promote sources[/bold] "
        f"once all sources are registered and access is confirmed."
    )


if __name__ == "__main__":
    app()
