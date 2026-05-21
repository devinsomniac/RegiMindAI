"""
main.py — RegiMindAI API

This is the web layer. It exposes my RAG pipeline over HTTP so the
frontend (or anyone) can ask a question and get a grounded answer back.

It's deliberately thin — all the real logic lives in generator.py.
This file just:
  - builds the RAGGenerator ONCE when the server starts (slow step done once)
  - accepts a question via POST /query
  - returns {answer, sources} as JSON

Run locally with:
    uvicorn src.api.main:app --reload
Then open http://localhost:8000/docs to test it in the browser.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag.generator import RAGGenerator


# Path to my corpus, relative to the project root.
CHUNKS_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"

# I hold the RAGGenerator here so it's created once and reused for every request.
rag: RAGGenerator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- runs ONCE at server startup ---
    # Building the dense index + loading the embedding model is the heavy part,
    # so I do it here rather than on every request.
    global rag
    print("Loading RegiMindAI pipeline (this takes a few seconds)...")
    rag = RAGGenerator(CHUNKS_PATH)
    print("Pipeline ready.")
    yield
    # (nothing to clean up on shutdown)


app = FastAPI(title="RegiMindAI API", lifespan=lifespan)

# CORS: lets my frontend (running on a different address) call this API.
# "*" allows any origin — fine for a demo. For production I'd restrict this
# to just my deployed frontend's URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- request/response shapes (pydantic validates these automatically) ---
class QueryRequest(BaseModel):
    question: str


class Source(BaseModel):
    policy_name: str
    section_heading: str
    text: str
    chunk_id: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


# --- endpoints ---

@app.get("/health")
def health():
    """Simple check so deployment platforms know the server is alive."""
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """Take a question, run it through the RAG pipeline, return answer + sources."""
    result = rag.query(req.question)
    return result