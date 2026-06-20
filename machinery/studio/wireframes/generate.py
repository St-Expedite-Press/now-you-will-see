"""
Generate Texgraph Studio wireframe images via DALL-E 3.
Run from repo root: python docs/wireframes/generate.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    # Try loading from .env
    env_path = Path(__file__).parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("OPENAI_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip()
                break

OUT_DIR = Path(__file__).parent / "new"
OUT_DIR.mkdir(exist_ok=True)

# ── Shared aesthetic description injected into every prompt ─────────────────

AESTHETIC = """
Dark UI mockup. Warm near-black background (#0d0a07, aged oak wood tone, not pure black).
Antique gold (#8b6914) as primary accent color. Deep burgundy (#7a1a2e) as secondary.
Aged cream (#e8dcc8) text on dark surfaces.
Pre-Raphaelite botanical ornaments: dense foliage, vines, thorns, and leaves woven into
the UI chrome as structural borders and corner pieces — not decoration applied on top,
but integral to the frame. William Morris acanthus-leaf pattern at very low opacity
as canvas background texture. Jewel-saturated color, flat gilded ornament, no gradients.
Indie zine / risograph aesthetic: two-color print feel, slight misregistration, halftone
texture in shadow areas, rough hand-drawn quality to decorative elements.
8-bit pixel-art accents mixed organically: pixel-art icons (quill, leaf, star, eye, rune)
at icon sizes, chunky pixel borders on certain elements, 8px grid ornaments.
Serif display typography (Cormorant Garamond style) for headings and section labels,
light-weight sans for UI chrome, JetBrains Mono for code/frontmatter regions.
Double-rule panel borders. Corner ornaments on highlighted panels.
No blue colors anywhere. No white backgrounds. No drop shadows. No corporate SaaS feel.
This is a literary instrument, not a dashboard. Every element should feel handcrafted.
"""

# ── Prompts organized by theme ───────────────────────────────────────────────

PROMPTS = [

    # ─── THEME 1: THE SCRIPTORIUM (Card Editor) ────────────────────────────

    {
        "name": "01_scriptorium_full_layout",
        "theme": "scriptorium",
        "title": "The Scriptorium — Full Card Editor Layout",
        "prompt": f"""
UI wireframe mockup of a poetry editing application — The Scriptorium.
Three-panel dark layout:
LEFT PANEL (240px): A list of manuscript sections as a vertical scroll. Each section
header is in Cormorant Garamond serif, gold color, with a small pixel-art leaf icon.
Under each section: 4-6 poem chips — worn leather colored rectangles with cream title
text, small type badge (color-coded), line count. Thin botanical vine dividers between
sections. Panel background: dark mahogany. A § glyph before each section name in fraktur style.
CENTER PANEL: A large dark-walnut writing area. At top, a thin header strip showing
section › poem title in antique gold. A CodeMirror-style text editor filled with
Markdown poem text (YAML frontmatter in lapis-tinted region, body text in warm cream
on near-black). A thick pixel-art block cursor. Generous line height. Subtle paper
grain texture. A small "Saved" indicator in muted gold.
RIGHT PANEL (256px): Properties sidebar titled "METADATA" in gold serif caps.
Fields: type, order, lines. Each label in muted cream, value in brighter cream.
A "VERSIONS" subsection with 2-3 stacked version entries, the canonical one starred.
{AESTHETIC}
Style: detailed UI mockup, not a sketch. Show actual text content. Landscape 16:9.
"""
    },

    {
        "name": "02_scriptorium_poem_chip",
        "theme": "scriptorium",
        "title": "The Scriptorium — Poem Chip Component Sheet",
        "prompt": f"""
Component reference sheet showing multiple variations of a 'poem chip' UI element for
a dark literary poetry editing application. Warm near-black background.
Show 8 different chip variants in a grid layout:
1. Standard poem chip: leather-brown rectangle, cream title, muted type badge, line count
2. Active/selected chip: gold border, slightly lighter background, glowing
3. Poem-cycle type chip: violet badge labeled "cycle" in pixel font
4. Prose type chip: amber badge
5. Poem-screenplay chip: rose/burgundy badge
6. Chip with version count indicator: small stacked-layers pixel icon, "v3" in pixel font
7. Chip with warning indicator: sienna color shift, tiny pixel exclamation
8. Section-title chip: different shape, italic serif title, no badge
Each chip has a thin botanical vine or rule separating it from the next.
Show the chip in both collapsed section and expanded section contexts.
Labels showing dimensions: ~220px wide, ~32px tall.
{AESTHETIC}
Style: detailed component reference mockup, dark background, all chips visible. Portrait.
"""
    },

    {
        "name": "03_scriptorium_editor_close",
        "theme": "scriptorium",
        "title": "The Scriptorium — Editor Zone Close-Up",
        "prompt": f"""
Close-up UI mockup of a poetry text editor panel — like a monk's writing desk.
Dark warm background (#1a1410). A CodeMirror-style editor showing a poem in Markdown:
- YAML frontmatter region at top: slightly lapis-tinted background (#1a3a5c tinted dark),
  monospace font, showing fields: title, type, order, epigraph
- A thin gold rule separating frontmatter from body
- Poem body: cream text on dark, generous 1.6 line-height, JetBrains Mono
  Stanzas clearly separated by extra space. 3 stanzas of verse visible.
- A thick block cursor (pixel art style) blinking in line 8
- Line numbers in muted gold on the left gutter
- A very subtle paper grain texture over the whole editor surface
- At the very top: a thin header bar with poem filename in small monospace,
  and a "Save" button that has a pixel-art quill icon, gold border, not filled

PRB botanical border: at the very top of the editor panel, a horizontal botanical
ornament — vines and leaves in gold, 8px tall, spanning the full width.
At the right margin: a thin vertical vine border, very subtle.
{AESTHETIC}
Close-up, filling most of frame. Dark and intimate. Landscape.
"""
    },

    {
        "name": "04_scriptorium_properties_panel",
        "theme": "scriptorium",
        "title": "The Scriptorium — Properties Panel (Heraldic Blazon Style)",
        "prompt": f"""
Close-up UI mockup of a properties/metadata sidebar panel for a poetry application.
Dark mahogany background. Panel titled "METADATA" in antique gold Cormorant Garamond
all-caps with wide letter-spacing and a decorative double-rule beneath.

Metadata fields displayed as a heraldic-style blazon:
- Each field name is in small gold serif caps: TYPE · ORDER · LINES · SUBTITLE
- Field values in larger cream serif text beneath each label
- Thin gold rules separating each field, with a tiny diamond ornament in the center

Below the metadata, a section titled "VERSIONS" with same header style.
Show 3 version entries:
1. "Draft v1" — stacked card icon (2 layers), 32 lines, ☆ star (uncanonical)
2. "Revised" — 36 lines, ☆ star
3. "Current" — 38 lines, ★ filled gold star (canonical), slightly highlighted row

At the bottom, a botanical corner ornament in the lower right.
The whole panel has a thin double-rule gold border on the left edge.
{AESTHETIC}
Tall portrait aspect ratio, showing the full panel.
"""
    },

    {
        "name": "05_scriptorium_frontmatter_editor",
        "theme": "scriptorium",
        "title": "The Scriptorium — Live Frontmatter Editor",
        "prompt": f"""
UI mockup of a structured frontmatter editing panel for a poetry application.
The panel allows editing poem metadata as form fields that sync with the raw Markdown.
Dark warm background, antique gold accents.

Title: "POEM PROPERTIES" in Cormorant Garamond gold serif with decorative underline.
Form fields arranged in a clean column:
- Title field: larger serif input, cream text on dark, gold underline (no box border)
- Type dropdown: showing "poem" selected, small leaf icon
- Order: small number input
- Subtitle: single-line text input
- Epigraph: multi-line textarea, showing short verse quote in italic cream
- Dedication: single-line, currently empty, ghost placeholder text

Each field label is in muted gold small-caps above the input.
Thin rules between field groups. Botanical vine ornament on one edge.
A small pixel-art quill icon in the corner.
Show the "sync" relationship: a small arrow pointing right labeled "→ editor syncs"
{AESTHETIC}
Portrait, showing the full panel cleanly.
"""
    },

    # ─── THEME 2: THE GARDEN LABYRINTH (Graph Assembly) ───────────────────

    {
        "name": "06_garden_full_canvas",
        "theme": "garden",
        "title": "The Garden Labyrinth — Full Graph Canvas",
        "prompt": f"""
UI wireframe mockup of a poetry collection graph assembly view — The Garden Labyrinth.
The graph canvas fills most of the screen. Dark near-black background with a very subtle
diamond lattice pattern (like graph paper for manuscripts, gold lines at 15% opacity).

Poem nodes displayed as CardStackNode elements scattered across the canvas:
- Each node is a worn leather card (dark warm rectangle) with:
  * Poem title in cream serif (Cormorant Garamond style)
  * Type badge in pixel font (small, color-coded)
  * Line count in muted gold
  * Nodes with 2+ versions have a stacked-card depth effect: 2 slightly offset
    underlayers visible, giving a physical stack appearance
  * Gold border that glows slightly on hover

Section organization: poems are loosely grouped by section, with very subtle horizontal
band labels for each section — "I. Vibrations of the Dented Spheres" in gold italic serif,
like a garden bed label on a copper stake.

In the lower-right: a RenderConfig panel overlay — a small dark panel with
"RENDER CONFIG" header and the cascade levels shown (Global → Section → Poem).

Minimap in corner: tiny version of the full canvas.
Navigation controls: zoom in/out as pixel-art buttons.

The overall feel: an overgrown walled garden seen from above, with poem-flowers scattered
through it. The diamond grid suggests garden geometry. The section bands are gravel paths.
{AESTHETIC}
Wide landscape mockup showing the full canvas experience.
"""
    },

    {
        "name": "07_garden_node_variants",
        "theme": "garden",
        "title": "The Garden — CardStackNode Variants",
        "prompt": f"""
Component reference sheet showing CardStackNode variants for a poetry graph canvas.
Dark background with faint diamond grid.

Show 6 node variants:
1. Single version node: simple card, cream title, gold border
2. Two-version stack: card with one underlayer visible (slightly rotated/offset)
3. Three-version stack: card with two underlayers, noticeably deeper stack
4. Selected/active node: bright gold border glow, slightly larger
5. Poem-cycle node: violet border tint, small spiral pixel icon
6. Section-title node: different shape (wider, flatter), italic serif title, no type badge

Show the node states in a grid with labels. Include the hover tooltip popup for one node:
small dark panel showing full metadata (title, type, order, line count, version count).

Include a small annotation showing node anatomy with labels:
- title area
- type badge (pixel font)
- depth layers (the stacked cards)
- version count indicator
- canonical star

The nodes should feel like physical objects — manuscript pages laid on a dark table.
{AESTHETIC}
Reference sheet layout, landscape, multiple nodes clearly visible.
"""
    },

    {
        "name": "08_garden_section_bands",
        "theme": "garden",
        "title": "The Garden — Section Band Labels",
        "prompt": f"""
Detail UI mockup showing the section band labels in the graph canvas view.
Dark background with diamond lattice texture.

Show 3 section bands as horizontal garden-path dividers:
Each band is a very subtle horizontal stripe across the canvas with:
- Section name in gold italic Cormorant Garamond: "I. Vibrations of the Dented Spheres"
- A thin botanical rule (vines/leaves in gold) running the full width of the band
- Section metadata in small muted text: poem count, total lines
- A small pixel-art leaf icon at the left end

Below each band: the poem nodes for that section, loosely arranged.
Show 4-5 nodes under the first band, 3 under the second, 6 under the third.

The garden path feel: the bands are stone paths between garden beds.
The nodes are flowers growing from the beds.
Negative space between bands feels like open garden.

Include one node that is cross-highlighted because it's selected — gold glow,
with a dashed line connecting it to the corresponding band label.
{AESTHETIC}
Wide landscape showing multiple bands and their nodes. Atmospheric.
"""
    },

    {
        "name": "09_garden_render_config_panel",
        "theme": "garden",
        "title": "The Garden — Render Config Panel Overlay",
        "prompt": f"""
Close-up of a RenderConfig panel overlay in a poetry graph canvas view.
The panel floats over the dark canvas like an illuminated page.
Dark mahogany background with thin gold double-rule border. Small botanical corner ornaments.

Title: "RENDER CONFIGURATION" in gold serif all-caps with decorative underline.

Show the cascade layers:
GLOBAL layer:
  mainfont: EB Garamond · fontsize: 11pt · paperwidth: 5.5in

SECTION layer (I. Vibrations):
  fontsize: 10.5pt (overrides global)

POEM layer (Harmonikum):
  verse_parskip: 2pt (overrides section)

RESOLVED section:
A clean table showing the final merged values.
Each field-value pair on its own line, with a small arrow → showing which level
the value came from.

At the bottom: edit buttons for each layer, pixel-art key icons.
The panel has a slight texture and depth — it looks like a physical properties sheet
dropped onto the garden canvas.
{AESTHETIC}
Portrait/square panel, showing the full overlay clearly against a dark canvas background.
"""
    },

    # ─── THEME 3: THE ALCHEMIST'S FORGE (Build View) ──────────────────────

    {
        "name": "10_forge_build_panel",
        "theme": "forge",
        "title": "The Alchemist's Forge — Build Panel",
        "prompt": f"""
UI wireframe mockup of a build/compile panel for a poetry-to-PDF application —
The Alchemist's Forge. The transmutation of Markdown into a PDF book.
Dark near-black background, sienna/amber warmth.

Left section: Build controls
- "BUILD" button: large, antique gold border, pixel-art alembic/spiral icon, cream text
- "DRAFT" button: smaller, muted, dashed border
- Status indicator: "Building…" with a rotating spiral pixel-art animation frame shown
- Build mode toggles: "Full Collection" / "Draft Mode" as small toggle chips

Center section: Build log (scrolling)
The log looks like an illuminated scroll unrolling:
- Each line in JetBrains Mono, cream on near-black
- Error lines in sienna/burnt-orange
- Success lines in forest green
- Warning lines in amber/gold
- The scroll has very subtle horizontal scan lines (CRT effect)
- At the top of the scroll: a pixel-art alembic dripping, decorative header
- Show 15 lines of lualatex output: package loads, page calculations, success

Right section: PDF Preview
A dark-bordered frame containing a small PDF preview.
The preview page itself is shown in parchment/cream — an actual formatted poetry page
with title, epigraph, and verse body visible (content made up).
A thin gold ornamental border around the iframe.
A "OPEN FULL SIZE" link in small gold text below.

The overall vibe: a medieval forge or alchemist's study, but the "furnace" is lualatex.
{AESTHETIC}
Wide landscape showing the three sections of the build panel.
"""
    },

    {
        "name": "11_forge_build_log",
        "theme": "forge",
        "title": "The Alchemist's Forge — Build Log Close-Up",
        "prompt": f"""
Close-up of a streaming build log panel in an alchemist's forge aesthetic.
Dark near-black background. The log looks like a scroll or a telegram ticker.

Show 20 lines of LaTeX compilation output in JetBrains Mono:
- Normal lines: cream text
- Lines starting with "(" or ")" in muted gold (package loads)
- Lines with "Warning" in amber
- Lines with "Error" in sienna/burnt red, slightly brighter
- Final line: "Output written on collection.pdf (148 pages)" in green

At the top of the panel: a thin horizontal header bar reading
"COMPILATION LOG" in gold pixel font with a tiny alembic icon and a timestamp.

Visual texture: very faint scanline effect (horizontal lines at 2px intervals, 3% opacity)
gives the whole log a CRT terminal feel.

On the right edge: a thin progress indicator — a vertical bar that fills from bottom to top
as the build progresses, in antique gold.

Bottom: shows "148 pages · 3 passes · 4.2s" in small muted text.

The log feels like watching a medieval scribe's hand working — you see the process.
{AESTHETIC}
Tall portrait, showing the log panel filling the frame.
"""
    },

    {
        "name": "12_forge_pdf_preview",
        "theme": "forge",
        "title": "The Alchemist's Forge — PDF Preview Frame",
        "prompt": f"""
UI mockup of a PDF preview panel in a poetry collection build application.
The preview frame is set into a dark panel like a window opening onto parchment.

The frame itself: dark mahogany border with a thin botanical vine ornament running around
the inner edge. Pixel-art corner ornaments at all four corners. Gold outer border.

Inside the frame: a rendered poetry page in warm parchment/cream.
The page shows:
- Collection title "LIFT WIND / LOVE HEAT" in Cormorant Garamond, centered, medium size
- A horizontal rule beneath
- A poem: "Harmonikum" as title, then verse stanzas
- Generous margins, good typography — it actually looks like a real book page
- Page number at bottom

Around the frame: the dark forge background.
Below the frame: controls — "◀ Previous Page" "Page 12 of 148" "Next Page ▶"
in small pixel font. Also: "Open Full Size" and "Open .tex" as text links.

The effect should be: the transmutation is complete — from raw Markdown in the editor
to this beautiful typeset page. Show the satisfaction of the finished object.
{AESTHETIC}
Portrait-ish, showing the full preview frame with comfortable margin. Dark and warm.
"""
    },

    # ─── THEME 4: THE ORACLE'S GROTTO (Agent Panel) ───────────────────────

    {
        "name": "13_oracle_agent_panel",
        "theme": "oracle",
        "title": "The Oracle's Grotto — Agent Chat Panel",
        "prompt": f"""
UI wireframe mockup of an AI agent chat panel — The Oracle's Grotto.
The panel slides in from the right side of the screen, 320px wide.
Dark violet-tinged background (#1a1020 — darker and more purple than the rest of the UI).
Thin dashed violet border on the left edge where it meets the main UI.

Panel header: "⬡ THE ORACLE" in medium Cormorant Garamond gold, small pixel rune icons.
Context chips row: small rounded chips showing "Harmonikum · §03 · chat mode"
in small pixel font, muted violet border.

Message history (scrollable):
USER message bubble: right-aligned, dark leather background, cream text, no border
ORACLE message bubble: left-aligned, dark violet (#2a1a40) background, cream text,
thin violet-gold left border (thick left rule). Cormorant Garamond for message text.

Show one exchange:
User: "What's the structural relationship between the cycle poems in section III?"
Oracle: [2 paragraphs of thoughtful literary analysis, cream serif text]
Then below the oracle message: a row of ACTION CHIPS:
Small horizontal chips like rune stones: "Show in Graph" "Open poem" "Add to Notes"
Each chip has a pixel-art rune or leaf icon, gold border, muted text.

Input area at bottom:
Multi-line textarea, dark background, thin gold border.
"Ask the oracle…" as placeholder text in ghost color.
A small pixel quill icon and "↵ Send" text.

The whole panel should feel like consulting a mystical oracle in a grotto — dark,
intimate, purple-lit, slightly theatrical. Not like a chat widget.
{AESTHETIC}
Tall portrait showing the full agent panel.
"""
    },

    {
        "name": "14_oracle_action_chips",
        "theme": "oracle",
        "title": "The Oracle — Action Chips (Rune Stones)",
        "prompt": f"""
Component reference sheet for AI agent action chips — styled as rune stones.
Dark violet background. Multiple chip variants displayed in a loose arrangement.

Chip anatomy: small rounded pill shape, ~100-180px wide, 28px tall.
Gold or violet border, dark interior, small pixel-art icon on left, text label.

Show these chips:
1. "⬡ Show in Graph" — gold border, eye pixel icon
2. "📜 Open Version" — violet border, scroll pixel icon
3. "✒ Edit Poem" — gold border, quill pixel icon
4. "🌿 Add to Section" — forest border, leaf icon
5. "⚗ Rebuild" — sienna border, alembic icon
6. "🔮 Explain Structure" — violet border, orb icon
7. "⭐ Set Canonical" — gold border, star icon
8. "📖 Open in Editor" — mahogany border, codex icon

Show chips in three states:
- Default: muted colors
- Hover: brightened border, slight glow
- Active/pressed: inverted (light background, dark text)

Group chips by category with small labels:
"NAVIGATION" / "CONTENT" / "BUILD" / "ANALYSIS"

The chips should feel like physical rune-stones or spell components from a grimoire.
{AESTHETIC}
Component sheet, dark background, all variants visible, some overlap for organic feel.
"""
    },

    {
        "name": "15_oracle_wizard_mode",
        "theme": "oracle",
        "title": "The Oracle — Project Creation Wizard",
        "prompt": f"""
UI mockup of a multi-step project creation wizard for a poetry collection application.
The Oracle is guiding the user through creating a new project.
Dark violet-tinted background, oracle-grotto aesthetic.

Show the wizard at Step 2 of 5: "COLLECTION METADATA"

Step indicator: horizontal row of 5 small diamond-ornament markers.
Steps 1 is filled (gold). Step 2 is active (glowing gold). Steps 3-5 are dim.
Connected by thin gold lines like a chain.

Main area: A "conversation" style — the Oracle's guidance appears as serif text
above the form:
"Your collection has a name. Now — who wrote it? Give me the author's name
as it should appear on the spine."

Below: Large elegant form fields
- Author name: large cream serif input field, gold underline, no box
- Publisher: elegant serif input
- Year: small number input with vintage number styling
- ISBN: monospace input (13 digits), shown partially filled

Submit button: "Continue to Publisher →" in Cormorant Garamond, gold border, no fill.
Back link: "← Return" in muted small text.

At the bottom right: a small pixel-art moth or spiral — the wizard's emblem.
{AESTHETIC}
Mostly centered layout, dark with violet and gold. Intimate and theatrical.
"""
    },

    # ─── THEME 5: THE ARCHIVE OF CODICES (Version Management) ─────────────

    {
        "name": "16_archive_version_stack",
        "theme": "archive",
        "title": "The Archive — Version Stack Visualization",
        "prompt": f"""
UI mockup of a version management panel for a poetry application —
The Archive of Codices, a library of manuscript variants.
Dark warm background, deep burgundy accents.

Show a version list for a poem called "Harmonikum" with 4 versions:

The versions are displayed as a stack of manuscript pages that fan out slightly:
Each version entry is a card-like row, slightly offset from the one before,
giving the impression of stacked physical manuscripts.

Version 1 (bottom of stack): "Draft — March 2025" 32 lines, ☆ uncanonical
Version 2: "Revised v1 — April 2025" 36 lines, ☆ uncanonical
Version 3: "Workshop edit — May 2025" 34 lines, ☆ uncanonical
Version 4 (top/front, canonical): "Current — June 2025" 38 lines, ★ canonical
  - This one has a wax seal stamp visual: a small circular emblem in burgundy
    with "★ CANONICAL" text — like a medieval document seal

Each entry shows: version name in serif, line count in muted text, creation date.
A burgundy ribbon runs down the left edge of the canonical card.
A star button (☆/★) on each entry to promote it to canonical.

Header: "CODEX VARIANTS" in gold serif with botanical divider beneath.
{AESTHETIC}
Tall portrait showing the stacked manuscripts clearly.
"""
    },

    {
        "name": "17_archive_diff_view",
        "theme": "archive",
        "title": "The Archive — Poem Version Diff",
        "prompt": f"""
UI mockup of a side-by-side version comparison (diff) view for poetry editing.
Two manuscript panels side by side, showing two versions of the same poem.

Panel A (left, labeled "DRAFT — March 2025"):
Dark warm background, cream text, JetBrains Mono.
A poem in verse form. Lines 4, 7, and 11 are highlighted in burgundy tint (changed/removed).
A thin red-sienna left border on changed lines.

Panel B (right, labeled "CURRENT — June 2025"):
Same layout. Lines 4, 7, and 11 are highlighted in forest-green tint (added/changed).
A thin green left border on changed lines.

Center divider: a thin vertical botanical rule — a vine with leaves.
A small number at the center of each changed line pair: "3 changes"

Header spanning both panels: "COMPARING VERSIONS" in gold serif with ornamental underline.
Poem title: "Harmonikum" below header.

At the bottom: "← Use Draft" and "Use Current →" buttons in gold border style.
And: "3 lines changed · 4 added · 2 removed" in small muted text.

The aesthetic: two illuminated manuscript pages being held side by side for comparison.
{AESTHETIC}
Wide landscape showing both panels and the diff clearly.
"""
    },

    # ─── THEME 6: THE THRESHOLD PORTAL (Login + Project Select) ───────────

    {
        "name": "18_threshold_login",
        "theme": "threshold",
        "title": "The Threshold — Login Portal",
        "prompt": f"""
UI mockup of a login/entry screen for a local poetry collection application.
The aesthetic of a threshold or portal — an arched gate opening into a garden.
Very dark near-black warm background.

Central element: A tall arch shape (not a literal graphic but a UI panel styled
to suggest an arch) with:
- Double-rule gold border forming an arch shape (or a rounded rectangle with thick gold frame)
- Botanical vines climbing the sides of the arch
- A pixel-art keyhole or gate ornament at the top center

Inside the arch:
- Application name: "TEXGRAPH STUDIO" in large Cormorant Garamond display serif, gold
  (not "TEXGRAPH STUDIO" as a brand — as a literary title, like a book title page)
- Subtitle in italic serif: "A poetry collection instrument"
- Small ornamental rule

Below title: Two options styled as doorways to pass through:
1. "Open Local Workspace" — large-ish button, gold border, cream text
2. "Sign In" — smaller, muted dashed border

Under those: a small monospace path: "workspace: ~/Desktop/Texgraph" (current workspace)

The whole screen background: William Morris acanthus motif at very low opacity (#2a1a0a tinted).
A pixel-art moth in the upper corner, barely visible.

This should feel like: standing at a gate to a secret garden at dusk.
Not a SaaS login page.
{AESTHETIC}
Centered portrait composition, very dark, gold and cream only.
"""
    },

    {
        "name": "19_threshold_project_select",
        "theme": "threshold",
        "title": "The Threshold — Project Selection (Codex Shelf)",
        "prompt": f"""
UI mockup of a project selection screen for a poetry collection application.
The aesthetic: a dark library shelf, books/codices as the project cards.

Header: "SELECT A COLLECTION" in gold Cormorant Garamond, ornamental rule below.
Workspace path displayed small and muted beneath.

Project cards displayed as book spines or illuminated codex covers:
3 cards in a row, each approximately 200x280px:

Card 1 (active project): "LIFT WIND / LOVE HEAT"
- Deep burgundy background
- Gold foil-stamped title text (Cormorant Garamond, centered vertically like a spine)
- Subtitle in small italic: author name
- Bottom metadata: "14 sections · 74 poems"
- A thin botanical border around the card
- A small ribbon bookmark in antique gold at the top

Card 2 (another project): Different color cover (dark lapis/indigo)
Similar layout. "A SECOND COLLECTION" placeholder title.

Card 3: "NEW COLLECTION +" — dark olive background, a dashed gold border, plus icon.
The "new project" card looks like a blank codex waiting to be filled.

All cards have slight physical depth — think of actual books on a shelf.
Below the cards: "New Collection" text link.

The background: darkest near-black with very faint wood grain texture.
{AESTHETIC}
Centered landscape, showing the shelf/cards clearly. Literary and warm.
"""
    },

    # ─── THEME 7: TYPOGRAPHY & COLOR SPECIMENS ────────────────────────────

    {
        "name": "20_typeset_specimen",
        "theme": "specimens",
        "title": "Typography Specimen — Literary Dark Theme",
        "prompt": f"""
Typography specimen sheet for a dark-mode literary poetry application.
Dark warm background (#0d0a07). Shows the complete type system.

Top section — DISPLAY TYPE:
"LIFT WIND / LOVE HEAT" in Cormorant Garamond at 48px, antique gold (#8b6914)
Below: "I. Vibrations of the Dented Spheres" in Cormorant Garamond 28px italic, cream

Second section — UI TYPE:
"CARDS    GRAPH    BUILD" in Inter light, tracked wide, small caps
"§ 03_vibrations-dented-spheres" section label in small serif, gold
Field labels: "TITLE  TYPE  ORDER  LINES" in small-caps, wide tracking, muted gold

Third section — EDITOR TYPE:
Lines of JetBrains Mono showing poem frontmatter (YAML) and verse body:
  title: "Harmonikum"
  type: poem
  order: 1

  Open the valves of the ear
  and let the sound pour through—
(in warm cream, generous leading)

Fourth section — ORNAMENTAL TYPE:
"CODEX VARIANTS" in larger serif with double ornamental underline
"★ CANONICAL" in Press Start 2P pixel font
"v3 · 38L" as a small version indicator badge

Fifth section — COLOR SWATCHES:
A row of colored rectangles: canvas, surface, panel, card, gold, burgundy, forest, violet
Each labeled with hex code in small monospace beneath.

The whole specimen should feel like a typographer's proof sheet.
{AESTHETIC}
Tall portrait, showing all type styles clearly with generous spacing.
"""
    },

    {
        "name": "21_color_palette_illustration",
        "theme": "specimens",
        "title": "Color Palette — PRB Jewel Tones Illustration",
        "prompt": f"""
A rich atmospheric illustration showing the Texgraph Studio color palette in context.
This is NOT a UI wireframe — it's a mood/color reference illustration in Pre-Raphaelite style.

A dark literary scene: a wooden writing desk in a candlelit study at night.
On the desk: an open manuscript, an ink bottle, a quill, scattered loose pages.

The scene uses ONLY the Texgraph palette:
- Deep background: #0d0a07 (warm near-black)
- Wood desk surface: #2e2318 (worn leather tone)
- Candlelight: #8b6914 (antique gold) as the warm glow source
- Shadow areas: #1a1410
- Manuscript pages: #e8dcc8 (aged cream)
- Ink spill: #1a1208 (near-black ink)
- A pressed botanical specimen on the desk in #3d5a47 (forest green)
- Wax seal on a letter in #7a1a2e (deep burgundy)
- Violet shadow cast by the candle: #6b4fa0

The style blends Pre-Raphaelite jewel-saturated naturalism with slight pixel-art texture
(you can see the pixels/grain). Everything is flat and rich, no photorealistic lighting.
This is the mood of the application — intimate, literary, handcrafted.
{AESTHETIC}
Square or portrait, atmospheric illustration, all palette colors visible in context.
"""
    },

    {
        "name": "22_ornament_system",
        "theme": "specimens",
        "title": "Ornamental Border & Divider System",
        "prompt": f"""
Design reference sheet for decorative borders, dividers, and ornaments for a
Pre-Raphaelite dark literary UI. Antique gold and cream on near-black background.

Show the following ornamental elements clearly labeled:

TOP SECTION — Horizontal Rules / Dividers:
1. Simple double rule (thin-gap-thin)
2. Botanical vine rule: a thin horizontal vine with leaves, thorns, and small flowers
3. Diamond-centered rule: line ◇ line
4. Thorn and briar rule: sharp, angular, gothic
5. Laurel wreath rule: gentle curves with leaves

MIDDLE SECTION — Corner Ornaments:
6. Acanthus corner: flowing leaf scroll for panel corners
7. Thorn corner: angular, sharp, gothic corner piece
8. Knotwork corner: interlaced bands (Celtic influence)
9. Simple serif corner: clean double-line L-shape

BOTTOM SECTION — Inline / Icon Ornaments:
10. § Paragraph/section mark in ornamental form
11. ❧ Hedera leaf (typographic reference mark)
12. ◈ Diamond with center dot
13. Fleur-de-lis (simplified)
14. Small pixel-art quill (8x16 pixels shown at 4x scale)
15. Small pixel-art leaf (8x8 pixels shown at 4x scale)

All ornaments in antique gold (#8b6914) on dark background.
Labeled with suggested usage context in small muted text.
{AESTHETIC}
Reference sheet portrait, all ornaments clearly visible and labeled.
"""
    },

    {
        "name": "23_pixel_icon_set",
        "theme": "specimens",
        "title": "8-Bit Pixel Art Icon Set",
        "prompt": f"""
Pixel art icon reference sheet for a literary poetry application.
Dark warm background. All icons on an 8-pixel grid, shown at both 1x (16px) and 4x (64px).

Show these 16 icons in a 4×4 grid, each with name label below:
1. Quill: an ink quill pen, pointing diagonally
2. Codex: a book seen from slight angle, with decorative clasp
3. Leaf: a simple botanical leaf with veins
4. Star: a 5-pointed star (for canonical marker), pixelated
5. Rune stone: a rounded stone with an angular rune mark on it
6. Key: an ornate old key
7. Eye: a stylized eye, slightly hooded/lidded, mystical
8. Spiral: a tightly wound spiral/vortex (for build/compile)
9. Moth: a moth facing forward, wings spread
10. Alembic: chemistry flask / alembic dripping
11. Scroll: a rolled scroll with text lines
12. Rose: a stylized rose head, simplified
13. Moon: a crescent moon (for dark mode, settings)
14. Crossquill: two quills crossing like a swords-crossed emblem
15. Orb: a glowing crystal ball/orb (for oracle/agent)
16. Acanthus: a simplified 3-petal acanthus leaf head

All icons: antique gold (#8b6914) with shadow accent in dark burgundy.
Show both 16px and 64px versions for each.
Grid labeled with icon names in small pixel font.
{AESTHETIC}
Square composition, all 16 icons clearly visible.
"""
    },

    # ─── THEME 8: FULL-SCREEN + SPECIAL MODES ─────────────────────────────

    {
        "name": "24_distraction_free_editor",
        "theme": "writing",
        "title": "Distraction-Free Full-Screen Writing Mode",
        "prompt": f"""
UI mockup of a full-screen distraction-free poetry writing mode.
Almost no chrome. The whole screen is the poem.

Background: #0d0a07 warm near-black. Very subtle acanthus leaf texture at 1% opacity.
A generous centered column of text, about 60-70 characters wide, vertically centered.

The poem "Harmonikum" is being written:
- Title in Cormorant Garamond 24px, antique gold, centered
- A thin gold rule 40px below title
- Verse body in JetBrains Mono 14px, 1.8 line-height, warm cream (#e8dcc8)
- Stanzas clearly separated by 2 blank lines
- Cursor: a thick pixel-art block cursor in gold, blinking in the middle of a line

At the absolute top: a tiny status bar (20px tall, barely visible):
"Harmonikum · §03 · 38L · ✓ Saved" in tiny monospace, muted gold. Almost invisible.

At the very bottom: "ESC to return" in ghost-gray, tiny, centered.

Absolutely nothing else. No sidebars. No borders. No decorations.
Just the poem and the warm darkness.

This should feel like writing by candlelight in an otherwise dark room.
The poem is the only light source.
{AESTHETIC}
Landscape, showing the full screen writing experience. Very minimal. Very atmospheric.
"""
    },

    {
        "name": "25_collection_map",
        "theme": "writing",
        "title": "Collection Overview Map",
        "prompt": f"""
UI mockup of a bird's-eye collection overview map for a poetry collection application.
Titled "COLLECTION MAP" in Cormorant Garamond gold. Dark background.

The map shows the entire "Lift Wind / Love Heat" collection structure:
14 sections displayed as horizontal bands, stacked vertically.
Each band shows:
- Section name in small gold italic serif (left)
- A row of tiny poem dots (6-8px squares) representing each poem in the section
  Color-coded by type: cream=poem, amber=prose, violet=cycle, rose=screenplay
- Band width proportional to line count (longer sections = wider dots area)
- A small bar chart on the right showing relative line count
- Section order number in muted text on far left

The section with most poems is visibly denser.
Some sections show a poem-cycle bracket.

The whole thing looks like a sheet music score or a tapestry pattern —
horizontal bands of information, left to right.

Beneath: summary stats: "74 poems · 14 sections · ~2,840 lines"

A thin botanical rule separates every other section for readability.
{AESTHETIC}
Tall portrait showing all 14 sections. Like a manuscript index or musical score.
"""
    },

    {
        "name": "26_empty_state_garden",
        "theme": "writing",
        "title": "Empty State — The Untended Garden",
        "prompt": f"""
UI mockup of an empty state illustration for a poetry collection application.
Shown when a new project has no sections or poems yet.

The illustration occupies the center of the screen on a dark warm background.
It shows: an empty walled garden seen from a low angle.
The garden has stone pathways and raised beds, but they are bare — no flowers yet.
An old wooden gate stands open, waiting.
In the garden center: a blank scroll or empty lectern, waiting to be written on.

Above the illustration, in Cormorant Garamond italic gold:
"The garden awaits its first poem."

Below: Two action buttons:
"+ Create Section" — gold border, leaf icon
"+ Import Poems" — muted dashed border, scroll icon

The illustration style: Pre-Raphaelite flat, jewel-toned, botanical.
A few acanthus leaves grow along the garden walls.
The empty beds feel full of potential, not sad.
8-bit moth in the upper corner.
{AESTHETIC}
Centered portrait, illustration filling upper half, text and buttons in lower half.
Literary and inviting, not lonely.
"""
    },

    {
        "name": "27_notes_editor",
        "theme": "writing",
        "title": "NOTES.md Editor — The Editorial Journal",
        "prompt": f"""
UI mockup of a NOTES.md editor panel for a poetry collection application.
This is the editorial journal — notes about the collection, motifs, intentions.
Also consumed by the AI agent as memory.

The panel occupies the right side of the screen, wider than the properties panel (~400px).
Dark mahogany background, double-rule gold border on the left edge.

Header: "EDITORIAL NOTES" in gold Cormorant Garamond with a botanical horizontal rule.
Small text beneath: "This file is read by the Oracle as memory."

The editor: a Markdown editor showing notes content:
- A heading: "## Motifs & Cross-references"
- Several bullet points about poem themes
- A cross-reference entry: "see: Harmonikum ↔ The Weight of Keys (§09)"
- Italic note: "_The third section cycles back to the opening image of wind_"

The editor has a warmer tone than the main PoemEditor — slightly parchment-tinted
background (#1a1612 instead of pure dark), suggesting a personal notebook.

At the bottom of the panel: a small "Saved to NOTES.md" timestamp in muted gold.
A pixel-art moth at the top right corner.

This panel should feel like a private journal or commonplace book.
{AESTHETIC}
Tall portrait showing the full notes panel.
"""
    },

]

# ── Generation function ───────────────────────────────────────────────────────

def generate_image(prompt_data: dict, delay: float = 2.0) -> bool:
    name = prompt_data["name"]
    theme = prompt_data["theme"]
    title = prompt_data["title"]
    prompt = prompt_data["prompt"].strip()

    out_path = OUT_DIR / f"{name}.png"
    if out_path.exists():
        print(f"  SKIP (exists): {name}")
        return True

    print(f"  GEN: {title}")

    payload = json.dumps({
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1792x1024",
        "quality": "standard",
        "response_format": "url",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read())
            image_url = data["data"][0]["url"]

        # Download the image
        with urllib.request.urlopen(image_url, timeout=60) as img_resp:
            out_path.write_bytes(img_resp.read())

        print(f"    ✓ saved → {out_path.name}")
        time.sleep(delay)
        return True

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"    ✗ HTTP {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False


def main():
    if not API_KEY:
        print("ERROR: OPENAI_API_KEY not found")
        return

    # Group by theme
    by_theme: dict[str, list[dict]] = {}
    for p in PROMPTS:
        by_theme.setdefault(p["theme"], []).append(p)

    print(f"\nTexgraph Studio Wireframe Generator")
    print(f"Output: {OUT_DIR}")
    print(f"Total prompts: {len(PROMPTS)}")
    print(f"Themes: {list(by_theme.keys())}\n")

    success = 0
    fail = 0

    for theme, prompts in by_theme.items():
        print(f"\n-- Theme: {theme.upper()} ({len(prompts)} images) --------------")
        for p in prompts:
            ok = generate_image(p, delay=3.0)
            if ok:
                success += 1
            else:
                fail += 1

    print(f"\n-- Complete: {success} generated, {fail} failed --")

    # Write an index
    write_index(by_theme)


def write_index(by_theme: dict):
    index_path = OUT_DIR / "INDEX.md"
    lines = ["# Texgraph Studio — Wireframe Index\n",
             "Generated wireframes organized by theme.\n"]

    theme_names = {
        "scriptorium": "The Scriptorium (Card Editor)",
        "garden": "The Garden Labyrinth (Graph Assembly)",
        "forge": "The Alchemist's Forge (Build View)",
        "oracle": "The Oracle's Grotto (Agent Panel)",
        "archive": "The Archive of Codices (Versions)",
        "threshold": "The Threshold Portal (Login + Select)",
        "specimens": "Specimens (Typography, Color, Ornaments, Icons)",
        "writing": "Writing Modes (Distraction-Free, Map, Notes)",
    }

    for theme, prompts in by_theme.items():
        label = theme_names.get(theme, theme.title())
        lines.append(f"\n## {label}\n")
        for p in prompts:
            fname = f"{p['name']}.png"
            exists = (OUT_DIR / fname).exists()
            status = "✓" if exists else "○"
            lines.append(f"- {status} [{p['title']}]({fname})\n")

    index_path.write_text("".join(lines), encoding="utf-8")
    print(f"Index written: {index_path}")


if __name__ == "__main__":
    main()
