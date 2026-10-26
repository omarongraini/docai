from collections.abc import Callable

from chatpdf.db import SessionLocal
from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.stores.pgvector_store import PgVectorStore

VECTOR_STORE_PROVIDERS: dict[str, Callable[[], VectorStore]] = {
    "pgvector": lambda: PgVectorStore(SessionLocal),
}

