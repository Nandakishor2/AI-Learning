from typing import List, Dict, Optional
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.config import STRUCTURE_COLLECTION

class HybridRetriever:
    """
    Hybrid retriever fusing Dense Cosine Retrieval and Tokenized BM25
    using Reciprocal Rank Fusion (RRF, k=60).
    """
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION):
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
        dense_results = self.dense.retrieve(query=query, region=region, top_k=top_dense)
        bm25_results = self.bm25.retrieve(query=query, top_k=top_bm25)

        rrf_scores = {}
        payload_map = {}

        # Accumulate dense ranks
        for rank, item in enumerate(dense_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            payload_map[cid] = item

        # Accumulate BM25 ranks
        for rank, item in enumerate(bm25_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
            if cid not in payload_map:
                payload_map[cid] = item

        # Sort by fused score descending
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        final_results = []
        for final_rank, (cid, fused_score) in enumerate(sorted_candidates[:top_n], start=1):
            item_data = dict(payload_map[cid])
            item_data["rank"] = final_rank
            item_data["score"] = float(fused_score)
            item_data["rrf_score"] = float(fused_score)
            final_results.append(item_data)

        return final_results
