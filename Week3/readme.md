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
├── EVALUATION_REPORT.md       # Benchmark findings and Q&A analysis
├── data_drop/                 # 6 Regional leave policy markdown files
│   ├── HR-207_APAC.md
│   ├── HR-207_EMEA.md
│   ├── HR-208_LATAM.md
│   ├── HR-208_NA.md
│   ├── HR-209_ANZ.md
│   └── HR-209_UK.md
├── Services/
│   ├── __init__.py
│   ├── Chunker.py             # Baseline and Structure-Aware chunkers
│   ├── injest.py              # Frontmatter parsing, embedding & Qdrant upsert
│   ├── bench_mark.py          # 8-question Hit@5 benchmark & metadata filtering demo
│   └── rag_engine.py          # Grounded synthesis, citation formatter & refusal handler
└── qdrant_storage/            # Persistent local Qdrant data storage
```

## Technical Highlights

- **Dual Chunking Strategies**:
  - **Baseline Chunker**: Fixed character slicing (350 characters, 50-character overlap) yielding 17 chunks.
  - **Structure-Aware Chunker**: Markdown section parser preserving `#`, `##`, `###` headings, policy IDs, and complete tables yielding 26 chunks.
- **Dense Vector Embeddings & Vector DB**:
  - Google `gemini-embedding-001` (3072 dimensions, Cosine distance).
  - Qdrant Vector Store indexing metadata payloads (`source_file`, `policy_id`, `region`, `effective_date`).
- **Retrieval Benchmark (Hit-in-Top-5)**:
  - Evaluated across 8 ground-truth operational questions covering all 6 regions with table-specific clauses.
  - Baseline Chunker: 8/8 (100%)
  - Structure-Aware Chunker: 8/8 (100%)
- **Metadata Filtering**:
  - Implemented `where={"region": "EMEA"}` payload filter, proving complete regional isolation without cross-region noise.
- **Grounded Generation & Guardrails**:
  - Enforced clause citations: `[Policy: <ID>, Section: <Section>, Region: <Region>]`.
  - Refusal mechanism for ungrounded / out-of-scope inquiries: `"I do not have sufficient information in the provided leave policy documents to answer this question."`