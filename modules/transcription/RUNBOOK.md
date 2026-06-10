# Transcribe Stage — Runbook

This document is the operator guide for the transcribe stage. It covers gate verification, volume scaffolding, poem transcription, metadata validation, and promotion. Every example uses *Preludes and Symphonies* (Fletcher, 1922) as the running case.

---

## What Transcribe Does

Transcription converts source PDF pages into clean, structured Markdown files — one file per poem, organized into volumes and books. It also captures front/back matter, records page mappings, and validates metadata before handing work to manuscript/interior modules.

Nothing in `manuscript/` or `interior/` may start until the transcription PROMOTION.yaml carries `status: approved`.

---

## Inputs

- Approved ingest PROMOTION.yaml (`status: approved`)
- Source PDF at `projects/<project_id>/sources/raw/<stable>.pdf`
- Volume structure decision (how the book divides into books/sections)
- Transcription policy (from `transcribe/metadata/editorial_policy.md`)

## Outputs

```
projects/<project_id>/transcription/
  metadata/
    editorial_policy.md
    transcription_plans/
      <volume_plan>.md
    source_matter_inventory.md        ← written by texgraph scan
  volumes/
    <volume>/
      volume.md                       ← volume front matter
      books/
        <book>/
          book.md                     ← book manifest
          book.json                   ← written by texgraph metadata --write
          poems/
            <slug>.md                 ← one file per poem
          front_matter/               ← dedications, title pages, etc.
          back_matter/                ← notes, indices, etc.
  PROMOTION.yaml
```

---

## Step 1 — Verify the ingest gate

**Always run this first.** If it fails, stop and resolve the ingest stage.

```powershell
.\.venv\Scripts\texgraph.exe verify transcribe `
  --project fletcher-complete-original-collections
```

Exit 0 means the source is approved and you may proceed.

---

## Step 2 — Map the source structure

Before creating any files, understand what you are transcribing.

```powershell
# Extract the table of contents pages as text
.\.venv\Scripts\texgraph.exe pdf text `
  projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf `
  --first 1 --last 15

# Render the first 15 pages as images for visual inspection
.\.venv\Scripts\texgraph.exe pdf render `
  projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf `
  --first 1 --last 15 --prefix tmp_toc
```

For *Preludes and Symphonies* (1922) the book divides into two parts:
- **Irradiations: Sand and Spray** — free-verse irradiations and the long sand-and-spray poems
- **Goblins and Pagodas** — the Symphonies sequence and the Japanese-influenced poems

Decide whether these map to one book or two within the volume. Convention for this project: each originally-published volume becomes one `book/` directory.

Use `texgraph page-map` to record the offset between printed page numbers and scan (PDF) page numbers — they almost always differ due to front matter:

```powershell
# Example: if printed page 1 = scan page 9
.\.venv\Scripts\texgraph.exe page-map --offset 8 --printed "1-156"
```

Record this offset in the book manifest (see Step 4).

---

## Step 3 — Scaffold the volume and book directories

Create the directory structure. For *Preludes and Symphonies* inside the Fletcher project:

```
projects/fletcher-complete-original-collections/transcribe/volumes/
  03_later_collections/
    volume.md
    books/
      preludes_and_symphonies_1922/
        book.md
        poems/
        front_matter/
        back_matter/
```

**volume.md** front matter:

```yaml
---
title: "Later Collections"
volume_order: 3
series: "John Gould Fletcher: The Complete Original Collections"
---
```

**book.md** front matter:

```yaml
---
title: "Preludes and Symphonies"
book_order: 1
author: "John Gould Fletcher"
publisher: "Macmillan"
place: "New York"
year: 1922
source_pdf: "projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf"
source_status: present
pdf_pages: <N>
rights_status: public_domain
transcription_status: in_progress
notes: []
---

# Preludes and Symphonies

- [ ] Irradiations section
- [ ] Sand and Spray section
- [ ] Goblins and Pagodas section
- [ ] Symphonies sequence
```

The checklist items drive the `unchecked` count in `texgraph audit`. Mark each `[x]` when its poems are transcribed and checked.

---

## Step 4 — Transcribe front matter

Dedications, title pages, half-titles, and epigraphs go in `front_matter/`. Each gets its own `.md` file.

Example: `front_matter/dedication.md`

```yaml
---
matter_type: dedication
matter_section: front
source_pages_scan: [5]
source_pages_printed: null
status: transcribed
notes: []
---

To Amy Lowell
```

Load `modules/transcription/skills/source-matter/SKILL.md` for the full rules on matter type tags and formatting.

---

## Step 5 — Transcribe poems

Each poem gets one file under `poems/`. Filename is a zero-padded order slug:

```
poems/
  001_irradiation-i.md
  002_irradiation-ii.md
  ...
  045_the-blue-symphony.md
  ...
```

**Poem file template:**

```yaml
---
title: "Irradiation I"
book: "Preludes and Symphonies"
book_order: 1
poem_order: 1
source_pdf: "projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf"
source_pages_scan: [17]
source_pages_printed: [9]
status: transcribed
notes: []
---

