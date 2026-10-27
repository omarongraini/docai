from collections.abc import Iterator

from chatpdf.config import settings
from chatpdf.factories import get_embedder, get_llm, get_vector_store
from chatpdf.models import Chunk
from chatpdf.rag.prompts import get_prompts
from chatpdf.factories import get_document_store


def retrieve(
    query: str,
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> list[Chunk]:
    k = top_k or settings.top_k
    embedding = get_embedder().embed([query])[0]
    return get_vector_store().search(embedding, k, document_ids)


def answer(
    query: str,
    language: str = "en",
    top_k: int | None = None,
    document_ids: list[str] | None = None,
) -> str:
    prompts = get_prompts(language)
    return get_llm().complete(
        _build_prompt(query, retrieve(query, top_k, document_ids), language),
        system=prompts.SYSTEM,
    )



def stream_from_chunks(
    query: str,
    chunks: list[Chunk],
    language: str = "en",
) -> Iterator[str]:
    prompts = get_prompts(language)
    yield from get_llm().stream(
        _build_prompt(query, chunks, language), system=prompts.SYSTEM
    )
    

def _build_prompt(query: str, chunks: list[Chunk], language: str) -> str:
    p = get_prompts(language)
    if not chunks:
        return f"{p.QUESTION_HEADER} {query}\n\n{p.CONTEXT_HEADER} {p.NO_CONTEXT}"

    try:
        filenames = {d.id: d.filename for d in get_document_store().list()}
    except Exception:
        filenames = {}

    context = "\n\n".join(
        f"{p.CHUNK_LABEL.format(i=i + 1, doc=filenames.get(c.document_id, c.document_id), page=c.page)}\n{c.content}"
        for i, c in enumerate(chunks)
    )
    return f"{p.CONTEXT_HEADER}\n{context}\n\n{p.QUESTION_HEADER} {query}"