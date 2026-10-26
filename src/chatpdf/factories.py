from functools import lru_cache

from openai import OpenAI

from chatpdf.config import settings
from chatpdf.db import SessionLocal
from chatpdf.interfaces import EmbedderInterface
from chatpdf.interfaces import LLMInterface
from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.providers.registry import EMBEDDER_PROVIDERS, LLM_PROVIDERS
from chatpdf.stores import DocumentStore
from chatpdf.stores.registry import VECTOR_STORE_PROVIDERS


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


@lru_cache(maxsize=1)
def get_llm() -> LLMInterface:
    name = settings.llm_provider
    if name not in LLM_PROVIDERS:
        raise ValueError(f"unknown llm_provider: {name!r}, valid: {list(LLM_PROVIDERS)}")
    return LLM_PROVIDERS[name]()


@lru_cache(maxsize=1)
def get_embedder() -> EmbedderInterface:
    name = settings.embedder_provider
    if name not in EMBEDDER_PROVIDERS:
        raise ValueError(f"unknown embedder_provider: {name!r}, valid: {list(EMBEDDER_PROVIDERS)}")
    return EMBEDDER_PROVIDERS[name]()


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    name = settings.vector_store_provider
    if name not in VECTOR_STORE_PROVIDERS:
        raise ValueError(f"unknown vector_store_provider: {name!r}, valid: {list(VECTOR_STORE_PROVIDERS)}")
    return VECTOR_STORE_PROVIDERS[name]()


@lru_cache(maxsize=1)
def get_document_store() -> DocumentStore:
    return DocumentStore(SessionLocal)