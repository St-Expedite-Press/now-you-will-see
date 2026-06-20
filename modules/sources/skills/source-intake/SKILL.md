---
name: source-intake
description: "Verify, normalize, and document source PDFs for transcription projects. Use when adding raw PDFs, checking source availability, running pdfinfo, recording page counts, refreshing source matter inventory, or deciding whether a volume is safe to transcribe."
module: sources
tools:
  - texgraph pdf info
  - texgraph pdf text
  - texgraph pdf render
  - texgraph archive files
  - texgraph archive download
  - texgraph ingest rename
  - texgraph scan
  - texgraph verify sources
---
# Source Intake

## Workflow

1. Confirm the full source PDF exists under `projects/<project_id>/sources/raw/` in
   the appropriate bucket subdirectory.
2. Do not transcribe from partial downloads, sample pages, screenshots, or search
   snippets.
3. Preserve source PDF bytes unchanged. If a stable filename is needed, copy by
   default; if the user explicitly asks to rename, confirm the target path does
   not already exist before moving.
4. Run PDF inspection through the repo venv:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf info <pdf>
   ```
5. For Internet Archive sources, use deterministic download:
   ```powershell
   .\.venv\Scripts\texgraph.exe archive files <identifier>
   .\.venv\Scripts\texgraph.exe archive download <identifier> <file> projects/<project_id>/sources/raw/<bucket>/<stable>.pdf
   ```
6. Do not download access-restricted items unless the user explicitly provides
   lawful source files. Record pending sources as `source_status: pending_acquisition`.
7. Record page count, provenance, and problems in
   `projects/<project_id>/sources/source_manifest.md` (create if absent).
8. Open or render title page, contents, first poem page, and final poem page
   to confirm the PDF is the intended source:
   ```powershell
   .\.venv\Scripts\texgraph.exe pdf render <pdf> --first 1 --last 5 --prefix verify_
   ```
9. Mark missing or suspect sources clearly before any transcription begins.
10. Refresh source matter signals after adding or replacing source PDFs:
    ```powershell
    .\.venv\Scripts\texgraph.exe scan projects/<project_id>/transcription/volumes --output projects/<project_id>/transcription/metadata/source_matter_inventory.md
    ```
    Visually review image-only sources and ambiguous OCR hits before creating
    source front/back matter files.
11. Do not create poem or source-matter files for missing, partial, restricted,
    or sample-only sources.

## Output

Update only source metadata unless the task explicitly asks for scaffolding.
Use `notes` fields for uncertainty rather than forcing a source into the workflow.

## Source Status Values

See `README.md § Data Schemas` for the full list:
`present`, `missing`, `working_source_reprint`, `access_restricted`, `pending_acquisition`
