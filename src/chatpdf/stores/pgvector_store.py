from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from chatpdf.interfaces.vector_store import VectorStore
from chatpdf.models import Chunk
from chatpdf.orm import ChunkRow


class PgVectorStore(VectorStore):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if not chunks:
            return
        with self._session_factory() as session:
            session.add_all([
                ChunkRow(
                    document_id=c.document_id,
                    content=c.content,
                    page=c.page,
                    chunk_index=c.chunk_index,
                    embedding=e,
                )
                for c, e in zip(chunks, embeddings)
            ])
            session.commit()

    def search(
            self,
            query_embedding: list[float],
            top_k: int,
            document_ids: list[str] | None = None,
        ) -> list[Chunk]:
        if top_k <= 0:
            return []
        if document_ids is not None and not document_ids:
            return []

        distance = ChunkRow.embedding.cosine_distance(query_embedding).label("distance")
        stmt = select(ChunkRow, distance)
        if document_ids is not None:
            stmt = stmt.where(ChunkRow.document_id.in_(document_ids))
        stmt = stmt.order_by(distance).limit(top_k)

        with self._session_factory() as session:
            rows = session.execute(stmt).all()
        return [
            Chunk(
                content=r.ChunkRow.content,
                document_id=r.ChunkRow.document_id,
                page=r.ChunkRow.page,
                chunk_index=r.ChunkRow.chunk_index,
                score=1.0 - r.distance,
            )
            for r in rows
        ]
    def delete_by_document(self, document_id: str) -> None:
        with self._session_factory() as session:
            session.execute(delete(ChunkRow).where(ChunkRow.document_id == document_id))
            session.commit()