from abc import ABC, abstractmethod


class EmbedderInterface(ABC):
    """Provider-agnostic text embedding interface."""

    @property
    @abstractmethod
    def dim(self) -> int:
        """Vector dimension. Must match pgvector column size."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Batch embed. Returns one vector per input, same order."""
