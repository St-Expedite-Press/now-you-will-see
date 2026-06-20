import yaml


def _write_workspace(root, project_id="demo", path="projects/demo/typeset"):
    workspace = {
        "projects": [
            {
                "id": project_id,
                "path": path,
                "description": "Demo",
            }
        ],
        "default_project": project_id,
    }
    (root / "workspace.yaml").write_text(yaml.safe_dump(workspace, sort_keys=False), encoding="utf-8")


def test_module_migration_dry_run_reports_operations_without_writing(tmp_path):
    from backend.core.modules import plan_module_migration

    _write_workspace(tmp_path)
    project_root = tmp_path / "projects" / "demo"
    project_root.mkdir(parents=True)
    (project_root / "typeset").mkdir()

    plan = plan_module_migration("demo", start=tmp_path)

    assert plan.conflicts == ()
    assert any(step.action == "move" for step in plan.steps)
    assert (project_root / "interior").exists() is False


def test_module_migration_conflict_detected_before_writes(tmp_path):
    from backend.core.modules import plan_module_migration

    _write_workspace(tmp_path)
    project_root = tmp_path / "projects" / "demo"
    project_root.mkdir(parents=True)
    (project_root / "typeset").mkdir()
    (project_root / "interior").mkdir()

    plan = plan_module_migration("demo", start=tmp_path)

    assert plan.conflicts
    assert any("typeset" in conflict and "interior" in conflict for conflict in plan.conflicts)
