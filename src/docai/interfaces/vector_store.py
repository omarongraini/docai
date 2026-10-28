from abc import ABC, abstractmethod

from docai.models import Chunk


class VectorStore(ABC):
    """Provider-agnostic vector storage interface."""

    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Persist chunks + vectors. len(chunks) == len(embeddings), else ValueError."""

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[Chunk]:
        """Top-k most similar chunks, best first.
        If document_ids is None → search all documents.
        Else → restrict to chunks whose document_id is in the list.
        Empty list → [].
        """

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None:
        """Remove all chunks for a document. No-op if none exist."""
