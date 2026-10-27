from chatpdf.interfaces import EmbedderInterface
from chatpdf.interfaces import LLMInterface
from chatpdf.providers.gemini import GeminiLLM
from chatpdf.providers.openai import OpenAIEmbedder, OpenAILLM

LLM_PROVIDERS: dict[str, type[LLMInterface]] = {
    "openai": OpenAILLM,
    "gemini": GeminiLLM,
}

EMBEDDER_PROVIDERS: dict[str, type[EmbedderInterface]] = {
    "openai": OpenAIEmbedder,
}