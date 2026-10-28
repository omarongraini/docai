from sqlalchemy import create_engine
from sqlalchemy import text as sql_text
from sqlalchemy.orm import sessionmaker

from docai.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def assert_schema_matches_settings() -> None:
    with engine.connect() as conn:
        actual = conn.execute(
            sql_text(
                "SELECT format_type(atttypid, atttypmod) "
                "FROM pg_attribute "
                "WHERE attrelid = 'chunks'::regclass AND attname = 'embedding'"
            )
        ).scalar()
    if not actual:
        return
    expected = f"vector({settings.embed_dim})"
    if actual != expected:
        raise RuntimeError(
            f"embedding dim mismatch: DB={actual}, settings={expected}. "
            f"Run alembic autogenerate+upgrade, then re-ingest."
        )
