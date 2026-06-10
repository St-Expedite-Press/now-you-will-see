from pathlib import Path


def test_proof_build_contract_names_typeset_output_proof():
    import texgraph.cli as cli

    source = Path(cli.__file__).read_text(encoding="utf-8")

    assert ' / "output" / "proof"' in source
    assert "proof/output/" not in source
