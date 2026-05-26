# Texgraph Studio — Wireframe Themes

Post-corporate / Pre-Raphaelite / Indie aesthetic concept document.
All generated images are in `docs/wireframes/new/`. See INDEX.md for the full list.

---

## Philosophy

Texgraph Studio is a literary instrument. It makes poetry books. The interface should feel like the thing it makes — not like the software used to build it.

The corporate SaaS aesthetic (blue primaries, white backgrounds, floating card shadows, gradient heroes) has colonized nearly all software UIs. We refuse it entirely. Instead the interface draws from three layered traditions:

1. **Pre-Raphaelite / Arts & Crafts**: handcraft over industrial reproduction, jewel tones, organic form, elaborate ornament as structure
2. **Indie zine / Risograph**: limited color passes, deliberate imperfection, halftone as aesthetic not defect, small-press materiality
3. **8-bit pixel art**: the pixel as honest unit, the limited palette as constraint turned beauty, the demo-scene era when programs were also art objects

These aren't decorations applied to a functional skeleton. They are the aesthetic that the functional choices grow from.

---

## Theme 1: The Scriptorium
**Maps to**: Cards view (CardBrowser + PoemEditor + PropertiesPanel)

The monk's scriptorium: a long table of light, manuscript in progress, quills and ink bottles, the smell of vellum. This is where poems are written and revised. It should feel like a serious, quiet place of work — not a noisy collaborative tool.

**Key visual elements:**
- Botanical vine borders framing the three-panel layout
- Cormorant Garamond serif for all labels and headings
- JetBrains Mono for the editor text with generous line-height
- Thick pixel-art block cursor in antique gold
- YAML frontmatter region tinted lapis blue (like an illuminated initial letter)
- Section headers in CardBrowser as gold serif text, §-glyph prefix
- Properties panel as a heraldic blazon: double-rule, gold label caps, cream values

**Color emphasis:** Warm mahogany panel, walnut surface, gold and cream text

**Image files:**
- `01_scriptorium_full_layout.png` — complete three-panel layout
- `02_scriptorium_poem_chip.png` — component sheet: all chip variants
- `03_scriptorium_editor_close.png` — editor zone close-up
- `04_scriptorium_properties_panel.png` — heraldic properties panel
- `05_scriptorium_frontmatter_editor.png` — live frontmatter editing form

---

## Theme 2: The Garden Labyrinth
**Maps to**: Graph view (GraphCanvas + CardStackNode + RenderConfigPanel)

The walled garden seen from above, laid out in geometric beds with gravel paths between. Poem-nodes are flowers. Section bands are garden paths. The diamond lattice grid replaces the corporate dot-grid. Clicking a node steps into the garden and sits with the poem.

**Key visual elements:**
- Diamond lattice background grid (manuscript graph paper, not corporate dots)
- Poem nodes as worn leather cards with stacked physical depth for versions
- Section band labels: copper-stake garden labels in italic gold serif
- Node hover: gold border glow (no drop shadows)
- Version stacks: literally stacked card layers, slightly offset, visible underlayers
- RenderConfig panel as floating parchment page dropped onto the garden

**Color emphasis:** Darkest canvas, gold node borders, forest greens in section labels

**Image files:**
- `06_garden_full_canvas.png` — full graph view
- `07_garden_node_variants.png` — CardStackNode component sheet
- `08_garden_section_bands.png` — section band labels detail
- `09_garden_render_config_panel.png` — render config overlay

---

## Theme 3: The Alchemist's Forge
**Maps to**: Build view (BuildPanel + BuildLog + PDF preview)

The compilation of Markdown into typeset PDF is transmutation — raw material becoming precious form. The forge metaphor: a workshop of alembics and crucibles where the lualatex process is visible as a physical process. The log is the alchemist's journal; the PDF is the gold.

**Key visual elements:**
- Scrolling build log with CRT scanline texture (history of the transformation)
- Sienna/amber error lines (heat), forest green success lines, cream normal output
- Rotating alembic/spiral pixel icon as the build spinner
- PDF preview framed like an illuminated manuscript page in a gold window
- The whole panel has slightly warmer, more orange-tinted darkness (forge glow)

**Color emphasis:** Sienna and gold, near-black, parchment for the PDF page

**Image files:**
- `10_forge_build_panel.png` — complete build panel
- `11_forge_build_log.png` — build log close-up
- `12_forge_pdf_preview.png` — PDF preview frame

---

## Theme 4: The Oracle's Grotto
**Maps to**: Agent panel (AgentPanel + ActionChips)

The AI agent is not a chatbot widget. It is a consulting oracle — something you approach with a question and receive a considered answer. The grotto is private, purple-dark, slightly theatrical. The oracle's responses arrive as ink on parchment. Action chips are rune stones you pick up and invoke.

