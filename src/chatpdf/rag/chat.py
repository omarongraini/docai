from collections.abc import Iterator

from chatpdf.config import settings
from chatpdf.factories import (
    get_embedder,
    get_llm,
    get_vector_store,
)
from chatpdf.logger import logger
from chatpdf.models import Chunk
from chatpdf.rag.prompts import get_prompts


def retrieve(
    query: str,
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> list[Chunk]:
    k = top_k or settings.top_k
    logger.info(f"Retrieving for query: {query!r} (top_k={k}, docs={document_ids})")
    embedding = get_embedder().embed([query])[0]
    chunks = get_vector_store().search(embedding, k, document_ids)

    chunk_info = [
        (c.chunk_index, c.page, c.document_id[:8], round(c.score or 0.0, 3))
        for c in chunks
    ]
    logger.info(f"Retrieved {len(chunks)} chunks: {chunk_info}")

    return chunks


def answer(
    query: str,
    language: str = "en",
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> str:
    prompts = get_prompts(language)
    return get_llm().complete(
        _build_prompt(query, retrieve(query, top_k, document_ids), language, {}),
        system=prompts.SYSTEM,
    )


def stream_from_chunks(
    query: str,
    chunks: list[Chunk],
    language: str = "en",
    filenames: dict[str, str] | None = None,
) -> Iterator[str]:
    prompts = get_prompts(language)
    yield from get_llm().stream(
        _build_prompt(query, chunks, language, filenames or {}), system=prompts.SYSTEM
    )


def _build_prompt(
    query: str, chunks: list[Chunk], language: str, filenames: dict[str, str]
) -> str:
    p = get_prompts(language)
    if not chunks:
        return f"{p.QUESTION_HEADER} {query}\n\n{p.CONTEXT_HEADER} {p.NO_CONTEXT}"

    context = "\n\n".join(
        f"{p.CHUNK_LABEL.format(doc=filenames.get(c.document_id, c.document_id), page=c.page, i=c.chunk_index)}\n{c.content}"
        for c in chunks
    )
    return f"{p.CONTEXT_HEADER}\n{context}\n\n{p.QUESTION_HEADER} {query}"
