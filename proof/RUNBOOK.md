# Proof Stage — Runbook

This document is the operator guide for the proof stage. It covers gate verification, audit-driven review, line-by-line checking against source scans, textual question resolution, and promotion. Every example uses *Preludes and Symphonies* (Fletcher, 1922) as the running case.

---

## What Proof Does

Proof is the quality gate between raw transcription and typesetting. Its job is to catch transcription errors, verify every uncertain reading, and confirm that the Markdown files faithfully reproduce the source. No typeset work begins until all open textual questions are resolved and the user signs off.

Nothing in `typeset/` or `final/` (direct path) may start until the proof PROMOTION.yaml carries `status: approved` and `textual_questions.open: 0`.

---

## Inputs

- Approved transcribe PROMOTION.yaml (`status: approved`)
- All poem and source-matter files under `projects/<project_id>/transcribe/`
- Source PDF at `projects/<project_id>/ingest/raw/<stable>.pdf`

## Outputs

```
projects/<project_id>/proof/
  audit/
    <book>_audit.json           ← written by texgraph audit --json
  corrections/
    <book>_corrections.md       ← agent or proofer notes
  output/
    tex/
      <slug>.tex                ← proof tex artifact (tracked)
    <slug>.pdf                  ← draft proof PDF (gitignored — for review only)
  PROMOTION.yaml
```

---

## Step 1 — Verify the transcribe gate

**Always run this first.**

```powershell
.\.venv\Scripts\texgraph.exe verify proof `
  --project fletcher-complete-original-collections
```

Exit 0 means transcription is approved and proof may proceed.

---

## Step 2 — Run the full automated audit

```powershell
.\.venv\Scripts\texgraph.exe audit `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922 `
  --json > projects/fletcher-complete-original-collections/proof/audit/preludes_1922_audit.json
```

Review the output. All of the following must be zero before promotion:

| Field | Must be |
|---|---|
| `issues` | `[]` (empty) |
| `forbidden_hits` | `[]` (empty) |
| `unchecked` | `[]` (empty) |
| `temporary_renders` | `[]` (empty) |

Any non-empty list is a blocker. Fix the underlying transcription file and re-run.

Also check metadata consistency:

```powershell
.\.venv\Scripts\texgraph.exe metadata `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922 `
  --check
```

Zero issues here means `book.json` is current and consistent with `book.md`.

---

## Step 3 — Line-by-line proof against source scans

Automated audit catches structural problems but not transcription errors. Human or agent review must compare each poem against the source scan page-by-page.

**Workflow per poem:**

1. Note `source_pages_scan` from the poem's YAML front matter
2. Render the relevant pages:

```powershell
.\.venv\Scripts\texgraph.exe pdf render `
  projects/fletcher-complete-original-collections/ingest/raw/gould-fletcher_1922_preludes-and-symphonies_ia.pdf `
  --first <scan_first> --last <scan_last> --prefix tmp_proof
```

3. Open the rendered PNG(s) alongside the `.md` poem file
4. Verify line by line:
   - Every line of verse present and in correct order
   - Line breaks match the source exactly (not wrapped or merged)
   - Indentation matches: one indent level = two leading spaces
   - Stanza breaks (blank lines) match
   - Capitalization, punctuation, and spelling match — including period at line end if printed
   - Section headings (`## I.`) present if the poem has numbered parts

5. Delete temporary render files when done:

```powershell
Remove-Item tmp_proof-*.png
```

---

## Step 4 — Record textual questions

When a passage is unclear (damaged, blurred, cropped, or ambiguous OCR), record it rather than guessing.

Create or append to `projects/fletcher-complete-original-collections/proof/corrections/preludes_1922_corrections.md`:

```markdown
## Textual Questions

### OPEN

- **`poems/045_the-blue-symphony.md` line 23**: Scan is blurred. Reads either
  "tremulous" or "tenuous". Printed page 87, scan page 95. Needs second-source verification.

### RESOLVED

- **`poems/012_irradiation-xii.md` line 8**: Confirmed "shimmering" — OCR read "shimmcring".
  Corrected in file.
```

**Rules:**
- An open textual question blocks promotion
- A resolved question must have the correction applied to the source `.md` file before it is marked resolved
- Questions about punctuation style (e.g., em-dash vs hyphen) are decided by the editorial policy, not left open

---

## Step 5 — Apply corrections

For each issue found during proof, edit the transcription file directly. Do not create separate "corrected" copies.

After corrections, re-run audit and metadata check to confirm they still pass:

```powershell
.\.venv\Scripts\texgraph.exe audit `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922

