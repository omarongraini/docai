from sqlalchemy import delete, select

from chatpdf.config import settings
from chatpdf.db import SessionLocal
from chatpdf.factories import get_embedder, get_vector_store
from chatpdf.models import Chunk
from chatpdf.orm import ChunkRow, DocumentRow
from chatpdf.rag.ingest import _split_text


def reindex_all() -> None:
    """Rebuild all chunks in the DB using the current config (chunk size & embedder)."""
    print(
        f"🔄 Starting reindex: model={settings.embed_model}, size={settings.chunk_size}"
    )

    with SessionLocal() as session:
        documents = session.scalars(select(DocumentRow)).all()
        if not documents:
            print("❌ No documents found to reindex.")
            return

        for doc in documents:
            _process_document(session, doc)

    print("✅ Reindex complete!")


def _process_document(session, doc: DocumentRow) -> None:
    """Extract text, re-chunk, re-embed, and replace for a single document."""
    print(f"  Re-chunking: {doc.filename} ({doc.id[:8]}…)")

    # 1. Reconstruct original text page-by-page
    pages = _reconstruct_pages(session, doc.id)
    if not pages:
        print(f"  ⚠️ No chunks found for {doc.filename}, skipping.")
        return

    # 2. Re-chunk using the new settings
    new_chunks = _create_chunks(doc.id, pages)
    if not new_chunks:
        print(f"  ⚠️ Chunking produced 0 chunks for {doc.filename}, skipping.")
        return

    # 3. Embed new chunks
    print(f"  Embedding {len(new_chunks)} chunks...")
    embeddings = get_embedder().embed([c.content for c in new_chunks])

    # 4. Replace in DB (delete old, add new)
    session.execute(delete(ChunkRow).where(ChunkRow.document_id == doc.id))
    session.commit()

    get_vector_store().add(new_chunks, embeddings)
    print(f"  ✅ Replaced {len(new_chunks)} chunks.")


def _reconstruct_pages(session, document_id: str) -> dict[int, str]:
    """Fetch old chunks, sort them, and merge them back into page-level text."""
    rows = session.scalars(
        select(ChunkRow)
        .where(ChunkRow.document_id == document_id)
        .order_by(ChunkRow.page, ChunkRow.chunk_index)
    ).all()

    pages: dict[int, list[str]] = {}
    for r in rows:
        pages.setdefault(r.page, []).append(r.content)

    return {page: " ".join(texts) for page, texts in pages.items()}


def _create_chunks(document_id: str, pages: dict[int, str]) -> list[Chunk]:
    """Split page text into new chunks based on current settings."""
    chunks = []
    idx = 0
    for page_num in sorted(pages.keys()):
        text = pages[page_num].strip()
        if not text:
            continue

        for piece in _split_text(text, settings.chunk_size, settings.chunk_overlap):
            if piece.strip():
                chunks.append(
                    Chunk(
                        content=piece.strip(),
                        document_id=document_id,
                        page=page_num,
                        chunk_index=idx,
                    )
                )
                idx += 1
    return chunks


if __name__ == "__main__":
    reindex_all()
