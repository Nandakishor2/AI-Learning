import pytest
from src.ingestion.document_loader import load_policy_documents
from src.ingestion.metadata_validator import validate_chunks
from src.ingestion.chunker import structure_aware_chunk

def test_document_ingestion_count():
    docs = load_policy_documents()
    assert len(docs) == 6, f"Expected exactly 6 policy addenda documents, found {len(docs)}"

def test_metadata_completeness():
    docs = load_policy_documents()
    all_chunks = []
    for d in docs:
        chunks = structure_aware_chunk(d["body"])
        for idx, ch in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"struct_{d['policy_id']}_{d['region']}_{idx}",
                "source_file": d["source_file"],
                "policy_id": d["policy_id"],
                "region": d["region"],
                "effective_date": d["effective_date"],
                "section": ch["section"],
                "text": ch["text"]
            })

    report = validate_chunks(all_chunks, total_files=len(docs))
    assert report.is_valid is True
    assert report.chunks_missing_source_file == 0
    assert report.chunks_missing_policy_id == 0
    assert report.chunks_missing_region == 0
    assert report.chunks_missing_effective_date == 0
