import pytest
from pydantic import ValidationError

from backend.core.models import PoemFrontMatter, first_heading, parse_front_matter

_VALID_POEM = """\
---
title: "January: The Coming of the Snow"
book: "The Book of Nature, 1910-1912"
book_order: 1
poem_order: 1
book_part: "Part I: The Months in Italy"
series: null
series_part: null
source_pdf: "raw/early_1913/the_book_of_nature_1910_1912.pdf"
source_pages_scan: [17]
source_pages_printed: [3]
status: "transcribed"
notes: []
---

# January: The Coming of the Snow

The long thin swaying curtains of the rain
Are tangled in the bare boughs of the plain.
"""


def test_parse_front_matter_basic():
    result = parse_front_matter(_VALID_POEM)
    assert result["title"] == "January: The Coming of the Snow"
    assert result["source_pages_scan"] == [17]
    assert result["series"] is None
    assert result["notes"] == []


def test_parse_front_matter_no_yaml():
    assert parse_front_matter("# Just a heading\n\nNo front matter.") == {}


def test_parse_front_matter_unclosed():
    assert parse_front_matter("---\ntitle: foo\n# no closing fence") == {}


def test_first_heading_found():
    assert first_heading("# My Title\n\nBody.") == "My Title"


def test_first_heading_none():
    assert first_heading("No headings here.") is None


def test_poem_validation_success():
    raw = parse_front_matter(_VALID_POEM)
    poem = PoemFrontMatter.model_validate(raw)
    assert poem.title == "January: The Coming of the Snow"
    assert poem.status == "transcribed"
    assert poem.source_pages_scan == [17]
    assert poem.book_order == 1


def test_poem_validation_invalid_status():
    raw = parse_front_matter(_VALID_POEM)
    raw["status"] = "draft"
    with pytest.raises(ValidationError):
        PoemFrontMatter.model_validate(raw)


def test_poem_validation_missing_required():
    raw = parse_front_matter(_VALID_POEM)
    del raw["title"]
    with pytest.raises(ValidationError):
        PoemFrontMatter.model_validate(raw)


def test_poem_multipage_scan():
    raw = parse_front_matter(_VALID_POEM)
    raw["source_pages_scan"] = [17, 18]
    poem = PoemFrontMatter.model_validate(raw)
    assert poem.source_pages_scan == [17, 18]
