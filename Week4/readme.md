# Week 4: Debugging Retrieval — Hybrid, Reranking & Failure Separation

> **Scope Notice**: **This folder is dedicated exclusively to Week 4** of the AI Engineering League (Module M2: Retrieval & RAG). The baseline Week 3 project resides in `../Week3/`. This repository builds directly upon that foundation to diagnose dense retrieval blindspots on exact alphanumeric tokens (e.g. `HR-207 section 3.2`), triage failure modes via a formal failure taxonomy (**R** vs. **G** vs. **Not-In-Corpus**), and buy back Hit-rate@3 using **Hybrid BM25 + Reciprocal Rank Fusion (RRF, $k=60$)**.

---

## 1. Problem Statement

Your HR assistant answers *"how much parental leave do I get"* well enough, and then misses completely on *"what does HR-207 section 3.2 say about carry-over"* — it returns three earnest, semantically adjacent leave paragraphs, none of them section 3.2. 

The team lead's immediate reaction is to swap the LLM to a bigger model. In this week's assessment, we use our **inspection view** to prove where the failures actually live, make **exactly ONE retrieval change**, and measure the before and after numbers.

---

## 2. Key Architectural Differences: Week 3 vs. Week 4

| Dimension | Week 3 Baseline (`../Week3/`) | Week 4 Production (`./`) |
| :--- | :--- | :--- |
| **Directory Scope** | `Week3/` | **`Week4/` (This folder)** |
| **Primary Objective** | Ingest 6 PDF addenda, evaluate Baseline vs. Structure-Aware chunking, and prove regional isolation. | Diagnose dense retrieval failures on exact alphanumeric tokens, triage R vs. G errors, and buy back Hit@3. |
| **Retrieval Engine** | Dense semantic vector search (`gemini-embedding-001`, 3072 dim) + metadata payload filter. | **Hybrid Search**: Dense Vector Search + BM25 Inverted Lexical Matching fused via Reciprocal Rank Fusion ($k=60$). |
| **Chunking Strategy** | Evaluated 350-char sliding window vs. structure-aware header/table chunker. | Standardized on Structure-Aware chunker (28 chunks) with tokenized inverted indices for exact codes. |
| **Evaluation Set** | 8 ground-truth operational questions evaluating **Hit-in-Top-5**. | **12-Question Golden Set** (7 with exact structural tokens) evaluating **Hit-rate@3** and **p50 query latency**. |
| **Failure Analysis** | Documented table row splitting in sliding window. | **Formal Failure Taxonomy**: Triage every miss into **[R]** (Retrieval miss), **[G]** (Generation misuse), or **[Not-In-Corpus]** (Valid refusal). |
| **Primary Deliverable** | `../Week3/results.md` (Hit@5 table, regional filter demo, 3 citations, 3 refusals). | [`results.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week4/results.md) (Golden set, R/G tally, before/after Hit@3 & p50 latency, fixed vs. unfixed analysis, shipping decision). |

---

## 3. Week 4 System Architecture

```text
                             +--------------------------------------------+
                             |       6 Regional Leave Policy PDFs         |
                             |       (APAC, EMEA, LATAM, NA, UK, ANZ)     |
                             +---------------------+----------------------+
                                                   |
                                                   v
                             +--------------------------------------------+
                             |      Structure-Aware Header & Table AST    |
                             |      28 Indexed Chunks with Full Metadata  |
                             +---------------------+----------------------+
                                                   |
                     +-----------------------------+-----------------------------+
                     |                                                           |
                     v                                                           v
      +-----------------------------+                             +-----------------------------+
      |  Dense Vector Search        |                             |  BM25 Lexical Inverted      |
      |  Google gemini-embedding-001|                             |  Exact token index on codes |
      |  3072-dim Cosine (Qdrant)   |                             |  (HR-207, 3.2, APAC, etc.)  |
      +--------------+--------------+                             +--------------+--------------+
                     |                                                           |
                     +-----------------------------+-----------------------------+
                                                   |
                                                   v
                             +--------------------------------------------+
                             |      Reciprocal Rank Fusion (RRF, k=60)    |
                             |      Score(d) = 1/(60+r_dense) +           |
                             |                 1/(60+r_bm25)              |
                             +---------------------+----------------------+
                                                   |
                                                   v
                             +--------------------------------------------+
                             |      Inspection View & Failure Separation  |
                             |      - [R]: Retrieval Miss (Context Bad)   |
                             |      - [G]: Generation Miss (Context Good) |
                             |      - [Not-In-Corpus]: Valid Refusal      |
                             +---------------------+----------------------+
                                                   |
                                                   v
                             +--------------------------------------------+
                             |      Gemini 2.5 Flash Generation           |
                             |      - Strict Grounded Citations           |
                             |      - Refusal Guardrails on Corpus Gaps   |
                             +--------------------------------------------+
```

---

## 4. Project Directory Tree

```text
Week4/
├── .env                       # API credentials (GEMINI_API_KEY)
├── golden_set.jsonl           # 12 real employee questions with known-correct chunk IDs
├── results.md                 # Complete Week 4 benchmark report (Hit@3, R/G tally, Latency, Code Diff)
├── readme.md                  # Week 4 overview, architecture & Week 3 vs Week 4 comparison
├── INSTALLATION.md            # Week 4 setup and pipeline execution guide
├── requirements.txt           # Dependencies (including rank-bm25, google-genai, qdrant-client)
├── ask.py                     # Interactive CLI powered by Week 4 Hybrid BM25+RRF retriever
├── data_drop/                 # 6 Regional leave policy PDF addenda
│   ├── HR-207_APAC.pdf
│   ├── HR-207_EMEA.pdf
│   ├── HR-208_LATAM.pdf
│   ├── HR-208_NA.pdf
│   ├── HR-209_ANZ.pdf
│   └── HR-209_UK.pdf
├── Services/
│   ├── __init__.py
│   ├── Chunker.py             # Structure-Aware Header & Table chunker
│   ├── hybrid_retriever.py    # DenseRetriever, BM25Retriever & HybridRetriever (RRF k=60)
│   ├── injest.py              # PDF extraction & Qdrant ingestion with metadata payloads
│   ├── bench_mark.py          # Week 4 Benchmark runner & results.md generator
│   ├── rag_engine.py          # Grounded synthesis engine using Hybrid retrieval by default
│   └── ask.py                 # Interactive question handler with retrieved source inspection
└── qdrant_storage/            # Persistent local Qdrant vector database storage
```

---

## 5. Week 4 Benchmark Results Summary

*Source: produced live by `python -m Services.bench_mark`, written to [`results.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week4/results.md). Numbers below reflect the current run; latency jitters slightly between runs since it is dominated by the remote embedding API.*

