import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from src.config import (
    get_gemini_client,
    GENERATION_MODEL,
    SYSTEM_INSTRUCTION,
    STRUCTURE_COLLECTION,
)
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.generation.citation_validator import CitationValidator

REFUSAL_STRING = "I don't have enough information in the provided HR policy documents to answer that."

@dataclass
class RAGResponse:
    status: str
    answer: str
    citations: List[Dict]
    retrieved_chunks: List[Dict]
    latency_ms: float
    raw_output: str

    def to_dict(self) -> Dict:
        return {
            "status": self.status,
            "answer": self.answer,
            "citations": self.citations,
            "retrieved_chunks": [
                {
                    "rank": c.get("rank"),
                    "chunk_id": c.get("chunk_id"),
                    "score": c.get("score"),
                    "policy_id": c.get("policy_id"),
                    "section": c.get("section"),
                    "region": c.get("region"),
                    "source_file": c.get("source_file"),
                }
                for c in self.retrieved_chunks
            ],
            "latency_ms": self.latency_ms,
            "raw_output": self.raw_output
        }

class RAGPipeline:
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION, use_hybrid: bool = False):
        self.collection_name = collection_name
        self.use_hybrid = use_hybrid
        self.gemini_client = get_gemini_client()
        self.dense_retriever = DenseRetriever(collection_name=collection_name)
        self.hybrid_retriever = HybridRetriever(collection_name=collection_name)
        self.citation_validator = CitationValidator(collection_name=collection_name)

    def retrieve(self, question: str, region: Optional[str] = None, top_k: int = 4) -> List[Dict]:
        if self.use_hybrid:
            return self.hybrid_retriever.retrieve(query=question, region=region, top_n=top_k)
        return self.dense_retriever.retrieve(query=question, region=region, top_k=top_k)

    def generate_answer(
        self,
        question: str,
        region: Optional[str] = None,
        top_k: int = 4,
        similarity_threshold: float = 0.40
    ) -> RAGResponse:
        start_time = time.perf_counter()
        retrieved = self.retrieve(question, region=region, top_k=top_k)

        # Refusal check: if top retrieved score is too low or empty
        if not retrieved or (not self.use_hybrid and retrieved[0]["score"] < similarity_threshold):
            latency = (time.perf_counter() - start_time) * 1000.0
            return RAGResponse(
                status="refused",
                answer=REFUSAL_STRING,
                citations=[],
                retrieved_chunks=retrieved,
                latency_ms=latency,
                raw_output="[AUTO_REFUSAL: Low similarity / no supporting context]"
            )

        # Build grounded context snippet
        context_snippets = []
        for c in retrieved:
            context_snippets.append(
                f"### Context Chunk [{c['chunk_id']}]\n"
                f"Source File: {c['source_file']} | Policy: {c['policy_id']} | Section: {c['section']} | Region: {c['region']} | Effective: {c['effective_date']}\n"
                f"Content:\n{c['text']}"
            )
        context_block = "\n\n---\n\n".join(context_snippets)

        prompt = f"""CONTEXT POLICY DOCUMENTS:
{context_block}

USER QUESTION:
{question}

Please answer the user question using ONLY the facts in the context policy documents above.
Attach the exact citation tag for every statement using:
[Citation: chunk_id=<chunk_id>, policy_id=<policy_id>, section=<section>, source_file=<source_file>]
If the context does not contain the answer, respond ONLY with:
"{REFUSAL_STRING}"
"""

        response = self.gemini_client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": 0.0
            }
        )

        raw_text = response.text.strip()
        latency = (time.perf_counter() - start_time) * 1000.0

        # Check if the model explicitly refused
        if (
            REFUSAL_STRING.lower() in raw_text.lower()
            or "don't have enough information" in raw_text.lower()
            or "do not have sufficient information" in raw_text.lower()
            or "not mentioned" in raw_text.lower()
            or "does not provide" in raw_text.lower()
        ):
            return RAGResponse(
                status="refused",
                answer=REFUSAL_STRING,
                citations=[],
                retrieved_chunks=retrieved,
                latency_ms=latency,
                raw_output=raw_text
            )

        # Extract citations
        citations = self.citation_validator.parse_citations_from_text(raw_text)
        
        # If citations were not extracted via regex tag, build from top retrieved supporting chunks
        if not citations and retrieved:
            top_chunk = retrieved[0]
            citations.append({
                "chunk_id": top_chunk["chunk_id"],
                "policy_id": top_chunk["policy_id"],
                "section": top_chunk["section"],
                "source_file": top_chunk["source_file"]
            })

        # Validate citations
        val_res = self.citation_validator.validate_citations(citations, answer_text=raw_text)
        if not val_res.is_valid and val_res.invalid_citations > 0:
            # If citations point to non-existent data, refuse rather than claiming answered
            return RAGResponse(
                status="refused",
                answer=REFUSAL_STRING,
                citations=[],
                retrieved_chunks=retrieved,
                latency_ms=latency,
                raw_output=raw_text
            )

        return RAGResponse(
            status="answered",
            answer=raw_text,
            citations=citations,
            retrieved_chunks=retrieved,
            latency_ms=latency,
            raw_output=raw_text
        )
