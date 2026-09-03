import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient

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

def run_baseline_inspection():
    golden_path = Path(__file__).resolve().parent.parent / "golden_set.jsonl"
    with open(golden_path, "r", encoding="utf-8") as f:
        queries = [json.loads(line) for line in f if line.strip()]

    hits_at_3 = 0
    total_valid = 0
    latencies = []
    
    tally = {"R": 0, "G": 0, "Not-In-Corpus": 0}
    inspection_records = []

    print(f"\n{'='*75}")
    print("BASELINE INSPECTION VIEW (Dense Retrieval - Top 3)")
    print(f"{'='*75}\n")

    for item in queries:
        qid = item["id"]
        qtext = item["question"]
        expected = item["expected_chunk_id"]

        start_t = time.perf_counter()
        query_emb = get_embedding(qtext)
        results = qdrant_client.query_points(
            collection_name="structure_chunks",
            query=query_emb,
            limit=3
        ).points
        latency_ms = (time.perf_counter() - start_t) * 1000.0
        latencies.append(latency_ms)

        retrieved_ids = [p.payload.get("chunk_id") for p in results]
        
        # Determine Hit / Failure category
        if expected == "NOT_IN_CORPUS":
            label = "Not-In-Corpus"
            evidence = f"Query target does not exist in policy corpus; retrieved adjacent chunks: {retrieved_ids[:2]}"
            tally["Not-In-Corpus"] += 1
            hit = False
        elif expected in retrieved_ids:
            label = "HIT"
            evidence = f"Expected chunk {expected} found at rank {retrieved_ids.index(expected) + 1}."
            hit = True
            hits_at_3 += 1
            total_valid += 1
        else:
            # Expected chunk was absent from top-3
            label = "R"
            evidence = f"Expected {expected}, but dense retriever fetched {retrieved_ids}."
            tally["R"] += 1
            hit = False
            total_valid += 1

        inspection_records.append({
            "id": qid,
            "question": qtext,
            "expected": expected,
            "retrieved": retrieved_ids,
            "label": label,
            "evidence": evidence,
            "latency_ms": latency_ms
        })

        status_flag = "[HIT]" if hit else f"[{label}]"
        print(f"{status_flag} {qid}: {qtext}")
        print(f"  Retrieved IDs: {retrieved_ids}")
        print(f"  Evidence: {evidence}\n")

    hit_rate = hits_at_3 / total_valid if total_valid > 0 else 0.0
    p50_latency = np.percentile(latencies, 50)

    print(f"{'='*75}")
    print("BASELINE SUMMARY METRICS")
    print(f"{'='*75}")
    print(f"Baseline Hit-rate@3: {hits_at_3}/{total_valid} ({hit_rate * 100:.1f}%)")
    print(f"Baseline p50 Latency: {p50_latency:.2f} ms")
    print(f"Failure Tally: R={tally['R']} | G={tally['G']} | Not-In-Corpus={tally['Not-In-Corpus']}\n")

    # Dump record for Phase 4 results.md
    with open("baseline_results.json", "w", encoding="utf-8") as out:
        json.dump({
            "hit_rate_at_3": hit_rate,
            "hits": hits_at_3,
            "total_valid": total_valid,
            "p50_latency": p50_latency,
            "tally": tally,
            "records": inspection_records
        }, out, indent=2)

if __name__ == "__main__":
    run_baseline_inspection()