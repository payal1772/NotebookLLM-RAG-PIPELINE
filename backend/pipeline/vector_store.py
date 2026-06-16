import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, Session

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}"
    f"/{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DB_URL)
Base = declarative_base()

class DocumentChunk(Base):
    __tablename__ = "notebook_chunks"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    doc_name  = Column(String(255), nullable=False)
    chunk_idx = Column(Integer, nullable=False)
    content   = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # all-MiniLM-L6-v2 = 384 dims


def init_db():
    """Create extension and tables on startup."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(engine)
    print("✅ notebook DB initialized")


def store_chunks(doc_name: str, chunks: list[str], embeddings: list[list[float]]):
    """Store chunks + their embeddings into pgvector."""
    with Session(engine) as session:
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            record = DocumentChunk(
                doc_name=doc_name,
                chunk_idx=idx,
                content=chunk,
                embedding=embedding
            )
            session.add(record)
        session.commit()
    print(f"✅ Stored {len(chunks)} chunks for '{doc_name}'")


def similarity_search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """Find top_k most similar chunks using cosine similarity."""
    with Session(engine) as session:
        results = session.execute(
            text("""
                SELECT doc_name, content,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS score
                FROM notebook_chunks
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {
                "embedding": str(query_embedding),
                "top_k": top_k
            }
        ).fetchall()

    return [
        {"doc_name": row.doc_name, "content": row.content, "score": row.score}
        for row in results
    ]


def get_all_documents() -> list[str]:
    """Return list of unique document names stored."""
    with Session(engine) as session:
        results = session.execute(
            text("SELECT DISTINCT doc_name FROM notebook_chunks ORDER BY doc_name")
        ).fetchall()
    return [row.doc_name for row in results]

def delete_document(doc_name: str):
    with Session(engine) as session:
        session.execute(
            text("DELETE FROM notebook_chunks WHERE doc_name = :doc_name"),
            {"doc_name": doc_name}
        )
        session.commit()
    print(f"🗑️ Deleted all chunks for '{doc_name}'")