from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, query
from pipeline.vector_store import init_db
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title="Notebook RAG API",
    description="Upload documents and ask questions powered by Gemini + pgvector",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(query.router, prefix="/api", tags=["Query"])

app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

@app.get("/")
async def home():
    return FileResponse("../frontend/index.html")