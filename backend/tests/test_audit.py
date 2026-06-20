from backend.core.audit import FORBIDDEN, forbidden_tokens


def test_clean_poem():
    text = "The long thin swaying curtains of the rain\nAre tangled in the bare boughs of the plain."
    assert forbidden_tokens(text) == []


def test_code_fence():
    assert "```" in forbidden_tokens("some text\n```python\ncode\n```")


def test_nbsp():
    assert "&nbsp;" in forbidden_tokens("text with&nbsp;a space")


def test_br_tag():
    assert "<br" in forbidden_tokens("line one<br>line two")
    assert "<br" in forbidden_tokens("line one<br/>line two")


def test_page_break_lower():
    assert "page-break" in forbidden_tokens("<!-- page-break -->")


def test_page_break_upper():
    assert "PAGE BREAK" in forbidden_tokens("--- PAGE BREAK ---")


def test_multiple_hits():
    text = "```code``` and &nbsp; with <br> breaks"
    found = forbidden_tokens(text)
    assert "```" in found
    assert "&nbsp;" in found
    assert "<br" in found


def test_forbidden_list_constant():
    assert "```" in FORBIDDEN
    assert "&nbsp;" in FORBIDDEN
    assert "<br" in FORBIDDEN
