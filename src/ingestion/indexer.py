import uuid
from typing import Dict, List, Tuple
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.config import (
    get_gemini_client,
    get_qdrant_client,
    EMBEDDING_MODEL,
    EMBEDDING_DIM,
    BASELINE_COLLECTION,
    STRUCTURE_COLLECTION,
)
from src.ingestion.document_loader import load_policy_documents
from src.ingestion.chunker import baseline_chunk, structure_aware_chunk
from src.ingestion.metadata_validator import validate_chunks, IngestionValidationReport

def get_embedding(text: str) -> List[float]:
    """Generate dense embedding vector using Gemini gemini-embedding-001."""
    client = get_gemini_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return response.embeddings[0].values

def setup_collections(qdrant_client):
    """Recreate Qdrant collections for baseline and structure-aware chunks."""
    for col in [BASELINE_COLLECTION, STRUCTURE_COLLECTION]:
        if qdrant_client.collection_exists(col):
            qdrant_client.delete_collection(col)
        qdrant_client.create_collection(
            collection_name=col,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )

def run_ingestion(data_dir=None) -> Tuple[IngestionValidationReport, IngestionValidationReport, Dict]:
    """
    Ingests ONLY the 6 regional policy addenda into Qdrant under both chunking strategies.
    Attaches complete metadata to every chunk: chunk_id, source_file, policy_id, region, effective_date, section, text.
    """
    qdrant = get_qdrant_client()
    setup_collections(qdrant)
    
    docs = load_policy_documents(data_dir)
    print(f"Loaded {len(docs)} regional policy addenda documents.")

    baseline_points = []
    structure_points = []
    
    baseline_chunk_records = []
    structure_chunk_records = []

    for doc in docs:
        source_file = doc["source_file"]
        policy_id = doc["policy_id"]
        region = doc["region"]
        effective_date = doc["effective_date"]
        body = doc["body"]

        # Strategy A: Baseline Fixed Sliding Window
        b_chunks = baseline_chunk(body)
        for idx, item in enumerate(b_chunks):
            chunk_id = f"base_{policy_id}_{region}_{idx}"
            text = item["text"]
            section = item["section"]
            emb = get_embedding(text)
            
            payload = {
                "chunk_id": chunk_id,
                "source_file": source_file,
                "policy_id": policy_id,
                "region": region,
                "effective_date": effective_date,
                "section": section,
                "text": text
            }
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"base_{source_file}_{idx}"))
            baseline_points.append(PointStruct(id=point_id, vector=emb, payload=payload))
            baseline_chunk_records.append(payload)

        # Strategy B: Structure-Aware Header & Table Preserving Chunker
        s_chunks = structure_aware_chunk(body)
        for idx, item in enumerate(s_chunks):
            chunk_id = f"struct_{policy_id}_{region}_{idx}"
            text = item["text"]
            section = item["section"]
            emb = get_embedding(text)
            
            payload = {
                "chunk_id": chunk_id,
                "source_file": source_file,
                "policy_id": policy_id,
                "region": region,
                "effective_date": effective_date,
                "section": section,
                "text": text
            }
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"struct_{source_file}_{idx}"))
            structure_points.append(PointStruct(id=point_id, vector=emb, payload=payload))
            structure_chunk_records.append(payload)

    # Upsert points
    qdrant.upsert(collection_name=BASELINE_COLLECTION, points=baseline_points)
    qdrant.upsert(collection_name=STRUCTURE_COLLECTION, points=structure_points)

    report_baseline = validate_chunks(baseline_chunk_records, total_files=len(docs))
    report_structure = validate_chunks(structure_chunk_records, total_files=len(docs))

    summary = {
        "files_ingested": [d["filename"] for d in docs],
        "baseline_chunk_count": len(baseline_points),
        "structure_chunk_count": len(structure_points),
        "baseline_report": report_baseline.to_dict(),
        "structure_report": report_structure.to_dict(),
    }
    
    print(f"Ingestion complete: {len(baseline_points)} baseline chunks, {len(structure_points)} structure chunks.")
    return report_baseline, report_structure, summary

if __name__ == "__main__":
    run_ingestion()
