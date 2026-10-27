from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from chatpdf.models import Document
from chatpdf.orm import DocumentRow


class DocumentStore:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_by_hash(self, file_hash: str) -> Document | None:
        with self._session_factory() as session:
            row = session.scalars(
                select(DocumentRow).where(DocumentRow.file_hash == file_hash)
            ).first()
            if not row:
                return None
            return Document(
                id=row.id,
                filename=row.filename,
                uploaded_at=row.uploaded_at,
                file_hash=row.file_hash,
            )

    def create(self, document: Document) -> None:
        with self._session_factory() as session:
            session.add(
                DocumentRow(
                    id=document.id,
                    filename=document.filename,
                    uploaded_at=document.uploaded_at,
                    file_hash=document.file_hash,
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
                file_hash=r.file_hash,  # <--- Make sure this is here
            )
            for r in rows
        ]
