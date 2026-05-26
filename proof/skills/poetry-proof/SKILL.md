---
name: poetry-proof
description: Proof verse transcriptions against source scans. Use for line-break fidelity, stanza correspondence, indentation accuracy, long-line and run-over handling, cycle structure, and front matter field correctness in poem files.
---

# Poetry Proof

## Use When

Load this skill when the proof task involves verse content:

- Verifying that transcribed lines match source scans line for line
- Checking stanza breaks (blank lines in Markdown match source stanza divisions)
- Auditing leading-space indentation against source
- Reviewing YAML front matter fields (`title`, `type`, `order`, `subtitle`, `epigraph`)
- Handling multi-page poems or poem cycles
- Signing off on a poem's `status` field as `checked` or `final`

Do not use for: prose paratext proof (`proof/skills/prose-proof`), cover work,
or technical documentation. If a poem combines verse body with substantial
editorial apparatus, also load `proof/skills/transcription-verification`.

## Required Reads

- `AGENTS.md`
- `proof/AGENTS.md`
- `ONTOLOGY.md § Data Schemas` — poem Markdown front matter spec
- The poem source scan (open via `texgraph pdf render` or equivalent)
- The poem file at `projects/<project_id>/typeset/content/<section>/<file>.md`

## Proof Checklist

Work through each poem in order. For each file:

### 1. Front Matter

- [ ] `title` matches the source title exactly (modulo silent drop-cap normalization)
- [ ] `type` is `poem`, `poem-cycle`, `poem-screenplay`, or `prose` — correct for content
- [ ] `order` matches position in the section (no duplicate order values)
- [ ] `subtitle`, `epigraph`, `dedication` present only if source shows them; empty strings omitted
- [ ] `status` is `transcribed` or higher; never `not_started` on a populated file

### 2. Line Fidelity

- [ ] Every source line is present; no lines added or omitted
- [ ] Line breaks match the source (do not join wrapped source lines)
- [ ] No `\\`, `<br>`, HTML entities, or code fences in body text
- [ ] Source hyphenation at line ends preserved as transcribed (do not silently join)

### 3. Stanza Structure

- [ ] Each blank line in source produces exactly one blank line in Markdown
- [ ] No extra blank lines (double stanza gaps) unless source shows a section break
- [ ] Section breaks (ornament, asterisks, rule) recorded as `---` or noted in `notes` field

### 4. Indentation

- [ ] Leading spaces match source indentation level (two leading spaces = one indent level)
- [ ] Indented lines in the source are indented in Markdown; flush lines are flush
- [ ] Do not add indentation for typographic reasons

### 5. Poem Cycles (`type: poem-cycle`)

- [ ] Internal section headings present as `## I.`, `## II.`, etc. or titled headings
- [ ] No separate files for cycle sections unless each appears as a separate contents entry
- [ ] All scan and printed page ranges recorded in front matter

### 6. Long Lines and Run-Overs

- [ ] Genuine long lines are preserved in full (not broken arbitrarily)
- [ ] Run-overs from the source are present (two extra leading spaces on continuation)
- [ ] No line breaks introduced that are not in the source

## Resolving Uncertain Readings

When a line is damaged, blurred, or ambiguous:

1. Note in the poem's `notes` YAML field: `"Line 3: reading uncertain — '[best attempt]'"`
2. Do not advance `status` to `checked` until all uncertain readings are resolved or
   explicitly accepted by the user.
3. Do not use external texts to fill uncertain readings unless the user permits.

## Changing Status

| Status | Meaning | Who sets it |
|---|---|---|
| `transcribed` | Transcribed against scan, not yet proofed | Transcriber |
| `checked` | Proofed against scan, readings verified | Proofer |
| `final` | Accepted by user; no further changes without cause | User or proofer with user approval |

Set `status: checked` only after completing the full checklist above.
Set `status: final` only with explicit user approval.

## Audit Command

The `texgraph audit` command reports `status` values across a volume:

```powershell
.\.venv\Scripts\texgraph.exe audit projects/<project_id>/transcribe/<volume> --json
```

Use this to identify poems not yet at `checked` status.

## Guardrails

- Do not alter content for editorial or stylistic reasons during proof.
- Proof is a fidelity check against the source. Editorial improvements belong in
  a subsequent editorial pass with explicit user direction.
- Do not change `type:` for typographic convenience — `type:` is a content classification.
- Cross-stage writes (modifying typeset files from proof stage) require user approval.
