from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of text chunks."""
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"✅ Generated {len(embeddings)} embeddings")
    return [e.tolist() for e in embeddings]


def get_query_embedding(query: str) -> list[float]:
    """Generate embedding for a user query."""
    embedding = model.encode([query])[0]
    return embedding.tolist()