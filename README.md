# RegiMind AI 🎓

> A comparative study of retrieval methods for domain-specific RAG question answering — built on Cardiff University's academic policy documents.

![Status](https://img.shields.io/badge/status-Phase%204%20In%20Progress-yellow)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![QA Pairs](https://img.shields.io/badge/gold%20QA%20pairs-145-orange)
![Chunks](https://img.shields.io/badge/corpus%20chunks-716-purple)

---

## Overview

RegiMind AI is a research-driven question-answering system that helps students navigate complex academic regulations. Instead of searching through multiple dense policy PDFs, students can ask natural language questions and receive grounded, cited answers.

The core research contribution is a **systematic comparison of three retrieval strategies** — sparse (BM25), dense (sentence-transformers + FAISS), and hybrid (Reciprocal Rank Fusion) — evaluated on a manually curated gold QA dataset using both IR metrics and RAG faithfulness measures.

This project was developed as part of **CMT227 — Advanced Topics in NLP** at Cardiff University's School of Computer Science and Informatics.

> ⚠️ **Disclaimer:** This system is not official and does not constitute legal or academic advice. Always verify with your institution directly.

---

## Research Question

> Which retrieval strategy — sparse (BM25), dense (bi-encoder), or hybrid — produces the most accurate and faithful answers when the knowledge source is restricted to Cardiff University's academic regulations?

---

## Project Roadmap

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Data Ingestion | ✅ Complete |
| 2 | Text Cleaning & Preprocessing | ✅ Complete |
| 3 | Gold QA Dataset Construction | ✅ Complete |
| 4a | QA-to-Chunk Relevance Mapping (Qrels) | 🔄 In Progress |
| 4b | BM25 Baseline Retrieval | ⬜ Next |
| 4c | Dense Retrieval (Sentence-Transformers + FAISS) | ⬜ Planned |
| 4d | Hybrid Retrieval (Reciprocal Rank Fusion) | ⬜ Planned |
| 4e | IR Metric Evaluation (Recall@k, MRR, nDCG) | ⬜ Planned |
| 5 | RAG Pipeline (LlamaIndex) + RAGAS Evaluation | ⬜ Planned |
| 6 | Report Writing (ACL Format) | ⬜ Planned |

---

## Architecture

```
Source Documents (6 PDFs + 1 xlsx)
   │
   ▼
[Phase 1] Ingestion ──────────────► all_records.json (413 records)
   │
   ▼
[Phase 2] Cleaning & Chunking ───► cleaned_pages.json → chunks.json (716 chunks)
   │
   ▼
[Phase 3] Gold QA Dataset ───────► qa_pairs.json (145 QA pairs, 5 clusters)
   │
   ▼
[Phase 4] Retrieval Experiments
   ├── BM25 (sparse)
   ├── Sentence-Transformers + FAISS (dense)
   └── Reciprocal Rank Fusion (hybrid)
   │
   ▼
[Phase 4] IR Evaluation ─────────► Recall@k, MRR, nDCG
   │
   ▼
[Phase 5] RAG Generation ────────► LlamaIndex + LLM
   │
   ▼
[Phase 5] Faithfulness Eval ─────► RAGAS (faithfulness, answer relevancy,
                                    context precision, context recall)
```

---

## Corpus

The retrieval corpus is built from **7 Cardiff University source documents**:

| Document | Chunks |
|----------|--------|
| Academic Regulations Handbook 2025-26 | 293 |
| Assessment Calendar (xlsx) | 229 |
| COMSC School Handbook 2025-26 | 113 |
| Extenuating Circumstances Procedure | 33 |
| Academic Misconduct Procedure | 27 |
| Academic Integrity Policy | 15 |
| Late Submission Policy | 6 |
| **Total** | **716** |

---

## Gold QA Dataset

145 manually written question-answer pairs across 5 thematic clusters:

| Cluster | Count |
|---------|-------|
| Late Submission | 30 |
| Extenuating Circumstances | 30 |
| Academic Integrity / Misconduct | 30 |
| General Academic Regulations | 30 |
| Assessment Calendar | 25 |

Each pair is tagged with source document, question type (factual / procedural / eligibility / comparative), and difficulty level. Questions use natural student language rather than verbatim policy text.

---

## Evaluation Strategy

**Retrieval (IR metrics):** Recall@k (k=1,3,5,10), MRR, nDCG — measured against manually constructed relevance judgments (qrels).

**Generation (RAGAS):** Faithfulness, answer relevancy, context precision, context recall — measuring whether the generated answer is actually grounded in the retrieved passages.

**Qualitative:** Manual error analysis of retrieval failures and hallucination patterns across strategies.

---

## Methodology Highlights

- **No model training** — the project uses only inference with pre-trained models; this is a retrieval comparison study, not a fine-tuning study
- **Generalised preprocessing** — frequency-based header detection, signal-based TOC filtering, and Unicode normalisation that generalise beyond these specific documents
- **Controlled comparison** — all three retrieval methods run against the same chunks, same questions, same evaluation metrics, with only the retrieval strategy varying
- **LlamaIndex deferred to Phase 5** — Phases 1–4 are fully local and inspectable for research methodology transparency

---

## Repository Structure

```
regimind-ai/
│
├── data/
│   ├── raw/                        # Original source PDFs (not committed)
│   ├── processed/
│   │   ├── all_records.json        # Phase 1: raw extracted records
│   │   ├── filter_log.json         # Phase 2: dropped pages + reasons
│   │   ├── cleaned_pages.json      # Phase 2: clean page-level text
│   │   └── chunks.json             # Phase 2: final retrieval corpus
│   └── qa/
│       ├── RegiMindAI_Gold_QA_145.xlsx  # Phase 3: gold dataset
│       ├── qa_pairs.json           # Phase 4a: QA pairs in JSON
│       └── qrels.json              # Phase 4a: relevance judgments
│
├── src/
│   ├── ingestion/
│   │   ├── extract_pdf_to_text.py  # PDF extraction with PyMuPDF
│   │   ├── extract_xlsx_to_text.py # Assessment Calendar extraction
│   │   └── ingestion.py            # Orchestrator → all_records.json
│   ├── preprocessing/
│   │   ├── filter_and_clean.py     # Noise filtering & normalisation
│   │   ├── chunker.py              # Section-aware chunking
│   │   └── preprocess.py           # Orchestrator → chunks.json
│   ├── retrieval/                  # Phase 4: BM25, dense, hybrid
│   ├── evaluation/                 # Phase 4–5: IR metrics, RAGAS
│   └── generation/                 # Phase 5: RAG pipeline
│
├── notebooks/
│   └── RegiMindAI_Pipeline.ipynb   # Full pipeline notebook (Colab)
│
├── requirements.txt
└── README.md
```

---

## Setup

```bash
git clone https://github.com/yourusername/regimind-ai.git
cd regimind-ai

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| PDF Extraction | PyMuPDF (fitz) |
| Data Processing | pandas |
| Sparse Retrieval | rank_bm25 |
| Dense Retrieval | sentence-transformers, FAISS |
| Hybrid Fusion | Reciprocal Rank Fusion |
| RAG Framework | LlamaIndex |
| LLM | TBD |
| Evaluation | RAGAS, custom IR metrics |
| Notebook | Google Colab |

---

## Non-Goals

This project intentionally does not:

- Provide official academic advice or legally binding interpretations
- Replace direct communication with your academic institution
- Handle real-time policy updates (a fixed document snapshot is used)
- Fine-tune retrieval models (comparison uses pre-trained models only)

---

## Licence

This is an academic research project. Source documents remain the property of Cardiff University.