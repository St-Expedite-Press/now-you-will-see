---
name: prose-proof
description: Proof prose transcriptions (prefaces, essays, paratext, source matter) against source scans. Use for paragraph integrity, quotation mark normalization, correct type tagging, and front matter field accuracy in prose files.
---

# Prose Proof

## Use When

Load this skill when the proof task involves prose content:

- Verifying paragraph breaks in prefaces, essays, introductions, dedications
- Checking that source blockquotes or epigraphs are present and correctly marked
- Auditing that `type: prose` is set correctly (not `type: poem`)
- Reviewing quotation marks, dashes, and typographic punctuation
- Signing off on `status` for source paratext or editorial prose files

Do not use for: verse proof (`proof/skills/poetry-proof`), cover work, or
infrastructure documentation.

## Required Reads

- `AGENTS.md`
- `modules/manuscript/AGENTS.md`
- `ONTOLOGY.md § Data Schemas` — source matter front matter spec, poem front matter spec
- The prose source scan (open via `texgraph pdf render`)
- The file being proofed

## Proof Checklist

### 1. Front Matter

- [ ] `type: prose` is set (not `type: poem`) — verify against source content
- [ ] For source paratext: `matter_type` is set to the correct value
  (`dedication`, `preface`, `contents`, `epigraph`, `acknowledgment`,
  `illustration_list`, `frontispiece`, `dedicatory_poem`, `colophon`,
  `publisher_ad`, `appendix`)
- [ ] `title` matches the source heading or is `"[Untitled]"` if absent
- [ ] `status` reflects actual completion, not assumption
- [ ] `source_pages_scan` and `source_pages_printed` present and accurate

### 2. Paragraph Integrity

- [ ] Each paragraph break in the source is present as a blank line in Markdown
- [ ] No paragraphs merged or split without source evidence
- [ ] No forced line breaks (`\\`, `<br>`) — prose flows as paragraphs

### 3. Quotation Marks and Punctuation

- [ ] Opening `"` and closing `"` (curly quotes) preserved as transcribed
- [ ] Em-dashes `—` preserved; not replaced with `--` or `-`
- [ ] Ellipses `...` or `…` match source convention
- [ ] No normalization of period/comma placement relative to quotes unless
  the source is ambiguous and the `notes` field records the decision

### 4. Blockquotes and Epigraphs

- [ ] Indented quoted matter in source is marked as `>` blockquote in Markdown
- [ ] Poem-within-prose quotations: if the source shows verse lines within prose,
  transcribe with preserved line breaks using `>` prefix on each line
- [ ] Epigraph fields in YAML match source placement (book-level `epigraph` vs.
  inline blockquote)

### 5. Section Headings

- [ ] Source section titles within a prose piece appear as `##` headings
- [ ] No heading level invented (do not add headings not present in source)

### 6. Special Characters

- [ ] Non-ASCII characters present and correct: accents, ligatures, currency symbols
- [ ] No HTML entities (`&amp;`, `&mdash;`, etc.) — use the literal Unicode character

## Status Protocol

| Status | Meaning |
|---|---|
| `transcribed` | Transcribed; not yet proofed |
| `checked` | Proofed against scan by proofer |
| `final` | User-approved; no further changes without cause |

Set `status: checked` only after completing the full checklist.

## Guardrails

- Do not modernize spelling, punctuation, or usage during proof.
- Do not alter the `type:` field unless it is genuinely misclassified.
- Proof is fidelity to source. All editorial decisions require user direction and
  belong in a separate editorial pass.
- Cross-stage writes require user approval.
