---
name: source-intake
description: Verify, normalize, and document source PDFs for the Fletcher scanned-book transcription repo. Use when adding raw PDFs, checking source availability, running pdfinfo, recording page counts, refreshing source matter inventory, or deciding whether a volume is safe to transcribe.
---

# Source Intake

## Workflow

1. Confirm the full source PDF exists in the correct `projects/fletcher-complete-original-collections/ingest/raw/` bucket:
   `early_1913/`, `middle_1915_1928/`, or `late_rights_pending/`.
2. Do not transcribe from partial downloads, sample pages, screenshots, or search
   snippets.
3. Preserve source PDF bytes unchanged. If a stable filename is needed, copy by
   default; if the user explicitly asks to rename, first confirm the target path
   does not already exist, then move the file to the stable name.
4. Run PDF inspection through the repo venv when possible:
   `fletcher pdf info <pdf>`.
5. For Internet Archive sources, prefer deterministic inspection/download:
   `fletcher archive files <identifier>` and
   `fletcher archive download <identifier> <file> raw\<bucket>\<stable>.pdf`.
6. Permission is cleared for all four falling-volume books. Do not download
   access-restricted items unless the user explicitly provides lawful source
   files. Record pending sources as `pending_acquisition`.
7. Record page count, provenance, and problems in `projects/fletcher-complete-original-collections/transcribe/metadata/source_manifest.md`.
8. Open or render front matter, title page, contents, first poem page, and final
   poem page to confirm the PDF is the intended book.
9. Mark missing or suspect sources clearly before any transcription begins.
10. Refresh source matter signals after adding or replacing source PDFs:
    `fletcher scan volumes --output metadata\source_matter_inventory.md`.
    Visually review image-only sources and ambiguous OCR hits before creating
    source front/back matter files.
11. If the source is image-only or OCR-poor, render likely front/back matter
    pages and add a short visual-review note to `projects/fletcher-complete-original-collections/transcribe/metadata/source_matter_inventory.md`.
12. Do not create poem or source-matter files for missing, partial, restricted,
    or sample-only sources.

## Output

Update only source metadata unless the task explicitly asks for scaffolding.
Use notes for uncertainty rather than forcing a source into the workflow.

