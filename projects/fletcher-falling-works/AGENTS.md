# fletcher-falling-works — Project AGENTS

**Volume 4 of *John Gould Fletcher: The Complete Original Collections*** —
*The Falling Works* (1935–1946, three books). **Scaffold:** sources mostly pending acquisition; transcription not yet begun. No reading edition or buildable
interior yet.

This file closes the loop for this project. For framework/tooling work see the
repo `README.md` § Agent Framework; for series context see
`projects/fletcher-series/SERIES.md`.

## State

- Transcription witnesses (where present) live in `transcription/volumes/04_falling_works/books/<book>/poems/`.
- Source PDFs are shared in `projects/fletcher-series/sources/raw/`; rights and
  acquisition state per book are in `projects/fletcher-series/metadata/four_volume_order.md`.
- `manuscript/reading/` is empty; `interior/collection.yaml` is a stub and will
  not build until a reading edition exists.

## Next step

This volume becomes buildable the same way Volume 1 did. When its transcription is
image-checked, promote it into volume-ordered `manuscript/reading/` book sections
(one section per book), then build and verify exactly as
`projects/fletcher-early-works/AGENTS.md` describes:

```
texgraph verify-coverage --project fletcher-falling-works      # every transcription poem maps to a built reading poem
texgraph proof-build      --project fletcher-falling-works      # once reading/ is populated
```

Model all working conventions (three-section poems, keyed notes, one-poem-per-page
layout, never edit output/, never nest poems below the section level) on
`projects/fletcher-early-works/AGENTS.md`.
