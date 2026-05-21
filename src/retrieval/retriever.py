"""
retriever.py — RegiMindAI

This is the retrieval layer of my RAG system. Its only job is:
given a question, find the most relevant chunks from the Cardiff
University policy corpus.

I implemented three methods during the research phase (BM25, dense,
and a hybrid of the two) so I could compare them. For the live demo
I'm using DENSE retrieval (Sentence-Transformers + FAISS), because it
matches questions by *meaning* rather than exact keywords — which suits
natural student questions like "what happens if I hand in late?" where
the wording won't exactly match the policy text.

The heavy work (building the index, embedding every chunk) happens ONCE
when the Retriever is created, so each search afterwards is fast. This
is the key difference from my Colab notebook, where everything re-ran
in cells — here it's a reusable object an API can hold in memory.
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# ---- field names in my chunks.json (confirmed against my actual data) ----
ID_KEY = "chunk_id"
TEXT_KEY = "text"
POLICY_KEY = "policy_name"
SECTION_KEY = "section_heading"

# Small, fast embedding model — runs fine on CPU for my 716 chunks.
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self, chunks_path: str | Path):
        # --- load my preprocessed corpus (the 716 chunks from Phase 1-3) ---
        with open(chunks_path, "r", encoding="utf-8") as f:
            self.chunks: list[dict] = json.load(f)

        # id -> chunk, so I can look a chunk back up by its id after searching
        self.chunk_lookup = {c[ID_KEY]: c for c in self.chunks}
        # parallel lists: position in these arrays == position in the FAISS index
        self.ids = [c[ID_KEY] for c in self.chunks]
        self.texts = [c[TEXT_KEY] for c in self.chunks]

        # --- build the dense index (this is the "embedding" step) ---
        # Each chunk of text becomes a vector that captures its meaning.
        self.embed_model = SentenceTransformer(EMBED_MODEL_NAME)
        embeddings = self.embed_model.encode(
            self.texts, convert_to_numpy=True, show_progress_bar=False
        ).astype("float32")

        # Normalising lets me use inner-product (IndexFlatIP) as cosine similarity,
        # which is the standard trick for sentence-transformer embeddings.
        faiss.normalize_L2(embeddings)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        """Find the top_k most relevant chunks for a question (dense retrieval).

        Returns a list of dicts with the chunk's id, text, policy and section,
        ready to be turned into context for the LLM and into the UI's
        'Sources' panel.
        """
        # Turn the question into a vector in the same space as the chunks...
        q = self.embed_model.encode([question], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(q)
        # ...and ask FAISS for the closest chunk vectors.
        _scores, idxs = self.index.search(q, top_k)
        ranked_ids = [self.ids[i] for i in idxs[0]]

        results = []
        for cid in ranked_ids:
            c = self.chunk_lookup[cid]
            results.append({
                "chunk_id": cid,
                "text": c.get(TEXT_KEY, ""),
                "policy_name": c.get(POLICY_KEY, "Unknown"),
                "section_heading": c.get(SECTION_KEY, ""),
            })
        return results


# Quick manual test:  python -m src.retrieval.retriever "late submission penalty"
if __name__ == "__main__":
    import sys

    chunks_file = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"
    r = Retriever(chunks_file)
    q = sys.argv[1] if len(sys.argv) > 1 else "what is the late submission penalty?"
    print(f"\nQuery: {q}\n")
    for i, hit in enumerate(r.search(q, top_k=5), 1):
        print(f"{i}. [{hit['policy_name']} — {hit['section_heading']}]")
        print(f"   {hit['text'][:160]}...\n")