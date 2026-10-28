from abc import ABC, abstractmethod
from collections.abc import Iterator


class LLMInterface(ABC):
    """Provider-agnostic chat completion interface."""

    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Blocking call, returns full text."""

    @abstractmethod
    def stream(self, prompt: str, *, system: str | None = None) -> Iterator[str]:
        """Streaming call, yields text deltas."""
