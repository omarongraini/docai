from collections.abc import Iterator

from openai import OpenAI

from chatpdf.config import settings
from chatpdf.interfaces import EmbedderInterface, LLMInterface


class OpenAILLM(LLMInterface):
    def __init__(self, *, api_key: str, base_url: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        resp = self._client.chat.completions.create(
            model=self._model, messages=self._messages(prompt, system)
        )
        return resp.choices[0].message.content or ""

    def stream(self, prompt: str, *, system: str | None = None) -> Iterator[str]:
        stream = self._client.chat.completions.create(
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
    def __init__(self, *, api_key: str, base_url: str, model: str, dim: int) -> None:
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._dim = dim
        self.config = settings

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self._client.embeddings.create(
            model=self._model, input=texts, dimensions=self.config.embed_dim
        )
        return [item.embedding for item in resp.data]
