# fletcher-dominant-works — Project AGENTS

**Volume 2 of *John Gould Fletcher: The Complete Original Collections*** —
*The Dominant Works* (1915–1918, four books). **Scaffold:** Irradiations and Goblins and Pagodas are transcribed; Japanese Prints and The Tree of Life are not. No reading edition or buildable
interior yet.

This file closes the loop for this project. For framework/tooling work see the
repo `README.md` § Agent Framework; for series context see
`projects/fletcher-series/SERIES.md`.

## State

- Transcription witnesses (where present) live in `transcription/volumes/02_dominant_works/books/<book>/poems/`.
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
texgraph verify-coverage --project fletcher-dominant-works      # every transcription poem maps to a built reading poem
texgraph proof-build      --project fletcher-dominant-works      # once reading/ is populated
```

Model all working conventions (three-section poems, keyed notes, one-poem-per-page
layout, never edit output/, never nest poems below the section level) on
`projects/fletcher-early-works/AGENTS.md`.
