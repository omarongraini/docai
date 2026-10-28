# tests/test_split.py
from docai.rag.ingest import _split_text as _split


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
    # Use a realistic sentence with spaces
    text = "This is a long sentence that will be split into multiple chunks by the recursive splitter."
    chunks = _split(text, 30, 10)

    assert len(chunks) > 1
    # The second chunk should contain the overlap from the first chunk
    # (The exact characters depend on where the space was trimmed)
    assert "will be split" in chunks[1] or "sentence that" in chunks[1]


def test_no_infinite_loop_on_pathological():
    _split(" ", 10, 2)  # must terminate
    _split("\n" * 1000, 10, 2)
