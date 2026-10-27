from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from chatpdf.models import Document
from chatpdf.orm import DocumentRow


class DocumentStore:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, document: Document) -> None:
        with self._session_factory() as session:
            session.add(
                DocumentRow(
                    id=document.id,
                    filename=document.filename,
                    uploaded_at=document.uploaded_at,
                )
            )
            session.commit()

    def exists(self, document_id: str) -> bool:
        with self._session_factory() as session:
            return session.get(DocumentRow, document_id) is not None

    def list(self) -> list[Document]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(DocumentRow).order_by(DocumentRow.uploaded_at.desc())
            ).all()
        return [
            Document(
                id=r.id,
                filename=r.filename,
                uploaded_at=r.uploaded_at,
            )
            for r in rows
        ]
