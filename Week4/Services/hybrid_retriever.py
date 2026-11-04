import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
try:
    from rank_bm25 import BM25Okapi
except ImportError:
    import math
    class BM25Okapi:
        def __init__(self, corpus, k1=1.5, b=0.75):
            self.corpus_size = len(corpus)
            self.avgdl = sum(len(x) for x in corpus) / max(self.corpus_size, 1)
            self.corpus = corpus
            self.k1 = k1
            self.b = b
            self.doc_lens = [len(x) for x in corpus]
            self.nd = {}
            for document in corpus:
                for word in set(document):
                    self.nd[word] = self.nd.get(word, 0) + 1
            self.idf = {}
            for word, freq in self.nd.items():
                self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
        def get_scores(self, query):
            scores = [0.0] * self.corpus_size
            for q in query:
                q_idf = self.idf.get(q, 0.0)
                for i, doc in enumerate(self.corpus):
                    f = doc.count(q)
                    if f > 0:
                        denom = f + self.k1 * (1 - self.b + self.b * self.doc_lens[i] / max(self.avgdl, 1e-6))
                        scores[i] += q_idf * (f * (self.k1 + 1)) / denom
            return scores

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
qdrant_client = QdrantClient(url="http://localhost:6333", check_compatibility=False)

def tokenize(text: str) -> List[str]:
    """
    Tokenizes text while preserving alphanumeric codes, policy numbers (e.g., HR-207),
    and decimal section numbers (e.g., 3.2, 2.1).
    """
    return re.findall(r'\b[a-zA-Z0-9\.\-]+\b', text.lower())

def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

class DenseRetriever:
    """Baseline dense semantic retriever using gemini-embedding-001 and Qdrant."""
    def __init__(self, collection_name: str = "structure_chunks"):
        self.collection_name = collection_name

    def retrieve(self, query: str, region: Optional[str] = None, top_k: int = 10) -> List[Dict]:
        start_time = time.perf_counter()
        query_emb = get_embedding(query)
        
        query_filter = None
        if region:
            query_filter = Filter(
                must=[FieldCondition(key="region", match=MatchValue(value=region))]
            )
            
        points = qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_emb,
            query_filter=query_filter,
            limit=top_k
        ).points
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        results = []
        for rank, p in enumerate(points, start=1):
            results.append({
                "rank": rank,
                "chunk_id": p.payload.get("chunk_id", ""),
                "score": float(p.score),
                "policy_id": p.payload.get("policy_id", "UNKNOWN"),
                "region": p.payload.get("region", "UNKNOWN"),
                "effective_date": p.payload.get("effective_date", "UNKNOWN"),
                "source_file": p.payload.get("source_file", "UNKNOWN"),
                "text": p.payload.get("text", ""),
                "latency_ms": elapsed_ms
            })
        return results

class BM25Retriever:
    """Lexical keyword retriever over indexed chunk payloads with pagination and lifecycle support."""
    def __init__(self, collection_name: str = "structure_chunks"):
        self.collection_name = collection_name
        self.points = []
        self.corpus_texts = []
        self.payloads = []
        self.bm25 = None
        self.refresh_index()

    def refresh_index(self):
        """
        Scrolls all points from Qdrant using pagination (cursor-based) to guarantee
        full corpus indexing regardless of collection size, then builds the BM25 inverted index.
        """
        all_records = []
        offset = None
        while True:
            records, next_offset = qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            all_records.extend(records)
            if next_offset is None:
                break
            offset = next_offset

        self.points = all_records
        self.corpus_texts = [
            f"Policy: {p.payload.get('policy_id', '')} | Region: {p.payload.get('region', '')} | File: {p.payload.get('source_file', '')}\n{p.payload.get('text', '')}"
            for p in self.points
        ]
        self.payloads = [p.payload for p in self.points]
        tokenized_corpus = [tokenize(doc) for doc in self.corpus_texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query: str, region: Optional[str] = None, top_k: int = 10) -> List[Dict]:
        start_time = time.perf_counter()
        tokens = tokenize(query)
        scores = self.bm25.get_scores(tokens)

        # Apply region filtering if specified to eliminate cross-region candidate bleeding
        candidate_indices = list(range(len(scores)))
        if region:
            candidate_indices = [
                i for i in candidate_indices
                if self.payloads[i].get("region", "").upper() == region.upper()
            ]

        top_indices = sorted(candidate_indices, key=lambda i: scores[i], reverse=True)[:top_k]
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        results = []
        for rank, idx in enumerate(top_indices, start=1):
            payload = self.payloads[idx]
            results.append({
                "rank": rank,
                "chunk_id": payload.get("chunk_id", ""),
                "score": float(scores[idx]),
                "policy_id": payload.get("policy_id", "UNKNOWN"),
                "region": payload.get("region", "UNKNOWN"),
                "effective_date": payload.get("effective_date", "UNKNOWN"),
                "source_file": payload.get("source_file", "UNKNOWN"),
                "text": payload.get("text", ""),
                "latency_ms": elapsed_ms
            })
        return results

class HybridRetriever:
    """
    Hybrid Retriever fusing Dense Semantic Retrieval and Lexical BM25
    using Reciprocal Rank Fusion (RRF, k=60).
    """
    def __init__(self, collection_name: str = "structure_chunks"):
        self.dense = DenseRetriever(collection_name=collection_name)
        self.bm25 = BM25Retriever(collection_name=collection_name)

    def retrieve(
        self,
        query: str,
        region: Optional[str] = None,
        top_dense: int = 10,
        top_bm25: int = 10,
        k: int = 60,
        top_n: int = 3
    ) -> List[Dict]:
        start_time = time.perf_counter()
        
        dense_results = self.dense.retrieve(query=query, region=region, top_k=top_dense)
        bm25_results = self.bm25.retrieve(query=query, region=region, top_k=top_bm25)

        rrf_scores = {}
        payload_map = {}

        # 1. Accumulate Dense RRF ranks
        for rank, item in enumerate(dense_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            payload_map[cid] = item

        # 2. Accumulate BM25 RRF ranks
        for rank, item in enumerate(bm25_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            if cid not in payload_map:
                payload_map[cid] = item

        # 3. Sort by fused RRF score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        final_results = []
        for final_rank, (cid, fused_score) in enumerate(sorted_candidates[:top_n], start=1):
            item_data = dict(payload_map[cid])
            item_data["rank"] = final_rank
            item_data["score"] = float(fused_score)
            item_data["rrf_score"] = float(fused_score)
            item_data["latency_ms"] = elapsed_ms
            final_results.append(item_data)

        return final_results
