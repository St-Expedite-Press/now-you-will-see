"""Texgraph Studio — FastAPI application entry point."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import AgentError, BuildError, ConflictError, NotFoundError, ValidationError
from app.routers import agent, build, covers, poems, preview, projects, render_config, sections, versions

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers ---

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(BuildError)
async def build_error_handler(request: Request, exc: BuildError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": str(exc)})


# --- Routers ---

app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(sections.router, prefix="/api/projects/{project_id}/sections", tags=["sections"])
app.include_router(poems.router, prefix="/api/projects/{project_id}/sections/{section_id}/poems", tags=["poems"])
app.include_router(versions.router, prefix="/api/projects/{project_id}/sections/{section_id}/poems/{poem_slug}/versions", tags=["versions"])
app.include_router(render_config.router, prefix="/api/projects/{project_id}/render-config", tags=["render-config"])
app.include_router(build.router, prefix="/api/projects/{project_id}/build", tags=["build"])
app.include_router(preview.router, prefix="/api/projects/{project_id}/preview", tags=["preview"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(covers.router, prefix="/api/covers", tags=["covers"])

# --- Health check ---

@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


# --- SPA static files (must be last — catches all unmatched routes) ---

_static_dir = Path(__file__).parents[1] / "static"
if _static_dir.is_dir():
    _assets_dir = _static_dir / "assets"
    if _assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="spa-assets")

    @app.get("/", include_in_schema=False)
    async def spa_root() -> FileResponse:
        return FileResponse(_static_dir / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        requested = (_static_dir / full_path).resolve()
        static_root = _static_dir.resolve()

        if static_root in requested.parents and requested.is_file():
            return FileResponse(requested)

        return FileResponse(static_root / "index.html")
