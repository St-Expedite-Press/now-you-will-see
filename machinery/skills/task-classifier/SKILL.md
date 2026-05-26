# Task Classifier

Load this skill when the job type of an incoming request is ambiguous. Work
through the decision tree, declare a classification, then return to the root
dispatcher to route.

---

## Decision Tree

Answer each question in order. The first match wins.

**1. Does this request name a pipeline stage and describe artifact-producing work?**
Source files, transcription, proof corrections, PDF builds, cover assets, release packaging.
→ `pipeline/<stage>`. Route to the relevant stage `AGENTS.md`.

**2. Does this request describe finding, evaluating, or comparing sources without yet committing them?**
"Find me a public domain edition of X", "what scans of Y exist", "check rights on Z."
→ `research`. Use `ingest/AGENTS.md` for source context. Offer to persist a `.research.md` note.

**3. Does this request mention a stage name but ask a question about how to proceed — no execution implied?**
"How should I handle uncertain readings?", "what does the proof stage require?", "should I use prose or poem type?"
→ `conversation`. Respond directly. Do not open a stage `AGENTS.md`.

**4. Does this request describe a change to CLI, infrastructure, documentation, or skills?**
"Add a command", "update ONTOLOGY.md", "rewrite this skill", "fix a bug in the build system."
→ `tooling`. Route to `machinery/AGENTS.md`.

**5. Is this a planning discussion, scoping question, or feedback with no named artifact target?**
"What should we build next?", "how does this pipeline work?", "rate these options."
→ `conversation`. Respond directly.

If none match: ask the user — "Is this pipeline work, a research task, or a discussion?" — before proceeding.

---

## Composite Path Declaration

When a request spans multiple types, declare the full path before starting:

```
Classification: research → pipeline/ingest
Phase 1 — research: identify candidate sources and rights status
Phase 2 — pipeline/ingest: texgraph ingest rename (after user approval)
Transition: user approves candidate → begin ingest
```

Announce the composite path to the user at the start of the session so they
know what phases are coming and where the handoff points are.

---

## Research Artifact Decision

At the end of a research phase, before transitioning to the next phase:

> "I found [X]. Do you want me to save this as a research note in
> `projects/<id>/ingest/<topic>.research.md`, or keep it in the conversation?"

If user says save: write a `.research.md` file with sources found, rights
status, and recommendation. Then transition to ingest or conversation as
appropriate.

If user says no: proceed without persisting. The conversation is the record.

---

## Tooling → Pipeline Transition

After tooling work completes and the user has confirmed the change:

> "The [tooling change] is done. Do you want to continue into [stage] work now,
> or end here?"

If user confirms: re-classify the next task as `pipeline/<stage>` and route to
the appropriate stage `AGENTS.md`. The session continues — no restart needed.

---

## Artifact Checklist by Job Type

| Type | Produces | Written where |
|---|---|---|
| `pipeline/ingest` | PROMOTION.yaml + ingest/raw/ files | `projects/<id>/ingest/` |
| `pipeline/transcribe` | PROMOTION.yaml + transcription files | `projects/<id>/transcribe/` |
| `pipeline/proof` | PROMOTION.yaml + correction notes | `projects/<id>/proof/` |
| `pipeline/typeset` | PROMOTION.yaml + interior PDF | `projects/<id>/typeset/` |
| `pipeline/covers` | Cover files | `projects/<id>/covers/` |
| `pipeline/front-end` | Publication files | `projects/<id>/front-end/` |
| `pipeline/final` | Release package | `projects/<id>/final/` |
| `research` | `<topic>.research.md` note (optional) | `projects/<id>/ingest/` |
| `conversation` | None | — |
| `tooling` | Code or doc change | `machinery/` or repo root |