**Key visual elements:**
- Deeper purple-violet tinting on the panel background
- Oracle message bubbles with thick left border in violet-gold
- Text arrives as if being inked: left-to-right reveal animation
- Action chips as physical rune stones: rounded, dark, pixel icons
- Context chips showing "current situation" at top of panel
- Thick block cursor in the input field
- Pixel-art orb in the panel toggle button

**Color emphasis:** Violet, gold, deep dark, cream text on purple-dark ground

**Image files:**
- `13_oracle_agent_panel.png` — full agent panel
- `14_oracle_action_chips.png` — rune stone chip component sheet
- `15_oracle_wizard_mode.png` — project creation wizard in oracle mode

---

## Theme 5: The Archive of Codices
**Maps to**: Version management (VersionList + diff view)

Versions of a poem are manuscripts in an archive. Each variant is a physical document with its own history. The canonical version wears a wax seal. Comparing versions is holding two manuscripts side by side on a reading table.

**Key visual elements:**
- Version entries as stacked manuscript pages with physical depth and slight fan
- Canonical version sealed with a burgundy wax-seal stamp emblem
- A ribbon bookmark on the canonical card
- Diff view: two illuminated pages side by side with botanical vine divider
- Changed lines highlighted in historical annotation colors (red strikethrough, green addition)

**Color emphasis:** Deep burgundy for canonical/destruction, forest for addition, dark leather

**Image files:**
- `16_archive_version_stack.png` — version list as manuscript stack
- `17_archive_diff_view.png` — side-by-side version diff

---

## Theme 6: The Threshold Portal
**Maps to**: Login + project selection screens

The entry to the application is a threshold — a gate, an arch, an opening. Passing through it is the beginning of the work. The project selection shows the collection like books on a dark shelf: physical objects waiting to be opened.

**Key visual elements:**
- Login: arched frame (doubled-rule gold), botanical vines climbing the sides
- Application title as book-spine typography, not a logo
- Project cards as actual book covers with spine and clasp details
- New project card as a blank codex waiting to be inscribed
- William Morris acanthus background at very low opacity
- Pixel moth in corner, barely visible

**Color emphasis:** Deepest near-black, gold and cream as the only lights

**Image files:**
- `18_threshold_login.png` — login portal
- `19_threshold_project_select.png` — codex shelf project selection

---

## Theme 7: Specimens
**Maps to**: Design system reference

The specimen sheets show the design system components in isolation: how the typography renders, how the color palette behaves in context, how the ornamental border vocabulary works, how the pixel icon set looks at full scale.

**Image files:**
- `20_typeset_specimen.png` — typography specimen with all text styles
- `21_color_palette_illustration.png` — palette mood illustration (PRB style)
- `22_ornament_system.png` — border, divider, and ornament reference sheet
- `23_pixel_icon_set.png` — 8-bit pixel art icon set at 1x and 4x

---

## Theme 8: Writing Modes
**Maps to**: Special views (distraction-free editor, collection map, notes editor)

Modes that exist outside the three main views — spaces for pure writing, for seeing the whole collection as a single object, for keeping notes.

**Image files:**
- `24_distraction_free_editor.png` — full-screen writing mode (maximum darkness)
- `25_collection_map.png` — bird's-eye collection overview
- `26_empty_state_garden.png` — empty state illustration
- `27_notes_editor.png` — NOTES.md editorial journal panel

---

## Implementation Priority

Based on the wireframe review, recommended implementation order:

### Immediate (high visual impact, low complexity)
1. Swap Tailwind color tokens to the PRB palette (canvas, surface, gold, burgundy, violet)
2. Add Cormorant Garamond via Google Fonts for display type
3. Add JetBrains Mono for editor
4. Style CardBrowser section headers with serif + § glyph
5. Color-code poem type badges (PoemTypeBadge component)
6. Double-rule + botanical dividers between sections

### Near-term (new components)
7. CreatePoemModal (highest functional need)
8. FrontmatterEditor (bidirectional sync with CodeMirror)
9. Version stack visual depth in VersionList
10. Empty state illustration for new projects
11. Pixel icon set (SVG components: quill, leaf, star, orb)

### Medium-term (richer experience)
12. Distraction-free writing mode
13. Collection map overview
14. NOTES.md editor panel
15. Diff view for versions
16. Graph section bands
17. Oracle panel visual differentiation (violet tinting)

### Later (polish)
18. Canvas background texture (acanthus motif, CSS only)
19. Token-appear animation for agent streaming
20. Build log scanline effect
21. Parchment shimmer skeleton loading states
