# tests/test_prompt.py
from chatpdf.models import Chunk
from chatpdf.rag.chat import _build_prompt


def _chunk(content="x", doc="d1", page=1):
    return Chunk(content=content, document_id=doc, page=page, chunk_index=0)


def test_empty_chunks_says_no_context():
    prompt = _build_prompt("q?", [], "en", {})
    assert "none found" in prompt
    assert "q?" in prompt


def test_citation_format_english():
    prompt = _build_prompt("q?", [_chunk(doc="acme.pdf", page=3)], "en", {})
    assert "acme.pdf" in prompt
    assert "page 3" in prompt


def test_arabic_headers():
    prompt = _build_prompt("س؟", [_chunk(page=2)], "ar", {})
    assert "السياق" in prompt
    assert "السؤال" in prompt
