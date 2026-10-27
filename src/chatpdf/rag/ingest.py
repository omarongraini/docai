import uuid
from datetime import UTC, datetime

import pymupdf

from chatpdf.config import settings
from chatpdf.factories import get_document_store, get_embedder, get_vector_store
from chatpdf.models import Chunk, Document

_SEPARATORS = ["\n\n", "\n", ". ", "؟ ", "! ", "، ", " ", ""]


def ingest_pdf(filename: str, data: bytes) -> Document:
    """Main pipeline: PDF bytes -> parsed pages -> chunks -> vectors -> DB."""
    doc = Document(
        id=str(uuid.uuid4()),
        filename=filename,
        uploaded_at=datetime.now(UTC),
    )

    pages = _extract_clean_pages(data)
    chunks = _chunk_document(doc.id, pages)

    if not chunks:
        raise ValueError(f"No extractable text in {filename!r}")

    # 1. Embed all chunks in one batch
    embeddings = get_embedder().embed([c.content for c in chunks])

    # 2. Save Document first (FK constraint), then Chunks
    get_document_store().create(doc)
    get_vector_store().add(chunks, embeddings)

    return doc


# ---------------------------------------------------------
# Extraction
# ---------------------------------------------------------


def _extract_clean_pages(data: bytes) -> list[str]:
    """Extract text using PyMuPDF, fixing line endings and hyphenation."""
    doc = pymupdf.open(stream=data, filetype="pdf")
    pages = []

    for page in doc:
        text = page.get_text("text") or ""
        # Clean up formatting
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("-\n", "")  # Fix hyphenated words across lines
        pages.append(text)

    doc.close()
    return pages


# ---------------------------------------------------------
# Chunking Pipeline
# ---------------------------------------------------------


def _chunk_document(document_id: str, pages: list[str]) -> list[Chunk]:
    """Iterate pages, split text, and attach metadata."""
    chunks = []
    chunk_index = 0

    for page_num, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue

        for piece in _split_text(text, settings.chunk_size, settings.chunk_overlap):
            if not piece.strip():
                continue

            chunks.append(
                Chunk(
                    content=piece.strip(),
                    document_id=document_id,
                    page=page_num,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1

    return chunks


def _split_text(text: str, size: int, overlap: int) -> list[str]:
    """Public wrapper for splitting logic with overlap applied."""
    if size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    raw_chunks = _recursive_split(text, _SEPARATORS, size)
    return _apply_overlap(raw_chunks, overlap)


# ---------------------------------------------------------
# Recursive Splitting Logic
# ---------------------------------------------------------


def _recursive_split(text: str, separators: list[str], limit: int) -> list[str]:
    """Recursively split text by the best available separator."""
    if len(text) <= limit:
        return [text] if text.strip() else []

    # Find the highest-priority separator present in the text
    sep = next((s for s in separators if s in text), "")

    # If no separators match, split at word boundary or hard cut
    if not sep:
        return _split_at_word_boundary(text, limit)

    return _split_by_separator(text, sep, separators, limit)


def _split_by_separator(
    text: str, sep: str, separators: list[str], limit: int
) -> list[str]:
    """Merge pieces separated by `sep` until they hit the size limit."""
    parts = text.split(sep)
    chunks = []
    current = ""

    for part in parts:
        candidate = (current + sep + part) if current else part

        if len(candidate) <= limit:
            current = candidate
            continue

        # Candidate exceeded limit, flush current and process the oversized part
        if current:
            chunks.append(current)
            current = ""

        if len(part) > limit:
            next_separators = (
                separators[separators.index(sep) + 1 :] if sep in separators else []
            )
            if next_separators:
                chunks.extend(_recursive_split(part, next_separators, limit))
            else:
                chunks.extend(_split_at_word_boundary(part, limit))
        else:
            current = part

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]


def _split_at_word_boundary(text: str, limit: int) -> list[str]:
    """Fallback: split a massive word/string without cutting mid-word."""
    if " " not in text:
        # No spaces at all (e.g., base64 or a massive URL), hard cut
        return [text[i : i + limit] for i in range(0, len(text), limit)]

    split_idx = text.rfind(" ", 0, limit)
    if split_idx == -1:
        split_idx = limit  # Force hard cut if the first word is longer than limit

    head = text[:split_idx].strip()
    tail = text[split_idx:].strip()

    chunks = [head] if head else []
    if tail:
        chunks.extend(_split_at_word_boundary(tail, limit))

    return chunks


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    """Prepend the tail of the previous chunk to the next chunk."""
    if overlap <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        overlapped.append(tail + chunks[i])
    return overlapped
