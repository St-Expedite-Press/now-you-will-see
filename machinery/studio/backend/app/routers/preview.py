from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.exceptions import ConflictError, NotFoundError
from app.services import build_service

router = APIRouter()


@router.get("/pdf")
async def preview_pdf(project_id: str) -> FileResponse:
    state = build_service.load_build_state(project_id)
    output_dir, _tex_file, pdf_file = build_service.expected_artifacts(project_id)
    if state is not None:
        if state.get("status") != "success":
            raise ConflictError(
                f"Latest Studio build did not finish successfully: {state.get('error') or 'run a fresh build'}"
            )
        if pdf_file.exists():
            return FileResponse(str(pdf_file), media_type="application/pdf")
        raise NotFoundError("Latest Studio build reported success but no PDF was found")

    pdfs = sorted(output_dir.glob("*.pdf"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not pdfs:
        raise NotFoundError("No PDF found; run a build first")
    return FileResponse(str(pdfs[0]), media_type="application/pdf")


@router.get("/tex")
async def preview_tex(project_id: str) -> FileResponse:
    state = build_service.load_build_state(project_id)
    output_dir, tex_file, _pdf_file = build_service.expected_artifacts(project_id)
    if state is not None and state.get("tex_written") and tex_file.exists():
        return FileResponse(str(tex_file), media_type="text/plain")

    tex_files = sorted(output_dir.glob("*.tex"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not tex_files:
        raise NotFoundError("No .tex file found; run a build first")
    return FileResponse(str(tex_files[0]), media_type="text/plain")
