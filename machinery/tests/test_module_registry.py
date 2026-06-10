import importlib
import pytest


def _modules():
    return importlib.import_module("texgraph.modules")


def test_module_registry_canonical_order_and_legacy_paths():
    modules = _modules()

    assert tuple(modules.CANONICAL_MODULES) == (
        "workspace",
        "sources",
        "transcription",
        "manuscript",
        "interior",
        "covers",
        "publication",
        "release",
    )

    loaded_ids = [module.id for module in modules.load_modules()]
    assert loaded_ids[: len(modules.CANONICAL_MODULES)] == list(modules.CANONICAL_MODULES)

    assert modules.get_module("typeset").id == "interior"
    assert modules.get_module("final").id == "release"
    assert modules.get_module("front-end").id == "publication"


@pytest.mark.parametrize(
    ("legacy", "canonical"),
    [
        ("ingest", "sources"),
        ("transcribe", "transcription"),
        ("typeset", "interior"),
        ("front-end", "publication"),
        ("final", "release"),
    ],
)
def test_legacy_alias_resolution(legacy, canonical):
    modules = _modules()

    assert modules.resolve_module(legacy) == canonical
    assert modules.resolve_module(canonical) == canonical


def test_proof_is_legacy_support_not_pipeline_alias():
    modules = _modules()

    assert "proof" not in [module.id for module in modules.load_modules()]
    assert modules.is_legacy_support("proof")
    with pytest.raises(ValueError, match="legacy support"):
        modules.resolve_module("proof")
