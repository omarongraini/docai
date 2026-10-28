from docai.interfaces.vector_store import VectorStore
from docai.stores.pgvector_store import PgVectorStore

VECTOR_STORE_PROVIDERS: dict[str, type[VectorStore]] = {
    "pgvector": PgVectorStore,
}
