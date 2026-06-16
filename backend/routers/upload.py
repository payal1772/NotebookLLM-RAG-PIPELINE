import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from pipeline.loader import load_document
from pipeline.chunker import chunk_text
from pipeline.embedder import get_embeddings
from pipeline.vector_store import store_chunks, get_all_documents

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document → load → chunk → embed → store in pgvector.
    """
    ext = Path(file.filename).suffix.lower()
    allowed = {".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp"}

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed)}"
        )

    # Save file to disk temporarily
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Step 1 — Load document text
        print(f"📄 Loading: {file.filename}")
        text = load_document(str(save_path))

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract any text from the document."
            )

        # Step 2 — Chunk the text
        print(f"✂️  Chunking: {file.filename}")
        chunks = chunk_text(text)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Document was too short to chunk."
            )

        # Step 3 — Generate embeddings
        print(f"🔢 Embedding: {file.filename}")
        embeddings = get_embeddings(chunks)

        # Step 4 — Store in pgvector
        print(f"💾 Storing: {file.filename}")
        store_chunks(
            doc_name=file.filename,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_stored": len(chunks),
            "message": f"'{file.filename}' processed and stored successfully."
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    finally:
        # Clean up temp file
        if save_path.exists():
            os.remove(save_path)



@router.get("/documents")
def list_documents():
    """Return all document names stored in the vector DB."""
    docs = get_all_documents()
    return {
        "total": len(docs),
        "documents": docs
    }

from pipeline.vector_store import delete_document

@router.delete("/documents/{doc_name}")
def remove_document(doc_name: str):
    try:
        delete_document(doc_name)
        return {"status": "success", "message": f"'{doc_name}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
