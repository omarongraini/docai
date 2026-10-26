from collections.abc import Iterator

from openai import OpenAI

from chatpdf.config import settings
from chatpdf.interfaces import EmbedderInterface
from chatpdf.interfaces import LLMInterface


class OpenAILLM(LLMInterface):
    def __init__(self, client: OpenAI) -> None:
        self._client = client
        self._model = settings.openai_chat_model

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = self._messages(prompt, system)
        resp = self._client.chat.completions.create(model=self._model, messages=messages)
        return resp.choices[0].message.content or ""

    def stream(self, prompt: str, *, system: str | None = None) -> Iterator[str]:
        messages = self._messages(prompt, system)
        stream = self._client.chat.completions.create(
            model=self._model, messages=messages, stream=True
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
    def __init__(self, client: OpenAI, dim: int) -> None:
        self._client = client
        self._model = settings.openai_embed_model
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self._client.embeddings.create(model=self._model, input=texts)
        return [item.embedding for item in resp.data]
    