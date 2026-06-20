"""Build service for the parse -> render -> compile pipeline.

Streams log lines via an async generator consumed by the WebSocket router.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

from app.core.exceptions import BuildError
from app.services import project_service

_src = Path(__file__).parents[4] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

BUILD_STATE_FILE = ".studio-build-state.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_state_path(output_dir: Path) -> Path:
    return output_dir / BUILD_STATE_FILE


def _write_build_state(output_dir: Path, state: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    build_state_path(output_dir).write_text(
        json.dumps(state, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_build_state(project_id: str) -> dict[str, object] | None:
    detail = project_service.get_project(project_id)
    output_dir = Path(detail.path) / detail.meta.output_dir
    state_path = build_state_path(output_dir)
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def expected_artifacts(project_id: str) -> tuple[Path, Path, Path]:
    from backend.core.utils import slugify

    detail = project_service.get_project(project_id)
    project_root = Path(detail.path)
    output_dir = project_root / detail.meta.output_dir
    stem = slugify(detail.meta.title)
    return output_dir, output_dir / f"{stem}.tex", output_dir / f"{stem}.pdf"


async def stream_build(project_id: str, draft: bool = False) -> AsyncIterator[str]:
    """Yield log lines as strings; raise BuildError on hard failure."""
    from backend.core.compiler import Compiler
    from backend.core.config import CollectionConfig
    from backend.core.parser import PoetryParser
    from backend.core.renderer import LaTeXRenderer
    from backend.core.utils import slugify

    detail = project_service.get_project(project_id)
    project_root = Path(detail.path)
    collection_yaml = project_root / "collection.yaml"

    yield f"[info] Loading config: {collection_yaml}\n"
    try:
        cfg = CollectionConfig.from_yaml(collection_yaml)
    except Exception as exc:
        raise BuildError(str(exc)) from exc

    if draft:
        cfg.draft_mode = True

    out_dir = cfg.ensure_output_dir()
    stem = slugify(cfg.title)
    tex_file = out_dir / f"{stem}.tex"
    pdf_file = out_dir / f"{stem}.pdf"
    state: dict[str, object] = {
        "status": "running",
        "project_id": project_id,
        "draft": cfg.draft_mode,
        "started_at": _utc_now(),
        "finished_at": None,
        "tex_path": str(tex_file),
        "pdf_path": str(pdf_file),
        "tex_written": False,
        "pdf_written": False,
        "error": "",
    }
    _write_build_state(out_dir, state)

    try:
        yield f"[info] Parsing content: {cfg.resolved_content_dir}\n"
        parser = PoetryParser()
        sections = parser.scan_collection(cfg.resolved_content_dir)

        poem_count = sum(len(section.poems) for section in sections)
        yield f"[info] Parsed {poem_count} poem(s) in {len(sections)} section(s)\n"

        yield "[info] Rendering LaTeX...\n"
        renderer = LaTeXRenderer()
        collection_data = {"config": cfg.as_dict(), "sections": sections}
        tex_source = renderer.render(collection_data)

        tex_file.write_text(tex_source, encoding="utf-8")
        state["tex_written"] = True
        _write_build_state(out_dir, state)
        yield f"[info] LaTeX written: {tex_file}\n"

        compiler = Compiler(lualatex_path=cfg.lualatex_path)
        if not compiler.check_available():
            raise BuildError(
                f"lualatex is unavailable at '{cfg.lualatex_path}'; refusing to present a stale PDF as fresh output"
            )

        runs = 1 if cfg.draft_mode else 2
        yield f"[info] Running lualatex ({runs} pass(es))...\n"

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: compiler.compile(tex_file, out_dir, runs=runs, draft=cfg.draft_mode),
        )

        for line in result.warnings or []:
            yield f"[warn] {line}\n"
            await asyncio.sleep(0)

        if not result.success:
            for err in result.errors or []:
                yield f"[error] {err}\n"
            raise BuildError("lualatex compilation failed")

        state.update({
            "status": "success",
            "finished_at": _utc_now(),
            "pdf_written": bool(result.pdf_path and result.pdf_path.exists()),
            "error": "",
        })
        _write_build_state(out_dir, state)
        yield f"[success] PDF written: {result.pdf_path}\n"
    except BuildError as exc:
        state.update({
            "status": "failed",
            "finished_at": _utc_now(),
            "pdf_written": pdf_file.exists(),
            "error": str(exc),
        })
        _write_build_state(out_dir, state)
        raise
    except Exception as exc:
        state.update({
            "status": "failed",
            "finished_at": _utc_now(),
            "pdf_written": pdf_file.exists(),
            "error": str(exc),
        })
        _write_build_state(out_dir, state)
        raise BuildError(str(exc)) from exc

