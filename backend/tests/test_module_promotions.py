import yaml


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _approved_transcription():
    return {
        "status": "approved",
        "policy_accepted": True,
        "all_statuses_at_least": "transcribed",
        "volumes": [
            {
                "id": "vol-1",
                "transcription_status": "transcribed",
                "uncertain_readings": [],
            }
        ],
    }


def _approved_interior():
    return {
        "status": "approved",
        "interior_pdf": "typeset/output/demo.pdf",
        "fonts_embedded": True,
        "user_approved_interior": True,
    }


def test_verify_interior_and_typeset_alias_use_transcription_gate(tmp_path):
    from backend.core.promotions import verify_stage

    project_root = tmp_path / "projects" / "demo"
    _write_yaml(project_root / "transcribe" / "PROMOTION.yaml", _approved_transcription())

    assert verify_stage(project_root, "interior") == (True, [])
    assert verify_stage(project_root, "typeset") == (True, [])


def test_verify_covers_uses_interior_not_release_gate(tmp_path):
    from backend.core.promotions import verify_stage

    project_root = tmp_path / "projects" / "demo"
    pdf = project_root / "typeset" / "output" / "demo.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4\n")
    _write_yaml(project_root / "typeset" / "PROMOTION.yaml", _approved_interior())

    assert verify_stage(project_root, "covers") == (True, [])
