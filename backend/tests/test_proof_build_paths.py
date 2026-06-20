from pathlib import Path


def test_proof_build_contract_names_typeset_output_proof():
    """Proof output resolves to interior/output/proof (or output/proof-<variant>),
    never a nested proof/output/."""
    import backend.core.cli as cli

    source = Path(cli.__file__).read_text(encoding="utf-8")

    # Default (no variant) proof dir is output/proof; variants are output/proof-<name>.
    assert '"output" / (f"proof-{variant}" if variant else "proof")' in source
    assert "proof/output/" not in source
