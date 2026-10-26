from abc import ABC, abstractmethod
from chatpdf.models import Chunk


class VectorStore(ABC):
    """Provider-agnostic vector storage interface."""

    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Persist chunks + vectors. len(chunks) == len(embeddings), else ValueError."""

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int) -> list[Chunk]:
        """Top-k most similar chunks, best first, score populated. Empty store → []."""

    @abstractmethod
    def delete_by_document(self, document_id: str) -> None:
        """Remove all chunks for a document. No-op if none exist."""