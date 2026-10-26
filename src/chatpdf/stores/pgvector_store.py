import psycopg
from pgvector.psycopg import register_vector

from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.models import Chunk


class PgVectorStore(VectorStore):
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def _conn(self) -> psycopg.Connection:
        conn = psycopg.connect(self._dsn)
        register_vector(conn)
        return conn

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if not chunks:
            return
        with self._conn() as conn, conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO chunks (document_id, content, page, chunk_index, embedding) "
                "VALUES (%s, %s, %s, %s, %s)",
                [
                    (c.document_id, c.content, c.page, c.chunk_index, e)
                    for c, e in zip(chunks, embeddings)
                ],
            )

    def search(self, query_embedding: list[float], top_k: int) -> list[Chunk]:
        if top_k <= 0:
            return []
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT content, document_id, page, chunk_index, "
                "       1 - (embedding <=> %s) AS score "
                "FROM chunks ORDER BY embedding <=> %s LIMIT %s",
                (query_embedding, query_embedding, top_k),
            )
            return [
                Chunk(content=r[0], document_id=r[1], page=r[2], chunk_index=r[3], score=r[4])
                for r in cur.fetchall()
            ]

    def delete_by_document(self, document_id: str) -> None:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM chunks WHERE document_id = %s", (document_id,))