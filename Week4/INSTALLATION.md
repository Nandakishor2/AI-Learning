# Week 4: Installation & Execution Guide

> **Scope Notice**: **This folder is dedicated exclusively to Week 4** of the AI Engineering League (*Debugging Retrieval — Hybrid, Reranking & Failure Separation*). For the baseline Week 3 RAG setup, please refer to [`../Week3/INSTALLATION.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week3/INSTALLATION.md).

---

## 1. Prerequisites

Ensure the following tools and services are available on your system:
- **Python**: Version 3.11+ (Python 3.14.x active in `./venv`)
- **Docker Desktop**: Running locally to host the Qdrant vector database container
- **Google Gemini API Key**: Valid key with access to `gemini-embedding-001` and `gemini-2.5-flash`

---

## 2. Environment Setup

### Step 2.1: Virtual Environment Activation

From the `Week4` project root:
```bash
# Activate existing virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows:
# .\venv\Scripts\Activate.ps1
```

### Step 2.2: Dependencies Installation

Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key packages utilized in Week 4:
- `rank-bm25`: BM25 lexical keyword retrieval over tokenized policy text
- `google-genai`: Google Gemini SDK for 3072-dim embeddings & grounded generation
- `qdrant-client`: High-speed vector database client
- `pypdf`: PDF text extraction
- `python-dotenv`: Environment configuration

### Step 2.3: Configure Environment Variables

Confirm your `.env` file exists in the `Week4` root directory:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Test your connection to Gemini:
```bash
python Connection/gemini.py
# Expected output: "Gemini response: Hello! Confirmed..."
```

---

## 3. Qdrant Vector Engine Startup

Ensure the Qdrant container is active and mapped to `./qdrant_storage`:

```bash
# Check if Qdrant container is already running
docker ps --filter "name=qdrant_rag"

# If stopped or not running, start it:
docker run -d -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
  --name qdrant_rag \
  qdrant/qdrant
```

Verify the Qdrant Dashboard is accessible: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

## 4. Week 4 Pipeline Execution

### Step 4.1: Re-Ingest Policy Addenda (If vector store is clean)
```bash
# Parses the 6 regional PDF addenda into structure-aware chunks and loads them into Qdrant:
python -m Services.injest
```

### Step 4.2: Execute Week 4 Golden Set Benchmark & Report Generator
Runs the **12-question Golden Set** benchmark, compares **Baseline Dense Retrieval vs. Hybrid BM25+RRF ($k=60$)**, logs **Hit-rate@3 Before -> After**, measures **p50 Latency**, evaluates the **MMR Diversity Challenge**, and auto-generates `results.md`:

```bash
python -m Services.bench_mark
```

Output highlights printed to the terminal:
- Baseline Hit-rate@3 & p50 query latency.
- Inspection view failure tally: `[R]` (Retrieval failures), `[G]` (Generation failures), `[Not-In-Corpus]`.
- Hybrid BM25+RRF Hit-rate@3 & p50 query latency.
- Per-question resolution status: `[Preserved HIT]`, `[FIXED (R -> HIT)]`, `[Untouched (Not-In-Corpus)]`.
- Automatically generated/updated: [`results.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week4/results.md).

### Step 4.3: Test End-to-End Generation & Guardrails
Evaluates grounded generation using the new Hybrid retriever, enforcing citations `[Chunk: <chunk_id>, Policy: <id>, Section: <sec>, Region: <reg>]` and honest refusals:

```bash
python -m Services.rag_engine
```

### Step 4.4: Interactive Querying with Source Inspection
Ask custom queries interactively or via CLI argument. Default retriever is Hybrid BM25+RRF:

```bash
python ask.py "What does HR-207 section 3.2 say about carry-over for probationary staff?"
```

Use `--retriever` (`-r`) to switch between the three methods for a side-by-side demo:

```bash
python ask.py "What does HR-207 section 3 cover for APAC?" -r cosine   # dense only  -> misses the section-3 chunk
python ask.py "What does HR-207 section 3 cover for APAC?" -r bm25     # lexical only -> finds it at rank 1
python ask.py "What does HR-207 section 3 cover for APAC?" -r hybrid   # fused (default) -> finds it in top-3
```

---

## 5. Week 4 Verification Checklist

- [x] `golden_set.jsonl`: 12 real employee questions with known-correct chunk IDs (7 with exact alphanumeric tokens).
- [x] Baseline Dense Hit-rate@3 measured and written down (`9/12`, 75.0%).
- [x] Baseline p50 latency measured (~540 ms/query; embedding-API dominated).
- [x] Failure separation completed with inspection-view evidence for every miss (tally: R=3, G=0, Not-In-Corpus=0).
- [x] Exactly ONE retrieval change applied: BM25 + Reciprocal Rank Fusion ($k=60$).
- [x] After Hybrid Hit-rate@3 measured (`11/12`, 91.7%) and After p50 latency measured (~540 ms/query).
- [x] Per-question fixed/unfixed/regression table: fixed `d01`/`d02`/`d03`, one regression `d09`.
- [x] [`results.md`](file:///Users/softsuave/Desktop/AI-Learning-Production/Week4/results.md) is regenerated live by `python -m Services.bench_mark`.
