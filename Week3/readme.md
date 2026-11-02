# Global HR Leave Policy RAG Assistant

A retrieval-augmented generation (RAG) assistant designed to parse, index, search, and answer employee leave policy queries across six regional jurisdictions (APAC, EMEA, NA, LATAM, UK, ANZ) with strict grounding, source citations, and graceful out-of-domain refusals.

## System Architecture

```text
                             +-------------------------------+
                             | 6 Regional Leave Policy Docs  |
                             | (YAML Frontmatter + Tables)   |
                             +---------------+---------------+
                                             |
                     +-----------------------+-----------------------+
                     |                                               |
                     v                                               v
        +-------------------------+                     +-------------------------+
        |  Strategy A: Baseline   |                     |  Strategy B: Structure  |
        |  (350-char sliding win) |                     |  (Header & Table Aware) |
        +------------+------------+                     +------------+------------+
                     |                                               |
                     +-----------------------+-----------------------+
                                             v
                          +-------------------------------------+
                          | Gemini Embedding (gemini-embedding-001)
                          | Dimension: 3072                     |
                          +------------------+------------------+
                                             v
                          +-------------------------------------+
                          | Qdrant Vector DB (Docker :6333)     |
                          | - baseline_chunks                   |
                          | - structure_chunks                  |
                          +------------------+------------------+
                                             |
                            +----------------+----------------+
                            |                                 |
                            v                                 v
                 +--------------------+            +--------------------+
                 | Semantic Retrieval |            |  Metadata Filter   |
                 | (Unfiltered Top-k) |            | (region == 'EMEA') |
                 +----------+---------+            +----------+---------+
                            |                                 |
                            +----------------+----------------+
                                             v
                          +-------------------------------------+
                          | Gemini 2.5 Flash Generation         |
                          | - Temperature: 0.0                  |
                          | - Exact Citations [Policy, Sec, Reg]|
                          | - Out-of-Domain Refusal Guardrail   |
                          +-------------------------------------+
```

## Project Directory Tree

```text
Week3/
├── .env                       # API configuration
├── INSTALLATION.md            # Environment setup instructions
├── README.md                  # Project overview and architecture
├── DEMO_GUIDE.md              # Live demo script, Q&A dataset & talking points
├── results.md                 # Benchmark findings, Hit@5 evaluation & Q&A analysis
├── ask.py                     # Interactive CLI for user-entered questions
├── data_drop/                 # 6 Regional leave policy PDF documents
│   ├── HR-207_APAC.pdf
│   ├── HR-207_EMEA.pdf
│   ├── HR-208_LATAM.pdf
│   ├── HR-208_NA.pdf
│   ├── HR-209_ANZ.pdf
│   └── HR-209_UK.pdf
├── Services/
│   ├── __init__.py
│   ├── Chunker.py             # Baseline and Structure-Aware chunkers
│   ├── injest.py              # PDF extraction, embedding & Qdrant upsert
│   ├── bench_mark.py          # 8-question Hit@5 benchmark, filtering demo & results.md generator
│   ├── rag_engine.py          # Grounded synthesis, citation formatter & refusal handler
│   └── ask.py                 # Interactive question handler across all policies
└── qdrant_storage/            # Persistent local Qdrant data storage
```

## Technical Highlights

- **Dual Chunking Strategies**:
  - **Baseline Chunker**: Fixed character slicing (350 characters, 50-character overlap) yielding 17 chunks.
  - **Structure-Aware Chunker**: Markdown section parser preserving `#`, `##`, `###` headings, policy IDs, and complete tables yielding 28 chunks.
- **Dense Vector Embeddings & Vector DB**:
  - Google `gemini-embedding-001` (3072 dimensions, Cosine distance).
  - Qdrant Vector Store indexing metadata payloads (`source_file`, `policy_id`, `region`, `effective_date`).
- **Retrieval Benchmark (Hit-in-Top-5)**:
  - Evaluated across 8 ground-truth operational questions covering all 6 regions with table-specific clauses.
  - Baseline Chunker: 8/8 (100%)
  - Structure-Aware Chunker: 8/8 (100%)
  - Full output saved automatically to [`results.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week3/results.md).
- **Metadata Filtering**:
  - Implemented `where={"region": "EMEA"}` payload filter, proving complete regional isolation without cross-region noise.
- **Grounded Generation & Guardrails**:
  - Enforced clause citations: `[Policy: <ID>, Section: <Section>, Region: <Region>]`.
  - Refusal mechanism for ungrounded / out-of-scope inquiries: `"I do not have sufficient information in the provided leave policy documents to answer this question."`

## Quick Execution

```bash
# 1. Ingest 6 PDF policies into Qdrant
python -m Services.injest

# 2. Run retrieval benchmark (Prints questions to terminal & writes results.md)
python -m Services.bench_mark

# 3. Run grounded QA generation & refusal test
python -m Services.rag_engine

# 4. Ask custom questions interactively (unrestricted across all regions)
python ask.py
```