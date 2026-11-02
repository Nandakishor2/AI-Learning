"""
support_drill.py
Production Support Drill for Track C: "Find the wrong notice period in the logs".
Simulates searching through a high-volume production trace log from a vague user complaint,
pinpoints the exact trace_id, inspects the per-step spans, and outputs an RCA report.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week11.tracer import ProductionTracer, Span

TRACE_LOG_PATH = Path(__file__).resolve().parent / "production_traces.jsonl"

def populate_sample_production_log(tracer: ProductionTracer, count: int = 100):
    """Generates a realistic stream of historical production traces with one planted bug."""
    if TRACE_LOG_PATH.exists():
        TRACE_LOG_PATH.unlink()

    regions = ["APAC", "EMEA", "NA", "LATAM", "UK", "ANZ"]
    
    # 1. Generate 99 valid background traces
    for i in range(1, count):
        reg = regions[i % len(regions)]
        emp_id = f"EMP-{1000 + (i % 10) + 1}"
        
        span1 = Span("resolve_employee_profile").start()
        span1.finish(tokens_in=250, tokens_out=80, tool_called="get_employee_record", 
                     tool_args={"employee_id": emp_id}, tool_result={"jurisdiction": reg, "is_prob": False})
        
        span2 = Span("lookup_statutory_rules").start()
        span2.finish(tokens_in=300, tokens_out=120, tool_called="get_jurisdiction_rules",
                     tool_args={"jurisdiction": reg}, tool_result={"policy_id": "HR-207", "cap": 10})
        
        span3 = Span("synthesize_policy_answer").start()
        span3.finish(tokens_in=350, tokens_out=150, 
                     tool_result={"answer": f"Policy rules for {reg} verified."})

        tracer.record_trace(
            query=f"What is the standard policy rule in {reg}?",
            employee_id=emp_id,
            spans=[span1, span2, span3],
            final_answer=f"Verified statutory entitlement under {reg} guidelines.",
            trace_id=f"trace-prod-{10000 + i}",
            timestamp_iso=f"2026-10-31T{(10 + (i % 8)):02d}:{(i * 7) % 60:02d}:00Z"
        )

    # 2. Plant the defective trace: The wrong notice period / carry-over in EMEA
    # Employee EMP-1003 (Clara Dupont, EMEA, probationary) was told 5 days instead of 0 days!
    bad_span1 = Span("resolve_employee_profile").start()
    bad_span1.finish(tokens_in=280, tokens_out=90, tool_called="get_employee_record",
                     tool_args={"employee_id": "EMP-1003"},
                     tool_result={"name": "Clara Dupont", "jurisdiction": "EMEA", "is_probationary": True})

    bad_span2 = Span("lookup_statutory_rules").start()
    # BUG IN SPAN 2: Evaluator looked up confirmed cap (5 days) rather than probationary cap (0 days)!
    bad_span2.finish(tokens_in=320, tokens_out=140, tool_called="get_jurisdiction_rules",
                     tool_args={"jurisdiction": "EMEA", "rule_type": "confirmed_standard"},
                     tool_result={"policy_id": "HR-207", "cap": 5, "error_flag": "LOOKUP_MISMATCH"})

    bad_span3 = Span("synthesize_policy_answer").start()
    bad_span3.finish(tokens_in=410, tokens_out=180,
                     tool_result={"flawed_answer": "Clara Dupont (EMEA) has an annual leave carry-over cap of 5 days under HR-207."})

    planted_trace_id = "trace-prod-FAIL-88219"
    tracer.record_trace(
        query="Can I roll over unused leave while in probation in EMEA?",
        employee_id="EMP-1003",
        spans=[bad_span1, bad_span2, bad_span3],
        final_answer="Clara Dupont (EMEA) has an annual leave carry-over cap of 5 days under HR-207.",
        status="COMPLETED_WITH_DEFECT",
        trace_id=planted_trace_id,
        timestamp_iso="2026-10-31T14:12:45Z"
    )
    print(f"Generated {count} production traces with planted failure ({planted_trace_id}).")
    return planted_trace_id

def run_support_drill(complaint: str) -> Dict[str, Any]:
    """
    Executes the Support Drill:
    Locates the defective trace from a vague complaint without knowing the trace_id.
    """
    print("=" * 80)
    print("STARTING SUPPORT DRILL: INVESTIGATING COMPLAINT")
    print(f"Vague Complaint: \"{complaint}\"")
    print("=" * 80)

    start_search = time.perf_counter()
    candidates = []

    # Read production traces
    with open(TRACE_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            # Filter criteria derived from complaint: EMEA jurisdiction, probation/carryover/notice, 5 days claim
            txt_blob = (rec["query"] + " " + rec["final_answer"]).lower()
            if "emea" in txt_blob and ("probation" in txt_blob or "roll over" in txt_blob or "carry-over" in txt_blob):
                if "5 days" in rec["final_answer"]:
                    candidates.append(rec)

    search_time_ms = (time.perf_counter() - start_search) * 1000.0
    print(f"Drill Search completed in {search_time_ms:.2f} ms. Found {len(candidates)} candidate trace(s).")

    if not candidates:
        print("ERROR: Defective trace not found!")
        return {}

    bad_trace = candidates[0]
    print("\n--- PINPOINTED DEFECTIVE PRODUCTION TRACE ---")
    print(f"Trace ID:        {bad_trace['trace_id']}")
    print(f"Timestamp:       {bad_trace['timestamp']}")
    print(f"Employee ID:     {bad_trace['employee_id']}")
    print(f"User Query:      \"{bad_trace['query']}\"")
    print(f"Reported Answer: \"{bad_trace['final_answer']}\"")
    print(f"Total Duration:  {bad_trace['total_duration_ms']:.2f} ms")
    print(f"Total Cost:      ${bad_trace['total_cost_usd']:.6f} USD")

    print("\n--- STEP-BY-STEP SPAN TELEMETRY BREAKDOWN ---")
    for s in bad_trace["spans"]:
        print(f"-> Span ID: {s['span_id']} | Step: {s['step_name']:<26} | Dur: {s['duration_ms']:>6.2f}ms | Cost: ${s['step_cost_usd']:.6f} | Tool: {s['tool_called']}")

    # Root Cause Diagnosis
    span2 = bad_trace["spans"][1]
    print("\n" + "=" * 80)
    print("ROOT CAUSE ANALYSIS (RCA)")
    print("=" * 80)
    print(f"Defective Span:  {span2['span_id']} ({span2['step_name']})")
    print(f"Tool Arguments:  {span2['tool_args']}")
    print(f"Fault Mechanism: The retriever called get_jurisdiction_rules with rule_type='confirmed_standard',")
    print(f"                 completely bypassing the 'is_probationary: true' condition in employee record.")
    print(f"Policy Reality:  HR-207 Section 3.2 strictly mandates 0 days carry-over during EMEA probation.")
    print(f"Action Taken:    Quarantined trace ID, patched rule dispatcher, authored regression test.")

    return bad_trace

if __name__ == "__main__":
    tracer = ProductionTracer()
    populate_sample_production_log(tracer, 100)
    complaint_text = "An EMEA employee complained that yesterday around 14:00 the bot told them they have 5 days carry-over during probation, but our EMEA handbook says 0 days."
    run_support_drill(complaint_text)

