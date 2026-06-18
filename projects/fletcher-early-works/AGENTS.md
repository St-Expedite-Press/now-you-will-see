# fletcher-early-works — Project AGENTS

**Volume 1 of *John Gould Fletcher: The Complete Original Collections*** — *The
Early Works*, the five self-financed 1913 London books (Book of Nature, Dominant
City, Fire and Wine, Fool's Gold, Visions of the Evening). 276 poems. This is the
built, proven volume and the workspace default project.

This file is self-contained for routine work here. Reach for the repo `README.md`
§ Agent Framework only for framework/tooling changes; for series-wide context see
`projects/fletcher-series/SERIES.md`.

## Where things live

```
transcription/volumes/01_early_works/books/<book>/poems/   ← documentary witnesses (source of truth)
manuscript/reading/<NN_book>/<poem>.md                     ← reading edition (built); three-section format
manuscript/EDITORIAL_PROCEDURE.md                          ← the editorial contract — read before editing reading files
manuscript/corrections/                                    ← proof notes, house style
interior/collection.yaml                                   ← trade review style sheet (6x9)
interior/collection_hardcover.yaml / _softcover.yaml       ← print variants
interior/output/                                           ← all build output (gitignored; never hand-edit)
```

Source PDFs and series metadata are shared in `projects/fletcher-series/`
(sources/raw, four_volume_order.md, PROJECT_PLAN.md).

## Commands (this project)

```
texgraph proof-build  --project fletcher-early-works                 # trade review proof -> output/proof/
texgraph proof-build  --config interior/collection_hardcover.yaml    # variant -> output/proof-hardcover/
texgraph proof-build  --print-ready --config interior/collection_softcover.yaml  # PDF/X -> output/print/softcover/
texgraph proof-preview --project fletcher-early-works                # render key pages to PNG (visual review)
texgraph verify-coverage --project fletcher-early-works              # every transcription poem is built (1:1)
```

Current baseline: trade proof = **534 pages, 298 units**; coverage **276 poems 1:1**.

## Conventions that close the loop

- **Editing reading poems:** follow `manuscript/EDITORIAL_PROCEDURE.md`. Poems use
  the three-section format (`## Original Lineation` / `## Editorial Relineation` /
  `## Context Notes`); the parser typesets the relineation when present, else the
  original. Context notes become keyed back-matter endnotes — lead each note with a
  line citation (`ll. 9–10 ('lemma'):`) or `Form:` so it sets apart from the gloss.
- **Layout:** one-poem-per-page, placement decided by measured height in TeX (not a
  line count); full-page recto part dividers; per-book recto title pages; per-volume
  keyed notes. Tune via `render_config` (`stanza_skip` is the inter-stanza lever,
  overridable per poem). Details: `modules/interior/skills/typesetting/SKILL.md`.
- **Never** hand-edit anything under `interior/output/`. **Never** nest a poem `.md`
  below the section level (the scanner hard-errors). Keep `source:` fields valid —
  `verify-coverage` is the gate and runs in CI.
- **Before sign-off:** rebuild, then `proof-preview` and actually look at the pages
  (book openings, dividers, short poems, notes). A sparse non-divider page is a defect.

## Pipeline gate

Stage: **manuscript → interior**. `manuscript/PROMOTION.yaml` is `pending`
(line-by-line proof against source scans, and final layout sign-off, not yet
recorded). Set it approved only after a visual proof review with the user. The
sources and transcription gates upstream are approved.
