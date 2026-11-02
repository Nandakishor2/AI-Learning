import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

import re
import pypdf

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Services.Chunker import baseline_chunk, structure_aware_chunk

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Connect to running Docker Qdrant instance
qdrant_client = QdrantClient(url="http://localhost:6333", check_compatibility=False)

EMBEDDING_DIM = 3072  # gemini-embedding-001 output dimension

def setup_collections():
    try:
        for col_name in ["baseline_chunks", "structure_chunks"]:
            if qdrant_client.collection_exists(col_name):
                print(f"Deleting existing collection: {col_name}")
                qdrant_client.delete_collection(col_name)
            qdrant_client.create_collection(
                collection_name=col_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"\n[!] Failed to connect to Qdrant at http://localhost:6333: {e}")
        print("[!] Please make sure Qdrant is running: docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant\n")
        raise

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from all pages of a PDF document."""
    reader = pypdf.PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)

def parse_frontmatter(content: str):
    """Extract YAML-style metadata block and body text."""
    meta = {}
    body = content
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
    return meta, body

def extract_metadata_and_body(filename: str, raw_content: str) -> tuple[dict, str]:
    """
    Extract metadata (source_file, policy_id, region, effective_date) and clean body.
    Supports YAML frontmatter blocks as well as filename/content regex fallbacks.
    """
    meta, body = parse_frontmatter(raw_content)
    stem = Path(filename).stem  # e.g., "HR-207_APAC"

    # Extract policy_id
    if "policy_id" not in meta:
        policy_match = re.search(r"(HR-\d+)", stem) or re.search(r"(HR-\d+)", raw_content)
        meta["policy_id"] = policy_match.group(1) if policy_match else "UNKNOWN"

    # Extract region
    if "region" not in meta:
        region_match = re.search(r"(APAC|EMEA|LATAM|NA|ANZ|UK)", stem, re.IGNORECASE)
        if not region_match:
            region_match = re.search(r"region[:\s]+(APAC|EMEA|LATAM|NA|ANZ|UK)", raw_content, re.IGNORECASE)
        meta["region"] = region_match.group(1).upper() if region_match else "GLOBAL"

    # Extract effective_date
    if "effective_date" not in meta:
        date_match = re.search(r"effective(?:_date)?[:\s]+(\d{4}-\d{2}-\d{2})", raw_content, re.IGNORECASE)
        meta["effective_date"] = date_match.group(1) if date_match else "2026-01-01"

    meta["source_file"] = filename
    return meta, body

def get_embedding(text: str) -> list[float]:
    """Generate dense embeddings via Gemini gemini-embedding-001."""
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

def run_ingestion(data_dir: str = "./data_drop"):
    setup_collections()
    
    doc_files = sorted([f for f in os.listdir(data_dir) if f.lower().endswith(".pdf")])
    if not doc_files:
        print(f"No PDF files found in {data_dir}. Please place PDF policy documents in {data_dir}.")
        return

    print(f"Discovered {len(doc_files)} PDF files in {data_dir}: {doc_files}")
    
    baseline_points = []
    structure_points = []

    for filename in doc_files:
        filepath = os.path.join(data_dir, filename)
        raw_content = extract_text_from_pdf(filepath)

        base_meta, body = extract_metadata_and_body(filename, raw_content)
        print(f"Loaded {filename} -> Policy: {base_meta['policy_id']}, Region: {base_meta['region']}, Effective: {base_meta['effective_date']}")

        # 1. Baseline Fixed Chunker
        b_chunks = baseline_chunk(body)
        for idx, chunk in enumerate(b_chunks):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"base_{filename}_{idx}"))
            emb = get_embedding(chunk)
            payload = {
                **base_meta, 
                "chunk_id": f"base_{base_meta['policy_id']}_{base_meta['region']}_{idx}", 
                "text": chunk
            }
            baseline_points.append(PointStruct(id=point_id, vector=emb, payload=payload))

        # 2. Structure-Aware Chunker
        s_chunks = structure_aware_chunk(body)
        for idx, chunk in enumerate(s_chunks):
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"struct_{filename}_{idx}"))
            emb = get_embedding(chunk)
            payload = {
                **base_meta, 
                "chunk_id": f"struct_{base_meta['policy_id']}_{base_meta['region']}_{idx}", 
                "text": chunk
            }
            structure_points.append(PointStruct(id=point_id, vector=emb, payload=payload))

    # Upsert points into Qdrant
    qdrant_client.upsert(collection_name="baseline_chunks", points=baseline_points)
    qdrant_client.upsert(collection_name="structure_chunks", points=structure_points)

    print("Ingestion into Qdrant Complete!")
    print(f"Baseline chunks: {qdrant_client.count('baseline_chunks').count}")
    print(f"Structure chunks: {qdrant_client.count('structure_chunks').count}")

if __name__ == "__main__":
    run_ingestion()