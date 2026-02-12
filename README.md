# RegiMind AI 🎓

> An end-to-end NLP system for querying academic regulations — built from a raw policy PDF to a production-ready RAG pipeline.

![Status](https://img.shields.io/badge/status-Phase%201%20Complete-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)


---

## Overview

RegiMind AI is a production-grade question-answering system designed to help students navigate complex academic regulations. Instead of searching through dense policy handbooks manually, students can ask natural language questions and receive grounded, cited answers.

The system is built end-to-end — from raw PDF ingestion through transformer-based retrieval, reranking, and RAG answer generation — with a focus on faithfulness, calibration, and production readiness.

> ⚠️ **Disclaimer:** This system is not official and does not constitute legal or academic advice. Always verify with your institution directly.

---

## Project Roadmap

| Phase | Title | Status |
|-------|-------|--------|
| 0 | Project & Product Setup | ✅ Complete |
| 1 | Data Ingestion | ✅ Complete |
| 2 | Text Cleaning & Structuring | 🔜 Up next |
| 3 | Corpus EDA | ⬜ Planned |
| 4 | Gold QA Dataset Creation | ⬜ Planned |
| 5 | Baseline Retrieval (BM25) | ⬜ Planned |
| 6 | Transformer Embeddings | ⬜ Planned |
| 7 | Train Bi-Encoder Retriever | ⬜ Planned |
| 8 | Train Cross-Encoder Reranker | ⬜ Planned |
| 9 | Query Understanding Models | ⬜ Planned |
| 10 | RAG Answer Generation | ⬜ Planned |
| 11 | Faithfulness & Calibration | ⬜ Planned |
| 12 | Evaluation Suite | ⬜ Planned |
| 13 | Backend API | ⬜ Planned |
| 14 | Frontend | ⬜ Planned |
| 15 | Deployment & Ops | ⬜ Planned |
| 16 | Documentation & Branding | ⬜ Planned |

---

## Architecture (Planned)

```
Raw PDF
   │
   ▼
[Phase 1] PDF Ingestion → handbook_pages.json
   │
   ▼
[Phase 2] Text Cleaning → handbook_sections.jsonl
   │
   ├──▶ [Phase 3] EDA & Chunking Strategy
   │
   ├──▶ [Phase 4] Gold QA Dataset
   │
   ▼
[Phase 5] BM25 Baseline Retriever
   │
   ▼
[Phase 6] Dense Retriever (Transformer Embeddings)
   │
   ▼
[Phase 7] Fine-tuned Bi-Encoder (Training)
   │
   ▼
[Phase 8] Cross-Encoder Reranker (Training)
   │
   ▼
[Phase 9] Query Understanding (Intent + Rewriting)
   │
   ▼
[Phase 10] RAG Answer Generation (LLM + Citations)
   │
   ▼
[Phase 11] Faithfulness & Hallucination Control
   │
   ▼
[Phase 13] FastAPI Backend
   │
   ▼
[Phase 14] Next.js Frontend
   │
   ▼
[Phase 15] Deployed System
```

---

## Phase 1 — Data Ingestion ✅

**Goal:** Turn a raw policy PDF into a machine-readable, page-indexed corpus.

### What was done

The first phase of the pipeline handles loading the academic regulations PDF and extracting its text content in a structured, reproducible format. Each page is extracted individually and stored with its page number, raw text content, and metadata. The output is a clean JSON file that feeds directly into Phase 2 cleaning.

### Output

`data/handbook_pages.json` — a list of page objects with the following schema:

```json
[
  {
    "page_number": 1,
    "text": "...",
    "char_count": 842,
    "word_count": 134
  },
  ...
]
```

### How to run

```bash
# Install dependencies
pip install -r requirements.txt

# Run ingestion
python src/ingestion/extract_pages.py --input data/raw/handbook.pdf --output data/handbook_pages.json
```

### Dependencies

- `PyMuPDF` (fitz) — PDF parsing
- `pdfplumber` — fallback extraction and table detection
- `tqdm` — progress tracking

---

## Repository Structure

```
regimind-ai/
│
├── data/
│   ├── raw/                    # Original source PDFs (not committed)
│   ├── handbook_pages.json     # Phase 1 output
│   ├── handbook_sections.jsonl # Phase 2 output (planned)
│   └── gold_questions.json     # Phase 4 output (planned)
│
├── src/
│   ├── ingestion/              # Phase 1: PDF → JSON
│   ├── preprocessing/          # Phase 2: Cleaning & structuring
│   ├── retrieval/              # Phases 5–8: BM25, bi-encoder, reranker
│   ├── query_understanding/    # Phase 9: Intent, rewriting, extraction
│   ├── generation/             # Phase 10: RAG pipeline
│   ├── evaluation/             # Phase 12: Metrics & error analysis
│   └── api/                    # Phase 13: FastAPI backend
│
├── notebooks/
│   ├── phase3_eda.ipynb        # Corpus EDA (planned)
│   └── phase12_eval.ipynb      # Evaluation analysis (planned)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/regimind-ai.git
cd regimind-ai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

---

## Non-Goals

This project intentionally does not:

- Provide official academic advice or legally binding interpretations
- Replace direct communication with your academic institution
- Guarantee accuracy for regulations that change over time

---

## Evaluation (Planned)

Once the full pipeline is built, the system will be evaluated across multiple dimensions:

**Retrieval** — Recall@5, Recall@10, nDCG, MRR

**Reranking** — Precision@1, NDCG@5

**QA Accuracy** — Exact match, F1 on gold QA dataset

**Faithfulness** — % of answers fully supported by retrieved context

**Calibration** — Confidence score correlation with correctness

---

## Tech Stack (Planned)

| Component | Technology |
|-----------|-----------|
| PDF Ingestion | PyMuPDF, pdfplumber |
| Embeddings | sentence-transformers, HuggingFace |
| Vector Index | FAISS |
| BM25 Baseline | rank_bm25 |
| LLM (Generation) | OpenAI API / local model |
| Fine-tuning | HuggingFace Trainer, LoRA |
| Backend API | FastAPI |
| Frontend | Next.js |
| Deployment | TBD |

---

## Contributing

This is a personal portfolio project. Feedback and suggestions are welcome via issues.

---