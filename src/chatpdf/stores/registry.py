from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.stores.pgvector_store import PgVectorStore

VECTOR_STORE_PROVIDERS: dict[str, type[VectorStore]] = {
    "pgvector": PgVectorStore,
}