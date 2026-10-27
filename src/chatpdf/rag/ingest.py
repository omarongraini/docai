import io
import uuid
from datetime import UTC, datetime

from pypdf import PdfReader

from chatpdf.config import settings
from chatpdf.factories import get_document_store, get_embedder, get_vector_store
from chatpdf.models import Chunk, Document

_SEPARATORS = ["\n\n", "\n", ". ", "؟ ", "! ", "، ", " ", ""]


def ingest_pdf(filename: str, data: bytes) -> Document:
    doc = Document(
        id=str(uuid.uuid4()),
        filename=filename,
        uploaded_at=datetime.now(UTC),
    )

    text_per_page = _extract_pages(data)
    chunks = _chunk_pages(doc.id, text_per_page)
    if not chunks:
        raise ValueError(f"no extractable text in {filename!r}")

    embeddings = get_embedder().embed([c.content for c in chunks])

    get_document_store().create(doc)
    get_vector_store().add(chunks, embeddings)
    return doc


def _extract_pages(data: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(data))
    return [page.extract_text() or "" for page in reader.pages]


def _chunk_pages(document_id: str, pages: list[str]) -> list[Chunk]:
    chunks: list[Chunk] = []
    idx = 0
    for page_num, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue
        for piece in _split(text, settings.chunk_size, settings.chunk_overlap):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append(
                Chunk(
                    content=piece,
                    document_id=document_id,
                    page=page_num,
                    chunk_index=idx,
                )
            )
            idx += 1
    return chunks


def _split(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0 or overlap >= size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")
    pieces = _recursive_split(text, _SEPARATORS, size)
    return _apply_overlap(pieces, overlap)


def _recursive_split(text: str, seps: list[str], size: int) -> list[str]:
    if len(text) <= size:
        return [text] if text.strip() else []

    sep = next((s for s in seps if s in text), "")
    parts = text.split(sep) if sep else list(text)

    chunks: list[str] = []
    current = ""

    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(part) > size:
            finer = seps[seps.index(sep) + 1 :] if sep in seps else []
            if finer:
                chunks.extend(_recursive_split(part, finer, size))
            else:
                # hard-cut: no finer separator available
                chunks.extend(part[i : i + size] for i in range(0, len(part), size))
        else:
            current = part

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    overlapped = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap:]
        overlapped.append(tail + chunks[i])
    return overlapped
