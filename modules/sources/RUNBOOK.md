# Sources Stage — Runbook

This document is the operator guide for the sources stage. It covers source discovery, download, naming, verification, and promotion. Every example uses *Preludes and Symphonies* (Fletcher, 1922) as the running case.

---

## What the Sources Stage Does

The sources stage owns the boundary between the outside world and the repo. Its job is to locate a source PDF, download it from a known archive, give it a stable filename, record its provenance, and let the user approve it before any transcription work begins.

Nothing in `transcription/` may start until the sources PROMOTION.yaml carries `status: approved`.

---

## Inputs

- A source identifier (Internet Archive ID, direct URL, or user-supplied file)
- Rights/access confirmation from the user
- Desired stable title slug and publication year

## Outputs

```
projects/<project_id>/sources/
  raw/
    <stable_name>.pdf                   ← renamed, certified source
    <stable_name>.provenance.yaml       ← written by texgraph ingest rename
  source_manifest.md                    ← maintained by hand or agent
  PROMOTION.yaml                        ← written pending, approved by user
```

---

## Step 1 — Find the source on Internet Archive

Search the Internet Archive for the identifier. *Preludes and Symphonies* was published by Macmillan in 1922 and is in the public domain.

```powershell
# List known files for a candidate identifier
.\.venv\Scripts\texgraph.exe archive files preludesandsymph00flet
```

If the identifier is uncertain, search archive.org directly and paste the URL slug here. IA identifiers follow the pattern `<shorttitle><sequence><authorabbrev>` — e.g. `preludesandsymph00flet`. Confirm you have the right edition (Macmillan 1922, not a later reprint) before downloading.

Expected output of `archive files`:
```
preludesandsymph00flet_djvu.txt    DjVuTXT    ...
preludesandsymph00flet.pdf         Text PDF   ...
preludesandsymph00flet_jp2.zip     ZIP        ...
```

Choose the `Text PDF` entry if available; it has OCR embedded and will improve `texgraph pdf text` output. If only a scanned PDF is available, note `source_status: present` (not `working_source_reprint`).

---

## Step 2 — Download the source

```powershell
.\.venv\Scripts\texgraph.exe archive download `
  preludesandsymph00flet `
  preludesandsymph00flet.pdf `
  projects/fletcher-early-works/sources/raw/preludes_and_symphonies_1922_ia.pdf
```

The destination path is **not** the final stable name — it is a working download target. We rename it in Step 4.

---

## Step 3 — Verify the download

Confirm the PDF is intact and matches the intended source before spending any effort on it.

```powershell
# Page count and basic metadata
.\.venv\Scripts\texgraph.exe pdf info `
  projects/fletcher-early-works/sources/raw/preludes_and_symphonies_1922_ia.pdf

# Render first 5 pages as images to confirm title page / edition
.\.venv\Scripts\texgraph.exe pdf render `
  projects/fletcher-early-works/sources/raw/preludes_and_symphonies_1922_ia.pdf `
  --first 1 --last 5 --prefix tmp_verify
```

Open the rendered PNGs and confirm:
- Title page reads *Preludes and Symphonies* by John Gould Fletcher
- Publisher line reads Macmillan (not Constable or a later reprint)
- Copyright page shows 1922
- No pages appear blank, cut off, or scrambled

Delete the `tmp_verify-*.png` files after confirming.

```powershell
Remove-Item tmp_verify-*.png
```

---

## Step 4 — Rename to stable filename and record provenance

```powershell
.\.venv\Scripts\texgraph.exe ingest rename `
  projects/fletcher-early-works/sources/raw/preludes_and_symphonies_1922_ia.pdf `
  --author gould-fletcher `
  --year 1922 `
  --title preludes-and-symphonies `
  --source ia `
  --project fletcher-early-works
```

This command:
1. Moves the file to `gould-fletcher_1922_preludes-and-symphonies_ia.pdf`
2. Writes `gould-fletcher_1922_preludes-and-symphonies_ia.provenance.yaml` alongside it
3. Creates or updates `projects/fletcher-early-works/sources/PROMOTION.yaml` with `status: pending`

The stable filename schema is:

```
<author_slug>_<year>_<title_slug>_<source_slug>.<ext>
```

After renaming, the working download path no longer exists. Do not reference it again.

---

## Step 5 — Review and complete the provenance record

Open the generated provenance file and fill in any missing fields:

```
projects/fletcher-early-works/sources/raw/
  gould-fletcher_1922_preludes-and-symphonies_ia.provenance.yaml
```

Required fields before approval:

```yaml
source: ia                           # ia | upload | hathi | other
identifier: preludesandsymph00flet   # IA identifier or URL
rights_status: public_domain         # public_domain | unknown | access_restricted
access_confirmed: true               # must be true to approve
page_count: <N>                      # from pdf info output
sha256: <hash>                       # written by ingest rename
ingested_at: <ISO 8601>              # written by ingest rename
notes: []
```

For a pre-1928 US publication with no renewal, `rights_status: public_domain` is correct.

---

## Step 6 — Update source_manifest.md

Open or create `projects/fletcher-early-works/sources/source_manifest.md` and add an entry:

```markdown
## gould-fletcher_1922_preludes-and-symphonies_ia.pdf

- **Edition:** Preludes and Symphonies, Macmillan, New York, 1922
- **IA identifier:** preludesandsymph00flet
- **Pages:** <N>
- **Rights:** public_domain
- **Source quality:** Text PDF with embedded OCR
- **Notes:** First combined collection of Irradiations and Goblins and Pagodas material.
```

---

## Step 7 — User approves and promotes

Review all of the above. When the source set is confirmed, edit the PROMOTION.yaml to approve:

```yaml
# projects/fletcher-early-works/sources/PROMOTION.yaml
stage: sources
status: approved
approved_at: <ISO 8601>
sources:
  - gould-fletcher_1922_preludes-and-symphonies_ia.pdf
notes: "Macmillan 1922 first combined edition. Public domain. 156 pages. Text PDF."
```

Verify the gate passes:

```powershell
.\.venv\Scripts\texgraph.exe verify transcription `
  --project fletcher-early-works
```

Exit 0 means transcription work may begin.

---

## Failure modes and what to do

| Symptom | Likely cause | Resolution |
|---|---|---|
| `archive files` returns nothing | Wrong identifier | Search archive.org manually; use IA search |
| Download is 0 bytes or corrupt | Network issue or access restriction | Re-download; check `access_confirmed` in provenance |
| Rendered pages are wrong edition | IA has multiple scans | Find the correct identifier; check publication date on title page |
| `pdf info` shows 0 pages | Corrupted download | Re-download; verify SHA-256 |
| `verify transcription` fails | PROMOTION.yaml missing or `status: pending` | Complete approval steps above |

---

## Commands reference

```powershell
.\.venv\Scripts\texgraph.exe archive files <identifier>
.\.venv\Scripts\texgraph.exe archive download <id> <filename> <dest>
.\.venv\Scripts\texgraph.exe pdf info <pdf>
.\.venv\Scripts\texgraph.exe pdf text <pdf> --first N --last N
.\.venv\Scripts\texgraph.exe pdf render <pdf> --first N --last N --prefix P
.\.venv\Scripts\texgraph.exe ingest rename <file> --author A --year Y --title T --source S --project <id>
.\.venv\Scripts\texgraph.exe verify transcription --project <id>
```
