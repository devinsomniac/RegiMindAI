"""
generator.py — RegiMindAI

This is the RAG generation layer. It ties everything together to answer
a question end-to-end:

    question -> retrieve relevant chunks -> build a prompt -> ask the LLM
             -> return {answer, sources}

In my research notebook the retrieved chunks were pre-computed for a fixed
set of 145 evaluation questions. A live app is different: it gets brand-new
questions it has never seen, so here I retrieve fresh for every question
using the Retriever (set to dense retrieval).

I keep generation grounded: the prompt tells the model to answer ONLY from
the retrieved policy text, and I return the source chunks alongside the
answer so the user can see exactly where it came from. That traceability
is the whole point of the project — students need to be able to trust
and verify the answer.

LLM: Groq (Llama 3.1 8B) via LangChain — same model I used in the research
phase, and it has a free tier which keeps the demo free to run.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # loads GROQ_API_KEY from my .env file (never committed to git)

from langchain_groq import ChatGroq

from src.retrieval.retriever import Retriever


# My prompt template — the rules here are what keep answers grounded.
PROMPT_TEMPLATE = """
You are RegiMindAI, a helpful assistant that answers questions
about Cardiff University academic regulations and policies.

IMPORTANT RULES:
- Only answer based on the context provided below
- If the context does not contain enough information to answer, say
  "I cannot find this information in the provided policy documents."
- Include the policy name and section number when citing information
- Be concise and direct

CONTEXT:
{context}

QUESTION: {question}

ANSWER:
"""


def _build_context(chunks: list[dict]) -> str:
    """Turn the retrieved chunks into a single context string for the prompt.

    Each chunk is tagged with its policy and section so the model can cite
    its source, formatted the same way as in my research notebook.
    """
    parts = []
    for c in chunks:
        tag = f"[{c['policy_name']}-{c['section_heading']}]"
        parts.append(f"{tag}\n{c['text']}")
    return "\n\n--\n\n".join(parts)


class RAGGenerator:
    def __init__(self, chunks_path: str | Path):
        # The Retriever builds its dense index once here, at startup.
        self.retriever = Retriever(chunks_path)
        # Groq LLM. temperature=0 -> deterministic, factual answers (no creativity).
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    def query(self, question: str, top_k: int = 5) -> dict:
        """Answer one question. Returns {answer, sources}."""
        # 1. retrieve the most relevant policy chunks
        chunks = self.retriever.search(question, top_k=top_k)
        # 2. format them into context and fill the prompt
        context = _build_context(chunks)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        # 3. ask the LLM
        response = self.llm.invoke(prompt)
        answer = response.content

        # 4. return the answer plus the sources it was grounded on
        #    (this feeds the 'Sources' panel in the frontend)
        sources = [
            {
                "policy_name": c["policy_name"],
                "section_heading": c["section_heading"],
                "text": c["text"],
                "chunk_id": c["chunk_id"],
            }
            for c in chunks
        ]
        return {"answer": answer, "sources": sources}


# Quick manual test:  python -m src.rag.generator "late submission penalty?"
if __name__ == "__main__":
    import sys

    if not os.environ.get("GROQ_API_KEY"):
        raise SystemExit("Set GROQ_API_KEY first (add it to your .env file)")

    chunks_file = Path(__file__).resolve().parents[2] / "data" / "processed" / "chunks.json"
    rag = RAGGenerator(chunks_file)

    q = sys.argv[1] if len(sys.argv) > 1 else "what is the late submission penalty?"
    out = rag.query(q)

    print(f"\nQ: {q}\n")
    print("ANSWER:\n" + out["answer"] + "\n")
    print("SOURCES:")
    for s in out["sources"]:
        print(f"  - [{s['policy_name']} — {s['section_heading']}]")