import pytest
from texgraph.pagemap import expand_pages


def test_single_page():
    assert expand_pages("5") == [5]


def test_range():
    assert expand_pages("7-10") == [7, 8, 9, 10]


def test_compound():
    assert expand_pages("7-10,14") == [7, 8, 9, 10, 14]


def test_multi_range():
    assert expand_pages("1-3,7-9,12") == [1, 2, 3, 7, 8, 9, 12]


def test_empty_string():
    assert expand_pages("") == []


def test_trailing_comma():
    assert expand_pages("5,") == [5]


def test_invalid_range_raises():
    with pytest.raises(SystemExit, match="Invalid page range"):
        expand_pages("10-5")
