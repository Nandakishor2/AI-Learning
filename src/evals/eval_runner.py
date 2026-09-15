import json
from collections import defaultdict
from typing import Dict, List
from src.config import get_qdrant_client, STRUCTURE_COLLECTION
from src.evals.dataset import get_eval_cases
from src.evals.deterministic_assertions import run_deterministic_assertions
from src.evals.judge import LLMJudge
from src.generation.rag_pipeline import RAGPipeline

def run_evaluation_suite(judge_version: str = "v2", use_hybrid: bool = True) -> Dict:
    """
    Executes the full evaluation suite over all 25+ cases:
    - Executes end-to-end RAG pipeline
    - Evaluates deterministic assertions
    - Executes LLM Judge
    - Aggregates pass rates overall and by taxonomy mode
    """
    cases = get_eval_cases()
    pipeline = RAGPipeline(collection_name=STRUCTURE_COLLECTION, use_hybrid=use_hybrid)
    judge = LLMJudge(version=judge_version)
    
    qdrant = get_qdrant_client()
    records, _ = qdrant.scroll(collection_name=STRUCTURE_COLLECTION, limit=500, with_payload=True, with_vectors=False)
    chunk_index = {p.payload.get("chunk_id"): p.payload for p in records}

    results = []
    mode_counts = defaultdict(int)
    mode_passes = defaultdict(int)

    total = len(cases)
    total_passed = 0

    print("\n" + "="*80)
    print(f"EVALUATION RUNNER (Cases: {total} | Judge: {judge_version.upper()} | Retriever: {'Hybrid' if use_hybrid else 'Dense'})")
    print("="*80)

    for idx, case in enumerate(cases, start=1):
        cid = case["case_id"]
        q = case["question"]
        mode = case["taxonomy_mode"]
        region = case.get("region")

        mode_counts[mode] += 1

        # 1. Run RAG Pipeline
        rag_res = pipeline.generate_answer(question=q, region=region).to_dict()

        # 2. Run Deterministic Assertions
        assertion_res = run_deterministic_assertions(case, rag_res, chunk_index)

        # 3. Run LLM Judge
        judge_res = judge.evaluate_answer(
            question=q,
            expected_behavior=case["expected_behavior"],
            generated_answer=rag_res["answer"]
        )

        # Final Pass Condition: both deterministic assertions and LLM judge must pass
        overall_pass = assertion_res.passed and (judge_res["judgment"] == 1)
        if overall_pass:
            total_passed += 1
            mode_passes[mode] += 1

        results.append({
            "case_id": cid,
            "question": q,
            "taxonomy_mode": mode,
            "region": region,
            "rag_status": rag_res["status"],
            "rag_answer": rag_res["answer"],
            "assertions_passed": assertion_res.passed,
            "assertion_failures": assertion_res.failures,
            "judge_judgment": judge_res["judgment"],
            "judge_reasoning": judge_res["reasoning"],
            "overall_pass": overall_pass,
            "latency_ms": rag_res["latency_ms"]
        })

        status_str = "PASS" if overall_pass else "FAIL"
        print(f"[{status_str}] {cid} ({mode}): {q[:65]}...")
        if not overall_pass:
            if not assertion_res.passed:
                print(f"      Assertion Failures: {assertion_res.failures}")
            if judge_res["judgment"] == 0:
                print(f"      Judge Reasoning: {judge_res['reasoning']}")

    overall_pass_rate = (total_passed / total) * 100.0

    print("\n" + "="*80)
    print("EVALUATION SUMMARY RESULTS")
    print("="*80)
    print(f"TOTAL CASES : {total}")
    print(f"TOTAL PASS  : {total_passed}")
    print(f"TOTAL FAIL  : {total - total_passed}")
    print(f"PASS RATE   : {overall_pass_rate:.1f}%\n")

    print("PASS RATE BY TAXONOMY MODE:")
    print("-" * 60)
    mode_summary = {}
    for mode, count in sorted(mode_counts.items()):
        passes = mode_passes[mode]
        rate = (passes / count) * 100.0 if count > 0 else 0.0
        mode_summary[mode] = {"total": count, "passed": passes, "pass_rate": rate}
        print(f"  {mode:<40} : {passes}/{count} ({rate:.1f}%)")
    print("-" * 60)

    return {
        "total_cases": total,
        "total_passed": total_passed,
        "total_failed": total - total_passed,
        "overall_pass_rate": overall_pass_rate,
        "mode_summary": mode_summary,
        "results": results
    }

if __name__ == "__main__":
    run_evaluation_suite(judge_version="v2")
