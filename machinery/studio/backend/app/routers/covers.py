"""Cover studio assets and typography regime data."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import yaml
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.models.cover import CoverAsset, CoverAssetsResponse, CoverRegimesResponse, TypographyRegime

router = APIRouter()

# app/routers/covers.py -> app/ -> backend/ -> studio/ -> machinery/ -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[5]
_PROJECTS_DIR = _REPO_ROOT / "projects"
_UMBRELLA_PROJECT = "fletcher-complete-original-collections"
_UMBRELLA_COVERS_DIR = _PROJECTS_DIR / _UMBRELLA_PROJECT / "covers"

_REGIME_DEFS: dict[str, dict[str, str]] = {
    "A": {
        "name": "The Creole Small Press",
        "face": "Cormorant Garamond",
        "alignment": "justified",
        "distinctive": "crossroads ornament; generous symmetric margins; centered poem titles in small caps",
    },
    "B": {
        "name": "The Imagist Score",
        "face": "EB Garamond",
        "alignment": "flush-left ragged",
        "distinctive": "silence column; bilingual margin strip; no running heads on poem pages; fixed-height slugs",
    },
    "C": {
        "name": "The Apparatus Edition",
        "face": "TeX Gyre Pagella",
        "alignment": "justified",
        "distinctive": "2.5pt black dividing rule; dual prose/monospace apparatus stream; scholarly editorial apparatus",
    },
    "D": {
        "name": "The Devotional Arc",
        "face": "Gentium Plus",
        "alignment": "justified",
        "distinctive": "variable leading arc across volumes; gladius accumulation; HODIE threshold; novena Vol IV",
    },
}


def _has_cover_data(path: Path) -> bool:
    return path.is_dir() and ((path / "STYLES.md").exists() or any(path.rglob("*.png")))


def _covers_dir(project_id: str | None = None) -> Path:
    if project_id:
        project_covers = _PROJECTS_DIR / project_id / "covers"
        if _has_cover_data(project_covers):
            return project_covers
    return _UMBRELLA_COVERS_DIR


def _active_regime(covers_dir: Path) -> str | None:
    """Parse active_regime from STYLES.md front matter."""
    styles_file = covers_dir / "STYLES.md"
    if not styles_file.exists():
        return None
    text = styles_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm = yaml.safe_load(text[4:end]) or {}
    val = fm.get("active_regime")
    return str(val) if val else None


def _parse_asset(rel_path: Path, project_id: str | None) -> CoverAsset | None:
    """Parse cover filename schema: {author}_{book}_{role}_{variant}.{ext}."""
    parts = rel_path.stem.split("_", 3)
    if len(parts) != 4:
        return None
    author, book, role, variant = parts
    rel_url = quote(str(rel_path).replace("\\", "/"))
    query = f"?project_id={quote(project_id)}" if project_id else ""
    return CoverAsset(
        filename=rel_path.name,
        rel_path=str(rel_path).replace("\\", "/"),
        author=author,
        book=book,
        role=role,
        variant=variant,
        url=f"/api/covers/assets/{rel_url}{query}",
    )


@router.get("", response_model=CoverAssetsResponse)
async def list_cover_assets(project_id: str | None = Query(default=None)) -> CoverAssetsResponse:
    covers_dir = _covers_dir(project_id)
    if not covers_dir.exists():
        return CoverAssetsResponse(assets=[], total=0)

    effective_project = project_id if covers_dir == (_PROJECTS_DIR / str(project_id) / "covers") else None
    assets: list[CoverAsset] = []
    for png in sorted(covers_dir.rglob("*.png")):
        rel = png.relative_to(covers_dir)
        asset = _parse_asset(rel, effective_project)
        if asset:
            assets.append(asset)
    return CoverAssetsResponse(assets=assets, total=len(assets))


@router.get("/regimes", response_model=CoverRegimesResponse)
async def get_regimes(project_id: str | None = Query(default=None)) -> CoverRegimesResponse:
    active = _active_regime(_covers_dir(project_id))
    regimes = [
        TypographyRegime(
            id=regime_id,
            active=(regime_id == active),
            **info,
        )
        for regime_id, info in _REGIME_DEFS.items()
    ]
    return CoverRegimesResponse(regimes=regimes, active_regime=active)


@router.get("/assets/{file_path:path}")
async def get_cover_asset(
    file_path: str,
    project_id: str | None = Query(default=None),
) -> FileResponse:
    covers_dir = _covers_dir(project_id)
    asset_path = (covers_dir / file_path).resolve()
    covers_resolved = covers_dir.resolve()
    if not (asset_path == covers_resolved or covers_resolved in asset_path.parents):
        raise HTTPException(status_code=403, detail="Access denied")
    if not asset_path.exists():
        raise HTTPException(status_code=404, detail=f"Asset not found: {file_path}")
    return FileResponse(asset_path)
