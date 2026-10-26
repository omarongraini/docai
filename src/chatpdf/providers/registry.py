from collections.abc import Callable

from chatpdf.config import settings
from chatpdf.interfaces import EmbedderInterface
from chatpdf.interfaces import LLMInterface
from chatpdf.providers.openai import OpenAIEmbedder, OpenAILLM

LLM_PROVIDERS: dict[str, Callable[[], LLMInterface]] = {
    "openai": OpenAILLM,
}

EMBEDDER_PROVIDERS: dict[str, Callable[[], EmbedderInterface]] = {
    "openai": lambda: OpenAIEmbedder(dim=settings.embedding_dim),
}

