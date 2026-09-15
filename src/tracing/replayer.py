from typing import Dict, Tuple
from src.config import get_gemini_client, get_qdrant_client, STRUCTURE_COLLECTION, SYSTEM_INSTRUCTION
from src.generation.rag_pipeline import REFUSAL_STRING

class TraceReplayer:
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION):
        self.collection_name = collection_name
        self.gemini_client = get_gemini_client()
        self.qdrant_client = get_qdrant_client()
        
        # Load chunk index
        records, _ = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=500,
            with_payload=True,
            with_vectors=False
        )
        self.chunk_index = {p.payload.get("chunk_id"): p.payload for p in records}

    def replay_trace(self, trace: Dict) -> Dict:
        """
        Deterministically replays a request using only the information available in the trace.
        """
        question = trace["question"]
        retrieved_ids = [c["chunk_id"] for c in trace.get("retrieved_chunks", [])]
        
        context_snippets = []
        for cid in retrieved_ids:
            chunk = self.chunk_index.get(cid)
            if chunk:
                context_snippets.append(
                    f"### Context Chunk [{chunk.get('chunk_id')}]\n"
                    f"Source File: {chunk.get('source_file')} | Policy: {chunk.get('policy_id')} | Section: {chunk.get('section')} | Region: {chunk.get('region')} | Effective: {chunk.get('effective_date')}\n"
                    f"Content:\n{chunk.get('text')}"
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

        model_params = trace.get("model_parameters", {})
        temp = model_params.get("temperature", 0.0)

        response = self.gemini_client.models.generate_content(
            model=trace.get("model", "gemini-2.5-flash"),
            contents=prompt,
            config={
                "system_instruction": SYSTEM_INSTRUCTION,
                "temperature": temp
            }
        )

        replayed_raw = response.text.strip()
        replayed_status = "refused" if (REFUSAL_STRING.lower() in replayed_raw.lower() or "not mentioned" in replayed_raw.lower()) else "answered"
        
        return {
            "trace_id": trace["trace_id"],
            "original_output": trace.get("final_output", ""),
            "original_status": trace.get("status", ""),
            "replayed_output": replayed_raw,
            "replayed_status": replayed_status,
            "is_identical": (trace.get("final_output", "").strip() == replayed_raw.strip())
        }
