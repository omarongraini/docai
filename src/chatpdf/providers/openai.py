from collections.abc import Iterator

from openai import OpenAI

from chatpdf.config import settings
from chatpdf.interfaces import EmbedderInterface
from chatpdf.interfaces import LLMInterface

_client = OpenAI(base_url=settings.openai_base_url, api_key=settings.openai_api_key)


class OpenAILLM(LLMInterface):
    def __init__(self) -> None:
        self._model = settings.openai_chat_model

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        resp = _client.chat.completions.create(
            model=self._model, messages=self._messages(prompt, system)
        )
        return resp.choices[0].message.content or ""

    def stream(self, prompt: str, *, system: str | None = None) -> Iterator[str]:
        stream = _client.chat.completions.create(
            model=self._model, messages=self._messages(prompt, system), stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    @staticmethod
    def _messages(prompt: str, system: str | None) -> list[dict]:
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        return msgs


class OpenAIEmbedder(EmbedderInterface):
    def __init__(self, dim: int) -> None:
        self._model = settings.openai_embed_model
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = _client.embeddings.create(model=self._model, input=texts, dimensions=settings.embedding_dim)
        return [item.embedding for item in resp.data]