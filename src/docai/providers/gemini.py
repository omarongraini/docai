from collections.abc import Iterator

from google import genai
from google.genai import types

from docai.interfaces import LLMInterface


class GeminiLLM(LLMInterface):
    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        print("generate content...")
        resp = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=self._config(system),
        )
        print("generate content...[done]")

        return resp.text or ""

    def stream(self, prompt: str, *, system: str | None = None) -> Iterator[str]:
        for chunk in self._client.models.generate_content_stream(
            model=self._model,
            contents=prompt,
            config=self._config(system),
        ):
            if chunk.text:
                yield chunk.text

    @staticmethod
    def _config(system: str | None) -> types.GenerateContentConfig | None:
        if system:
            return types.GenerateContentConfig(system_instruction=system)
        return None
