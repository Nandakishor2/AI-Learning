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

def get_embedding(text: str) -> list[float]:
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
    )
    return response.embeddings[0].values

BENCHMARK_QUESTIONS = [
    {"id": "Q1", "question": "What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?", "expected_policy": "HR-207", "expected_section": "3.2", "region": "APAC"},
    {"id": "Q2", "question": "What is the carry-over cap for Tier 2 Leads during probation in APAC?", "expected_policy": "HR-207", "expected_section": "3.2", "region": "APAC"},
    {"id": "Q3", "question": "Are unconfirmed probationary employees allowed to roll over leave in EMEA?", "expected_policy": "HR-207", "expected_section": "3.2", "region": "EMEA"},
    {"id": "Q4", "question": "What is the paid leave duration for a primary caregiver with 24 months of service in North America?", "expected_policy": "HR-208", "expected_section": "2.1", "region": "NA"},
    {"id": "Q5", "question": "How many weeks of paid leave does a Category A primary caregiver receive in LATAM?", "expected_policy": "HR-208", "expected_section": "2.1", "region": "LATAM"},
    {"id": "Q6", "question": "What documentation is required for medical absences exceeding 8 days in the UK?", "expected_policy": "HR-209", "expected_section": "2.1", "region": "UK"},
    {"id": "Q7", "question": "How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM?", "expected_policy": "HR-208", "expected_section": "2.2", "region": "LATAM"},
    {"id": "Q8", "question": "What is the Carer's Conversion Cap for Year 2+ employees in ANZ?", "expected_policy": "HR-209", "expected_section": "2.1", "region": "ANZ"},
]

def evaluate_hit_rate(collection_name: str, strategy_name: str):
    hits = 0
    records = []
    
    for item in BENCHMARK_QUESTIONS:
        query_emb = get_embedding(item["question"])
        results = qdrant_client.query_points(
            collection_name=collection_name,
            query=query_emb,
            limit=5
        ).points
        
        hit = False
        top1_policy = results[0].payload.get("policy_id") if results else "None"
        
        for point in results:
            doc_text = point.payload.get("text", "")
            meta_policy = point.payload.get("policy_id")
            meta_region = point.payload.get("region")
            
            if meta_policy == item["expected_policy"] and (item["expected_section"] in doc_text or item["region"] == meta_region):
                hit = True
                break
                
        if hit:
            hits += 1
        records.append((item["id"], hit, top1_policy))
        
    print(f"\n--- {strategy_name} Hit-in-Top-5: {hits}/{len(BENCHMARK_QUESTIONS)} ---")
    for q_id, hit_status, top1 in records:
        print(f"  [{'HIT' if hit_status else 'MISS'}] {q_id} -> Top-1 Policy: {top1}")
    return hits, records

def run_metadata_filter_demo():
    query = "What is the carry-over cap for probationary employees?"
    print("\n" + "="*50)
    print("METADATA FILTER DEMONSTRATION")
    print(f"Query: '{query}'\n")
    
    query_emb = get_embedding(query)
    
    # 1. Unfiltered Query
    unfiltered = qdrant_client.query_points(
        collection_name="structure_chunks",
        query=query_emb,
        limit=3
    ).points
    
    print("--- UNFILTERED SEARCH RESULTS ---")
    for i, p in enumerate(unfiltered):
        print(f"Rank {i+1} [Score: {p.score:.4f}] Region: {p.payload.get('region')} | Policy: {p.payload.get('policy_id')}")
        print(f"Snippet: {p.payload.get('text', '')[:110]}...\n")
        
    # 2. Filtered Query (region == 'EMEA')
    filtered = qdrant_client.query_points(
        collection_name="structure_chunks",
        query=query_emb,
        query_filter=Filter(
            must=[FieldCondition(key="region", match=MatchValue(value="EMEA"))]
        ),
        limit=3
    ).points
    
    print("--- FILTERED SEARCH RESULTS (region == 'EMEA') ---")
    for i, p in enumerate(filtered):
        print(f"Rank {i+1} [Score: {p.score:.4f}] Region: {p.payload.get('region')} | Policy: {p.payload.get('policy_id')}")
        print(f"Snippet: {p.payload.get('text', '')[:110]}...\n")

if __name__ == "__main__":
    evaluate_hit_rate("baseline_chunks", "Baseline Chunker")
    evaluate_hit_rate("structure_chunks", "Structure-Aware Chunker")
    run_metadata_filter_demo()