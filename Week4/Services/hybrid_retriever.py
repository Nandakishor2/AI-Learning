import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
qdrant_client = QdrantClient(url="http://localhost:6333")

def tokenize(text: str) -> list[str]:
    """Tokenize text preserving alphanumeric codes like HR-207, 3.2, etc."""
    return re.findall(r'\b[a-zA-Z0-9\.\-]+\b', text.lower())

def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

class HybridRetriever:
    def __init__(self, collection_name: str = "structure_chunks"):
        self.collection_name = collection_name
        
        # Load all points from Qdrant into memory to build the BM25 inverted index
        records, _ = qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=200,
            with_payload=True,
            with_vectors=False
        )
        self.points = records
        self.corpus_chunks = [p.payload.get("text", "") for p in self.points]
        self.chunk_ids = [p.payload.get("chunk_id", "") for p in self.points]
        
        # Build BM25 index
        tokenized_corpus = [tokenize(doc) for doc in self.corpus_chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search_dense(self, query: str, limit: int = 10):
        emb = get_embedding(query)
        points = qdrant_client.query_points(
            collection_name=self.collection_name,
            query=emb,
            limit=limit
        ).points
        return [p.payload.get("chunk_id") for p in points]

    def search_bm25(self, query: str, limit: int = 10):
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]
        return [self.chunk_ids[i] for i in top_indices]

    def rrf_fusion(self, dense_ranks: list[str], bm25_ranks: list[str], k: int = 60, top_n: int = 3):
        """
        Reciprocal Rank Fusion (RRF) with standard smoothing k=60.
        Score(d) = sum( 1 / (k + rank_m(d)) )
        """
        rrf_scores = {}
        
        # Accumulate dense ranks
        for rank, cid in enumerate(dense_ranks, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            
        # Accumulate BM25 ranks
        for rank, cid in enumerate(bm25_ranks, start=1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            
        ranked = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return [cid for cid, _ in ranked[:top_n]]

    def retrieve(self, query: str, top_n: int = 3):
        dense_top10 = self.search_dense(query, limit=10)
        bm25_top10 = self.search_bm25(query, limit=10)
        return self.rrf_fusion(dense_top10, bm25_top10, k=60, top_n=top_n)

if __name__ == "__main__":
    retriever = HybridRetriever()
    test_q = "What does HR-207 section 3.2 say about carry-over?"
    results = retriever.retrieve(test_q, top_n=3)
    print(f"Test Query: '{test_q}'")
    print(f"Retrieved Top-3 with RRF: {results}")