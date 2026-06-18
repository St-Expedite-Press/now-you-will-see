# John Gould Fletcher: The Complete Original Collections

A four-volume scholarly POD edition. This directory holds **series-level shared
assets only** — it is not a buildable texgraph project and is not registered in
`workspace.yaml`. Each volume is its own project under `projects/`.

## Volumes

| Vol | Project | Title | Books | Years | State |
|---:|---|---|---|---|---|
| 1 | `fletcher-early-works` | The Early Works | Book of Nature, Dominant City, Fire and Wine, Fool's Gold, Visions of the Evening | 1913 | **built** (276 poems) |
| 2 | `fletcher-dominant-works` | The Dominant Works | Irradiations, Goblins and Pagodas, Japanese Prints, The Tree of Life | 1915–1918 | transcription partial |
| 3 | `fletcher-embattled-works` | The Embattled Works | Breakers and Granite, Parables, Branches of Adam, The Black Rock | 1921–1928 | scaffold |
| 4 | `fletcher-falling-works` | The Falling Works | XXIV Elegies, South Star, The Burning Mountain | 1935–1946 | scaffold |

Canonical book order, publishers, and source state: `metadata/four_volume_order.md`.
Governing editorial plan: `project_plan/PROJECT_PLAN.md`.

## Shared assets

- `sources/raw/{early_1913, middle_1915_1928, late_rights_pending}/` — original
  source PDFs, organized by era (eras span volumes, so sources are shared, not
  per-volume). Each volume's transcription witnesses derive from these.
- `metadata/` — series-level metadata (four-volume order, etc.).
- `covers/` — series cover conventions (`SCHEMA.md`, `STYLES.md`) and the
  four-volume wrap designs.

## Method

Volume 1 is the proven engine: transcription → reading edition → keyed apparatus
→ measured one-poem-per-page interior → print-ready PDF/X. Volumes 2–4 inherit
its pipeline as their content is acquired and transcribed. Run
`texgraph verify-coverage --project <volume>` after any content move to confirm
every transcription poem is built.
