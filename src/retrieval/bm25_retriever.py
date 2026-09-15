import re
from typing import List, Dict
from rank_bm25 import BM25Okapi
from src.config import get_qdrant_client, STRUCTURE_COLLECTION

def tokenize(text: str) -> List[str]:
    """
    Tokenizes text while preserving alphanumeric codes, policy numbers (HR-207),
    and decimal section numbers (3.2, 2.1).
    """
    return re.findall(r'\b[a-zA-Z0-9\.\-]+\b', text.lower())

class BM25Retriever:
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION):
        self.collection_name = collection_name
        self.qdrant_client = get_qdrant_client()
        
        # Load all indexed chunks from Qdrant
        records, _ = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=500,
            with_payload=True,
            with_vectors=False
        )
        self.points = records
        self.corpus_texts = [
            f"Policy: {p.payload.get('policy_id', '')} | Region: {p.payload.get('region', '')} | Section: {p.payload.get('section', '')} | File: {p.payload.get('source_file', '')}\n{p.payload.get('text', '')}"
            for p in self.points
        ]
        self.payloads = [p.payload for p in self.points]
        
        # Build tokenized BM25 index
        tokenized_corpus = [tokenize(doc) for doc in self.corpus_texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 10) -> List[Dict]:
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices, start=1):
            payload = self.payloads[idx]
            results.append({
                "rank": rank,
                "chunk_id": payload.get("chunk_id", ""),
                "score": float(scores[idx]),
                "policy_id": payload.get("policy_id", "UNKNOWN"),
                "section": payload.get("section", "UNKNOWN"),
                "region": payload.get("region", "UNKNOWN"),
                "effective_date": payload.get("effective_date", "UNKNOWN"),
                "source_file": payload.get("source_file", "UNKNOWN"),
                "text": payload.get("text", "")
            })
        return results