### 5.1 Golden Set & Failure Tally
- **Total Questions Evaluated**: 12 real employee inquiries, all answerable from the corpus.
- **Exact Alphanumeric Token Queries**: **7 / 12** carry explicit policy numbers, section codes, region codes, or effective dates.
- **Failure Tally (Baseline Dense Cosine)**:
  - **[R] Retrieval Failures**: `3 / 12` — all three were vague/overview-style questions ("what does section 3 cover?") where dense drifts to section-scope preamble chunks. Notably, the exact-token lookups the team lead assumed would fail **all hit**.
  - **[G] Generation Failures**: `0 / 12` — whenever the correct chunk was in the top-3, the generator answered correctly.
  - **[Not-In-Corpus]**: `0 / 12` — every golden question is answerable.

### 5.2 Before vs After Retrieval Performance & Latency

| Evaluation Metric | Baseline (Dense Cosine) | After (Hybrid BM25 + RRF $k=60$) | Delta / Impact |
| :--- | :--- | :--- | :--- |
| **Hit-rate@3** | **9 / 12 (75.0%)** | **11 / 12 (91.7%)** | **+16.7 pts** (3 R failures fixed, 1 regression introduced) |
| **p50 Query Latency** | **~540 ms** | **~540 ms** | **≈ 0 ms** (in-memory BM25 + RRF add nothing vs the embedding round-trip) |

### 5.3 Shipping Decision
**SHIP — with eyes open.** Net hit-rate@3 rises +2 (fixes `d01`/`d02`/`d03`) at near-zero latency cost, but the change introduces one genuine regression (`d09`): dense alone had ranked the correct chunk #1, BM25 did not surface it, and RRF let two moderately-agreed chunks out-vote the single-list winner. Net math favours shipping; monitor `d09` and consider widening `top_n` or each retriever's candidate pool to recover it.

---

## 6. Quick Execution

```bash
# 1. Run the Week 4 Benchmark & generate results.md
python -m Services.bench_mark

# 2. Run Grounded QA Generation with Hybrid Retrieval & Refusal tests
python -m Services.rag_engine

# 3. Interactive CLI query (default: Hybrid Retrieval) with Source Inspection
python ask.py "What does HR-207 section 3.2 say about carry-over for probationary staff?"

# 4. Compare retrievers side by side on the same question (cosine | bm25 | hybrid)
python ask.py "What does HR-207 section 3 cover for APAC?" --retriever cosine
python ask.py "What does HR-207 section 3 cover for APAC?" --retriever bm25
python ask.py "What does HR-207 section 3 cover for APAC?" --retriever hybrid
```