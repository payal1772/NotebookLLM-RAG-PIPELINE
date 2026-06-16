import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from pipeline.embedder import get_query_embedding
from pipeline.vector_store import similarity_search

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
TOP_K  = int(os.getenv("TOP_K_RESULTS", 5))


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
async def query_documents(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Step 1 — Embed the query
        print(f"🔍 Query: {request.question}")
        query_embedding = get_query_embedding(request.question)

        # Step 2 — Retrieve relevant chunks
        results = similarity_search(query_embedding, top_k=TOP_K)

        if not results:
            return {
                "answer": "I don't have enough information in my knowledge base to answer that. Please upload relevant documents first.",
                "sources": []
            }

        # Step 3 — Build context from chunks
        context_parts = []
        for i, r in enumerate(results):
            context_parts.append(
                f"[Chunk {i+1} from '{r['doc_name']}' | relevance: {r['score']:.2f}]\n{r['content']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Step 4 — Build prompt
        prompt = f"""You are Notebook AI, a helpful assistant that answers questions strictly based on the provided document context.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

USER QUESTION:
{request.question}

INSTRUCTIONS:
- Answer based only on the context above.
- If the context does not contain enough information, say so clearly.
- Be concise, accurate, and helpful.
- Mention which document(s) the information came from.

ANSWER:"""

        # Step 5 — Call Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are Notebook AI, a helpful document assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        answer = response.choices[0].message.content.strip()

        # Step 6 — Return answer + sources
        return {
            "answer": answer,
            "sources": [
                {
                    "doc_name": r["doc_name"],
                    "content":  r["content"][:200] + "...",
                    "score":    round(r["score"], 4)
                }
                for r in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")