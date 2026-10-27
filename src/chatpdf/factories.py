from functools import lru_cache

from chatpdf.config import settings
from chatpdf.db import SessionLocal, assert_schema_matches_settings
from chatpdf.interfaces import EmbedderInterface, LLMInterface
from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.providers.registry import EMBEDDER_PROVIDERS, LLM_PROVIDERS
from chatpdf.stores.document_store import DocumentStore
from chatpdf.stores.registry import VECTOR_STORE_PROVIDERS


@lru_cache(maxsize=1)
def get_llm() -> LLMInterface:
    name = settings.llm_provider
    if name not in LLM_PROVIDERS:
        raise ValueError(
            f"unknown llm_provider: {name!r}, valid: {list(LLM_PROVIDERS)}"
        )
    cls = LLM_PROVIDERS[name]

    if name == "gemini":
        return cls(api_key=settings.llm_api_key, model=settings.llm_chat_model)

    return cls(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_chat_model,
    )


@lru_cache(maxsize=1)
def get_embedder() -> EmbedderInterface:
    assert_schema_matches_settings()
    name = settings.embed_provider
    if name not in EMBEDDER_PROVIDERS:
        raise ValueError(
            f"unknown embedder_provider: {name!r}, valid: {list(EMBEDDER_PROVIDERS)}"
        )
    cls = EMBEDDER_PROVIDERS[name]
    return cls(
        api_key=settings.embed_api_key,
        base_url=settings.embed_base_url,
        model=settings.embed_model,
        dim=settings.embed_dim,
    )


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    name = settings.vector_store_provider
    if name not in VECTOR_STORE_PROVIDERS:
        raise ValueError(
            f"unknown vector_store_provider: {name!r}, valid: {list(VECTOR_STORE_PROVIDERS)}"
        )
    return VECTOR_STORE_PROVIDERS[name](SessionLocal)


@lru_cache(maxsize=1)
def get_document_store() -> DocumentStore:
    return DocumentStore(SessionLocal)
