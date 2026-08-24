import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from Services.Chunker import baseline_chunk, structure_aware_chunk

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Connect to running Docker Qdrant instance
qdrant_client = QdrantClient(url="http://localhost:6333")

EMBEDDING_DIM = 3072  # gemini-embedding-001 output dimension

def setup_collections():
    for col_name in ["baseline_chunks", "structure_chunks"]:
        if not qdrant_client.collection_exists(col_name):
            qdrant_client.create_collection(
                collection_name=col_name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )

def parse_frontmatter(content: str):
    """Extract YAML-style metadata block and body text."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
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
    doc_files = [f for f in os.listdir(data_dir) if f.endswith(".md")]
    
    baseline_points = []
    structure_points = []

    for filename in doc_files:
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        meta, body = parse_frontmatter(content)
        
        # Mandatory metadata fields
        base_meta = {
            "source_file": meta.get("source_file", filename),
            "policy_id": meta.get("policy_id", "UNKNOWN"),
            "region": meta.get("region", "GLOBAL"),
            "effective_date": meta.get("effective_date", "UNKNOWN")
        }

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