.\.venv\Scripts\texgraph.exe metadata `
  projects/fletcher-complete-original-collections/transcribe/volumes/03_later_collections/books/preludes_and_symphonies_1922 `
  --write --check
```

---

## Step 6 — Update poem statuses

When a poem has been proofed and corrected, update its `status` field:

```yaml
status: checked   # or: final (if this is the definitive reading)
```

All poems should reach at least `checked` before promotion. `final` means no further review is expected.

---

## Step 7 — Verify zero open questions

Before writing the PROMOTION.yaml, confirm your corrections file has no open items:

```markdown
## Textual Questions

### OPEN

(none)

### RESOLVED

- ... (all resolved items listed)
```

Count the resolved items — you will need the number for PROMOTION.yaml.

---

## Step 7b — Build the proof PDF

After all poems are `checked` and all textual questions are resolved, run the proof build to produce the draft tex+pdf:

```powershell
.\.venv\Scripts\texgraph.exe proof-build `
  --project fletcher-complete-original-collections
```

This writes:
- `proof/output/tex/<slug>.tex` — the proof tex artifact (tracked in git)
- `proof/output/<slug>.pdf` — the draft PDF for review (gitignored)

The command prints the relative `proof_pdf` path for use in `PROMOTION.yaml`.

---

## Step 8 — User approves and promotes

When all poems are `checked` or `final`, all audit output is clean, all textual questions are resolved, and the proof PDF has been reviewed, write the PROMOTION.yaml:

```yaml
# projects/fletcher-complete-original-collections/proof/PROMOTION.yaml
stage: proof
status: approved
approved_at: <ISO 8601>
proof_pdf: "proof/output/<slug>.pdf"  # path from proof-build output
textual_questions:
  open: 0
  resolved: <N>
volumes:
  - id: 01_early_works
    books:
      - id: <book_id>
        poem_count: <N>
        all_status_at_least: checked
user_accepted_layout: true            # set true after reviewing the proof PDF
notes: ""
```

`proof_pdf` is the path printed by `texgraph proof-build`. `user_accepted_layout` must be set to `true` after the user has reviewed the proof PDF — this is the editorial sign-off that the text layout is acceptable for the typeset stage to begin.

Verify the gate passes:

```powershell
.\.venv\Scripts\texgraph.exe verify typeset `
  --project fletcher-complete-original-collections
```

Exit 0 means typeset work may begin.

---

## Failure modes and what to do

| Symptom | Likely cause | Resolution |
|---|---|---|
| `verify proof` fails | Transcribe PROMOTION.yaml missing or `status: pending` | Return to transcribe stage |
| `audit` reports forbidden tokens after corrections | Introduced during editing | Remove the token and re-run |
| Poem status still `transcribed` | Agent forgot to update after proof | Update `status: checked` in the poem file |
| Open textual questions remain | Second-source not yet consulted | Find a second copy (HathiTrust, Project Gutenberg) or note as unresolvable |
| `metadata --check` fails after corrections | `book.md` year/field edited without re-running `--write` | Run `metadata --write` then `--check` |
| `verify typeset` fails | `textual_questions.open` not 0, or PROMOTION.yaml status not `approved` | Fix and re-verify |

---

## What counts as a textual question vs an editorial decision

| Situation | Classification |
|---|---|
| Can't read a word due to scan damage | Textual question — open |
| OCR clearly wrong, source legible | Not a question — fix it directly |
| Two plausible spellings, same era | Textual question — research and resolve |
| Em-dash vs double hyphen | Editorial decision — follow editorial_policy.md |
| Missing punctuation at line end | Editorial decision — follow editorial_policy.md |
| Inconsistent capitalization across stanzas | Transcribe exactly as printed; note if suspicious |

---

## Commands reference

```powershell
.\.venv\Scripts\texgraph.exe verify proof --project <id>
.\.venv\Scripts\texgraph.exe verify typeset --project <id>
.\.venv\Scripts\texgraph.exe audit <book_dir> [--json]
.\.venv\Scripts\texgraph.exe metadata <book_dir> --write --check
.\.venv\Scripts\texgraph.exe pdf render <pdf> --first N --last N --prefix P
.\.venv\Scripts\texgraph.exe pdf text <pdf> --first N --last N
.\.venv\Scripts\texgraph.exe proof-build --project <id>
```

---

## Skills to load

| Task | Skill |
|---|---|
| Verse proof (line-by-line) | `proof/skills/poetry-proof/SKILL.md` |
| Prose or paratext proof | `proof/skills/prose-proof/SKILL.md` |
| Cross-file status and metadata audit | `proof/skills/transcription-verification/SKILL.md` |
| Editorial voice and apparatus | `proof/skills/persona-editorial/SKILL.md` |
