# tests/test_retrieve.py
from chatpdf.models import Chunk
from chatpdf.features.chat import service as chat


class FakeEmbedder:
    dim = 1536

    def embed(self, texts):
        return [[0.1] * 1536 for _ in texts]


class FakeStore:
    def __init__(self, chunks):
        self.chunks = chunks
        self.called_with = None

    def search(self, emb, top_k, document_ids=None):
        self.called_with = document_ids
        if document_ids is not None:
            return [c for c in self.chunks if c.document_id in document_ids]
        return self.chunks

    def add(self, *a): ...
    def delete_by_document(self, *a): ...


def test_retrieve_passes_filter(monkeypatch):
    # Add score=0.5 to the fake chunks
    store = FakeStore(
        [Chunk("x", "doc1", 1, 0, score=0.5), Chunk("y", "doc2", 1, 1, score=0.5)]
    )
    monkeypatch.setattr(chat, "get_embedder", lambda: FakeEmbedder())
    monkeypatch.setattr(chat, "get_vector_store", lambda: store)
    result = chat.retrieve("q?", document_ids=["doc1"])
    assert store.called_with == ["doc1"]
    assert len(result) == 1
