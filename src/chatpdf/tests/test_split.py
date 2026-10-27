# tests/test_split.py
from chatpdf.rag.ingest import _split_text as _split 

def test_empty():
    assert _split("", 100, 10) == []


def test_short_text_no_split():
    assert _split("short", 100, 10) == ["short"]


def test_respects_paragraph_boundary():
    text = "para one.\n\npara two."
    chunks = _split(text, 15, 0)
    assert all(len(c) <= 15 for c in chunks)
    assert chunks == ["para one.", "para two."]


def test_hard_cut_when_no_separator():
    text = "a" * 500
    chunks = _split(text, 100, 0)
    assert all(len(c) <= 100 for c in chunks)
    assert "".join(chunks) == text


def test_overlap():
    text = "abcdefghij" * 10
    chunks = _split(text, 30, 10)
    assert all(len(c) <= 40 for c in chunks)  # size + overlap
    # verify overlap exists
    assert chunks[0][-10:] == chunks[1][:10]


def test_no_infinite_loop_on_pathological():
    _split(" ", 10, 2)  # must terminate
    _split("\n" * 1000, 10, 2)
