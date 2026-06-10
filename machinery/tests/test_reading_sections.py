"""Reading-edition three-section format: parser selection and migration moves."""

import textwrap

import yaml


THREE_SECTION = textwrap.dedent("""\
    ---
    title: 'July: The Month of the Sun'
    type: poem
    order: 8
    ---

    ## Original Lineation

    Now bees and brutes and men leave drink and
        food;
    Sunk in a mighty reverie the earth,

    ## Editorial Relineation

    Now bees and brutes and men leave drink and food;
    Sunk in a mighty reverie the earth,

    ## Context Notes

    Note: wraps resolved into full metrical lines.
""")

ORIGINAL_ONLY = textwrap.dedent("""\
    ---
    title: 'January'
    type: poem
    order: 1
    ---

    ## Original Lineation

    The long thin swaying curtains of the rain
    Are tangled in the bare boughs of the plain.
""")

INTERNAL_MOVEMENTS = textwrap.dedent("""\
    ---
    title: 'June: Hymn to the Sun'
    type: poem
    order: 6
    ---

    ## Original Lineation

    ## I

    Sun that created me,

    ## II

    Not as in grey northern regions,
""")

LEGACY_PLAIN = textwrap.dedent("""\
    ---
    title: 'Plain'
    type: poem
    order: 2
    ---

    A body with no section headings
    passes through unchanged.
""")


def _parse(tmp_path, text):
    from texgraph.parser import PoetryParser

    f = tmp_path / "poem.md"
    f.write_text(text, encoding="utf-8")
    return PoetryParser().parse_file(f)


def test_relineation_selected_over_original(tmp_path):
    poem = _parse(tmp_path, THREE_SECTION)
    lines = [line for stanza in poem.stanzas for line in stanza.lines]
    assert "Now bees and brutes and men leave drink and food;" in lines
    assert "    food;" not in lines


def test_context_notes_captured_not_typeset(tmp_path):
    poem = _parse(tmp_path, THREE_SECTION)
    assert "wraps resolved" in poem.meta.get("context_notes", "")
    body_lines = [line for stanza in poem.stanzas for line in stanza.lines]
    assert not any("Note:" in line for line in body_lines)


def test_original_used_when_no_relineation(tmp_path):
    poem = _parse(tmp_path, ORIGINAL_ONLY)
    lines = [line for stanza in poem.stanzas for line in stanza.lines]
    assert lines[0] == "The long thin swaying curtains of the rain"
    assert not any("Original Lineation" in line for line in lines)


def test_internal_movement_headings_stay_in_section(tmp_path):
    poem = _parse(tmp_path, INTERNAL_MOVEMENTS)
    lines = [line for stanza in poem.stanzas for line in stanza.lines]
    assert "Sun that created me," in lines
    assert "Not as in grey northern regions," in lines


def test_plain_body_passes_through(tmp_path):
    poem = _parse(tmp_path, LEGACY_PLAIN)
    lines = [line for stanza in poem.stanzas for line in stanza.lines]
    assert lines[0] == "A body with no section headings"
    assert "context_notes" not in poem.meta


def _write_workspace(root, project_id="demo", path="projects/demo/typeset"):
    workspace = {
        "projects": [{"id": project_id, "path": path, "description": "Demo"}],
        "default_project": project_id,
    }
    (root / "workspace.yaml").write_text(
        yaml.safe_dump(workspace, sort_keys=False), encoding="utf-8"
    )


def test_migration_moves_reading_edition_to_manuscript(tmp_path):
    from texgraph.modules import apply_module_migration, plan_module_migration

    _write_workspace(tmp_path)
    project_root = tmp_path / "projects" / "demo"
    content = project_root / "typeset" / "content" / "01_section"
    content.mkdir(parents=True)
    (content / "001_poem.md").write_text("---\ntitle: x\n---\n\nLine\n", encoding="utf-8")
    (project_root / "typeset" / "collection.yaml").write_text(
        "title: Demo\nauthor: A\ncontent_dir: content\n", encoding="utf-8"
    )

    plan = plan_module_migration("demo", start=tmp_path)
    assert plan.conflicts == ()
    moves = {(s.old_name, s.new_name) for s in plan.steps if s.action == "move"}
    assert ("interior/content", "manuscript/reading") in moves

    apply_module_migration(plan)

    moved = project_root / "manuscript" / "reading" / "01_section" / "001_poem.md"
    assert moved.exists()
    assert not (project_root / "interior" / "content").exists()
    collection = (project_root / "interior" / "collection.yaml").read_text(encoding="utf-8")
    assert "content_dir: ../manuscript/reading" in collection


def test_migration_moves_stale_proof_output_under_interior(tmp_path):
    from texgraph.modules import apply_module_migration, plan_module_migration

    _write_workspace(tmp_path)
    project_root = tmp_path / "projects" / "demo"
    (project_root / "typeset").mkdir(parents=True)
    stale = project_root / "proof" / "output" / "tex"
    stale.mkdir(parents=True)
    (stale / "old.tex").write_text("% stale", encoding="utf-8")
    (project_root / "proof" / "corrections").mkdir()

    plan = plan_module_migration("demo", start=tmp_path)
    assert plan.conflicts == ()
    apply_module_migration(plan)

    assert (project_root / "interior" / "output" / "legacy-proof" / "tex" / "old.tex").exists()
    assert (project_root / "manuscript" / "corrections").exists()
    assert not (project_root / "manuscript" / "output").exists()


def test_scaffold_tool_skips_existing_files(tmp_path):
    import importlib.util
    from pathlib import Path

    tool = Path(__file__).resolve().parents[1] / "tools" / "scaffold_typeset_poems.py"
    spec = importlib.util.spec_from_file_location("scaffold_typeset_poems", tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    project = tmp_path / "projects" / "demo"
    src = project / "transcription" / "volumes" / "01_early_works" / "books"
    poems = src / "01_the_book_of_nature_1910_1912" / "poems"
    poems.mkdir(parents=True)
    (poems / "001_test.md").write_text(
        "---\ntitle: Test\npoem_order: 1\n---\n\n# Test\n\nLine one\n", encoding="utf-8"
    )
    (project / "manuscript").mkdir()

    src_root, dest_root = mod.resolve_roots(project)
    assert dest_root == project / "manuscript" / "reading"

    out = dest_root / "01_the-book-of-nature" / "001_test.md"
    out.parent.mkdir(parents=True)
    out.write_text("HAND-CURATED — must survive", encoding="utf-8")

    # Re-running the scaffold logic must not touch the existing file.
    text = (poems / "001_test.md").read_text(encoding="utf-8-sig")
    fm, body = mod.parse_frontmatter(text)
    assert out.read_text(encoding="utf-8") == "HAND-CURATED — must survive"
    scaffolded = f"---\n{mod.build_reading_fm(fm)}---\n\n## Original Lineation\n\n{mod.strip_heading(body)}"
    assert "## Original Lineation" in scaffolded
