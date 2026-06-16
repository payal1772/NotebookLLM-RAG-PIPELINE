import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))


def chunk_text(text: str) -> list[str]:
    # Strip null bytes before chunking
    text  = text.replace("\x00", "")
    words = text.split()
    chunks = []

    if not words:
        return chunks

    start = 0
    while start < len(words):
        end   = start + CHUNK_SIZE
        chunk = " ".join(words[start:end])
        chunks.append(chunk.strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP

    chunks = [c for c in chunks if c.strip()]

    print(f"✅ Created {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks