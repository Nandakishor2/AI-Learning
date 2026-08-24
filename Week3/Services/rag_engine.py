import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
qdrant_client = QdrantClient(url="http://localhost:6333")

SYSTEM_INSTRUCTION = """
You are an AI People Operations Assistant. Your task is to answer employee leave policy questions STRICTLY and SOLELY based on the provided policy context snippets.

STRICT RULES:
1. Cite your sources for every factual assertion using the exact format: [Policy: <policy_id>, Section: <section>, Region: <region>].
2. If the question cannot be directly and fully answered using ONLY the provided context, or if the context does not contain the answer, you MUST refuse gracefully by stating:
   "I do not have sufficient information in the provided leave policy documents to answer this question."
3. Never use outside knowledge or make assumptions beyond the text provided.
"""

def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

def retrieve_context(query: str, region: str = None, top_k: int = 4) -> list[dict]:
    """Retrieve relevant chunks from Qdrant with optional region metadata filtering."""
    query_emb = get_embedding(query)
    
    query_filter = None
    if region:
        query_filter = Filter(
            must=[FieldCondition(key="region", match=MatchValue(value=region))]
        )
        
    points = qdrant_client.query_points(
        collection_name="structure_chunks",
        query=query_emb,
        query_filter=query_filter,
        limit=top_k
    ).points
    
    contexts = []
    for p in points:
        contexts.append({
            "text": p.payload.get("text", ""),
            "policy_id": p.payload.get("policy_id", "UNKNOWN"),
            "region": p.payload.get("region", "UNKNOWN"),
            "effective_date": p.payload.get("effective_date", "UNKNOWN"),
            "source_file": p.payload.get("source_file", "UNKNOWN"),
            "score": p.score
        })
    return contexts

def answer_query(question: str, region: str = None) -> dict:
    """End-to-end RAG pipeline: Retrieve -> Construct Prompt -> Generate with Grounding & Refusal."""
    contexts = retrieve_context(question, region=region, top_k=3)
    
    # Format retrieved contexts into prompt
    context_str = "\n\n---\n\n".join([
        f"Document: {c['source_file']} | Policy: {c['policy_id']} | Region: {c['region']}\n{c['text']}"
        for c in contexts
    ])
    
    prompt = f"""CONTEXT POLICY DOCUMENTS:
{context_str}

USER QUESTION:
{question}
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={"system_instruction": SYSTEM_INSTRUCTION, "temperature": 0.0}
    )
    
    return {
        "question": question,
        "region_filter": region,
        "retrieved_count": len(contexts),
        "top_sources": [(c["policy_id"], c["region"]) for c in contexts],
        "answer": response.text.strip()
    }

if __name__ == "__main__":
    # 1. Grounded Question Test
    q1 = "What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?"
    print("\n" + "="*60)
    print("TEST 1: Grounded Table Question (with APAC region filter)")
    res1 = answer_query(q1, region="APAC")
    print(f"Question: {res1['question']}")
    print(f"Answer:\n{res1['answer']}\n")

    # 2. Refusal Test (Out of domain / Ungrounded question)
    q2 = "What is the company policy on remote work stipends for APAC engineers?"
    print("="*60)
    print("TEST 2: Ungrounded / Out-of-Domain Question (Refusal Test)")
    res2 = answer_query(q2, region="APAC")
    print(f"Question: {res2['question']}")
    print(f"Answer:\n{res2['answer']}\n")