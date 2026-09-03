# Installation & Environment Setup Guide

This guide walks through setting up the local environment, launching the Qdrant vector engine, indexing the regional leave policy addenda, and executing the retrieval and generation pipelines.

---

## Prerequisites
- **Python**: Version 3.11+
- **Docker Desktop**: Running locally (for Qdrant vector store)
- **Google Gemini API Key**: Valid key with access to `gemini-2.5-flash` and `gemini-embedding-001`

---

## Step 1: Clone Repository & Setup Virtual Environment

```powershell
# Navigate to the project root
cd "D:\AI Learning\Week3"

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Step 2: Install Dependencies

```powershell
pip install google-genai qdrant-client pydantic python-dotenv
```

## Step 3: Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

## Step 4: Launch Qdrant Vector Engine

Run the official Qdrant container with persistent storage mapped to `./qdrant_storage`:

```powershell
docker run -d -p 6333:6333 -p 6334:6334 -v "${PWD}/qdrant_storage:/qdrant/storage:z" --name qdrant_rag qdrant/qdrant
```

Verify that the Qdrant dashboard is operational at: http://localhost:6333/dashboard

## Step 5: Execute Ingestion, Benchmarks, and Generation

Execute the pipeline scripts using the `-m` module runner:

```powershell
# 1. Ingest documents into Qdrant (3072-dim embeddings for baseline & structure collections)
python -m Services.injest

# 2. Run the 8-question Hit-in-Top-5 benchmark & metadata filtering demo
python -m Services.bench_mark

# 3. Run Grounded QA Generation, Citation Enforcement, and Refusal Test
python -m Services.rag_engine
```
