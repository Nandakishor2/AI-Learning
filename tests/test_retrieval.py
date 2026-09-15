import pytest
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.config import STRUCTURE_COLLECTION

def test_dense_retriever():
    retriever = DenseRetriever(collection_name=STRUCTURE_COLLECTION)
    results = retriever.retrieve("What is the carry-over cap for Tier 1 staff in APAC?", top_k=3)
    assert len(results) > 0
    assert results[0]["policy_id"] in ["HR-207", "HR-208", "HR-209"]

def test_region_metadata_filtering():
    retriever = DenseRetriever(collection_name=STRUCTURE_COLLECTION)
    unfiltered = retriever.retrieve("What is the carry-over cap for probationary employees?", region=None, top_k=3)
    filtered = retriever.retrieve("What is the carry-over cap for probationary employees?", region="EMEA", top_k=3)
    
    assert len(filtered) > 0
    assert all(r["region"] == "EMEA" for r in filtered)

def test_hybrid_rrf_retriever():
    retriever = HybridRetriever(collection_name=STRUCTURE_COLLECTION)
    results = retriever.retrieve("Under HR-207 Section 3.2, what is the probationary cap?", top_n=3, k=60)
    assert len(results) == 3
    assert any("HR-207" in r["policy_id"] for r in results)