# Irradiation I

Over the rooftops race the shadows of clouds;
...
```

**Transcription rules (load `modules/transcription/skills/poem-transcription/SKILL.md` for full detail):**

- Preserve every line break exactly as printed
- Represent one indent level as two leading spaces
- No `<br>`, `&nbsp;`, HTML, or code fences — these fail `texgraph audit`
- Use `---` only for YAML fences, never as a poem separator
- For poems with internal section headings (e.g. the Symphonies), use `## I.` / `## II.` within the file
- `status` field: `pending` → `transcribed` → `checked` → `final`

**Render pages before transcribing uncertain passages:**

```powershell
.\.venv\Scripts\texgraph.exe pdf render `
  projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf `
  --first 17 --last 17 --prefix tmp_poem001
```

---

## Step 6 — Validate as you go

Run these after each book section is complete, not just at the end.

```powershell
# Check for forbidden tokens, missing fields, and unchecked items
.\.venv\Scripts\texgraph.exe audit `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922

# Generate/update book.json metadata
.\.venv\Scripts\texgraph.exe metadata `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922 `
  --write --check

# Scan source PDFs for front/back matter signals (run after all books done)
.\.venv\Scripts\texgraph.exe scan `
  projects/fletcher-complete-original-collections/transcribe/volumes `
  --output projects/fletcher-complete-original-collections/transcribe/metadata/source_matter_inventory.md
```

**`texgraph audit` checks:**
- Every poem has `source_pages_scan` and `source_pages_printed` set (not null)
- No forbidden markup tokens (`\`\`\``, `&nbsp;`, `<br`, `page-break`, `PAGE BREAK`)
- `book.md` exists and has no unchecked `- [ ]` items
- No `tmp_*.png` files left in repo root

All of these must be clean before promotion.

---

## Step 7 — Mark all checklist items complete

Go back to `book.md` and mark all sections `[x]`:

```markdown
- [x] Irradiations section
- [x] Sand and Spray section
- [x] Goblins and Pagodas section
- [x] Symphonies sequence
```

Update `transcription_status: complete` in the front matter.

---

## Step 8 — User approves and promotes

When the user has reviewed a representative sample of the transcription against the source scans, write the PROMOTION.yaml:

```yaml
# projects/fletcher-complete-original-collections/transcription/PROMOTION.yaml
stage: transcribe
status: approved
approved_at: <ISO 8601>
policy_accepted: true
all_statuses_at_least: transcribed
uncertain_readings_accepted: false
volumes:
  - id: 03_later_collections
    books:
      - id: preludes_and_symphonies_1922
        transcription_status: complete
        poem_count: <N>
notes: ""
```

Verify the gate passes:

```powershell
.\.venv\Scripts\texgraph.exe verify interior `
  --project fletcher-complete-original-collections
```

Exit 0 means manuscript/interior work may begin.

---

## Failure modes and what to do

| Symptom | Likely cause | Resolution |
|---|---|---|
| `verify transcribe` fails | Ingest PROMOTION.yaml missing or not approved | Return to ingest stage |
| `audit` reports forbidden tokens | HTML or markdown markup in a poem file | Remove `<br>`, `&nbsp;`, code fences |
| `audit` reports null `source_pages_scan` | Front matter not filled in | Add scan and printed page numbers |
| `audit` reports unchecked items | `book.md` checklist has `- [ ]` lines | Complete or mark complete the section |
| `metadata --check` reports stale | `book.md` fields changed after last `--write` | Re-run with `--write` flag |
| `verify interior` fails after approval | PROMOTION.yaml `status` not `approved` | Edit and set `status: approved` |

---

## Commands reference

```powershell
.\.venv\Scripts\texgraph.exe verify transcribe --project <id>
.\.venv\Scripts\texgraph.exe verify interior --project <id>
.\.venv\Scripts\texgraph.exe pdf text <pdf> --first N --last N
.\.venv\Scripts\texgraph.exe pdf render <pdf> --first N --last N --prefix P
.\.venv\Scripts\texgraph.exe page-map --offset N --printed "<ranges>"
.\.venv\Scripts\texgraph.exe audit <book_dir>
.\.venv\Scripts\texgraph.exe metadata <volumes_dir> --write --check
.\.venv\Scripts\texgraph.exe scan <volumes_dir> --output <path>
.\.venv\Scripts\texgraph.exe plan <plan.md> --check
```

---

## Skills to load

| Task | Skill |
|---|---|
| Transcribing verse | `modules/transcription/skills/poem-transcription/SKILL.md` |
| Transcribing prose or paratext | `modules/transcription/skills/prose-transcription/SKILL.md` |
| Transcribing dedications, prefaces, colophons | `modules/transcription/skills/source-matter/SKILL.md` |
| Planning a multi-book volume | `modules/transcription/skills/volume-planning/SKILL.md` |
| Planning a multi-volume project | `modules/transcription/skills/project-planning/SKILL.md` |
