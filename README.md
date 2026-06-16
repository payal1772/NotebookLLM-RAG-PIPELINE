# 📓 NotebookLLM RAG Pipeline

A local RAG (Retrieval-Augmented Generation) pipeline that lets you upload documents and ask questions across all of them — just like Google's NotebookLM.

## ✨ Features

- 📄 Upload multiple documents (PDF, DOCX, TXT, MD, PNG, JPG)
- 🧠 Ask questions across all uploaded documents at once
- 🔍 Semantic search using vector embeddings
- 📚 New documents automatically align with existing knowledge base
- 💬 Clean chat UI with source citations and relevance scores

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.12 |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Groq (llama-3.1-8b-instant) |
| Vector DB | pgvector (PostgreSQL via Docker) |
| Frontend | HTML + CSS + JS (single file) |

## 📁 Project Structure
notebook/

├── docker-compose.yml

├── backend/

│   ├── main.py

│   ├── requirements.txt

│   ├── .env               ← not committed (keep secret)

│   ├── pipeline/

│   │   ├── loader.py      ← loads all file types

│   │   ├── chunker.py     ← splits text into chunks

│   │   ├── embedder.py    ← generates embeddings

│   │   └── vector_store.py← pgvector operations

│   └── routers/

│       ├── upload.py      ← POST /api/upload

│       └── query.py       ← POST /api/query

└── frontend/

└── index.html         ← full UI in one file

## ⚙️ Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/payal1772/NotebookLLM-Clone.git
cd NotebookLLM-Clone
```

### 2. Start the database
```bash
docker compose up -d
```

### 3. Create your `.env` file
Create `backend/.env` with:
```env
GROQ_API_KEY=your_groq_api_key_here

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ragdb
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpassword

CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

Get your free Groq API key at [https://console.groq.com](https://console.groq.com)

### 4. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Start the backend
```bash
uvicorn main:app --reload --port 8000
```

### 6. Open the frontend
Open `frontend/index.html` directly in your browser.

## 🚀 Usage

1. **Upload documents** — drag & drop or click to upload in the sidebar
2. **Wait for processing** — documents are chunked, embedded, and stored
3. **Ask questions** — type in the chat and get answers with source citations
4. **Add more docs anytime** — new uploads merge with the existing knowledge base

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload and process a document |
| POST | `/api/query` | Ask a question |
| GET | `/api/documents` | List all indexed documents |
| GET | `/docs` | Interactive API docs (Swagger) |

## 📋 Supported File Types

`.pdf` `.docx` `.txt` `.md` `.png` `.jpg` `.jpeg` `.webp`
