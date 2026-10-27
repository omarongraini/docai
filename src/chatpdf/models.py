from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    id: str
    filename: str
    uploaded_at: datetime


@dataclass(frozen=True)
class Chunk:
    content: str
    document_id: str
    page: int
    chunk_index: int
    score: float | None = None
