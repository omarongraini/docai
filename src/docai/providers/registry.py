from docai.interfaces import EmbedderInterface, LLMInterface
from docai.providers.gemini import GeminiLLM
from docai.providers.openai import OpenAIEmbedder, OpenAILLM

LLM_PROVIDERS: dict[str, type[LLMInterface]] = {
    "openai": OpenAILLM,
    "gemini": GeminiLLM,
}

EMBEDDER_PROVIDERS: dict[str, type[EmbedderInterface]] = {
    "openai": OpenAIEmbedder,
}
