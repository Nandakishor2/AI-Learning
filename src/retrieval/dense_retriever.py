from typing import List, Dict, Optional
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.config import get_gemini_client, get_qdrant_client, EMBEDDING_MODEL, STRUCTURE_COLLECTION

class DenseRetriever:
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION):
        self.collection_name = collection_name
        self.gemini_client = get_gemini_client()
        self.qdrant_client = get_qdrant_client()

    def get_embedding(self, text: str) -> List[float]:
        response = self.gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values

    def retrieve(self, query: str, region: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """
        Executes dense cosine similarity search on Qdrant with optional region metadata filtering.
        """
        query_emb = self.get_embedding(query)
        
        query_filter = None
        if region:
            query_filter = Filter(
                must=[FieldCondition(key="region", match=MatchValue(value=region))]
            )

        points = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_emb,
            query_filter=query_filter,
            limit=top_k
        ).points

        results = []
        for rank, p in enumerate(points, start=1):
            payload = p.payload or {}
            results.append({
                "rank": rank,
                "chunk_id": payload.get("chunk_id", ""),
                "score": float(p.score),
                "policy_id": payload.get("policy_id", "UNKNOWN"),
                "section": payload.get("section", "UNKNOWN"),
                "region": payload.get("region", "UNKNOWN"),
                "effective_date": payload.get("effective_date", "UNKNOWN"),
                "source_file": payload.get("source_file", "UNKNOWN"),
                "text": payload.get("text", "")
            })
        return results
