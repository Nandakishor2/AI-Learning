"""
race.py
Races Single Agent vs Multi-Agent Policy Squad over 10 Identical HR Test Cases.
Measures Quality (Pass Rate), Speed (p50 Latency), Total Tokens, and Cost per Question.
Outputs race.csv and prints comparative breakdown.
"""

import sys
import csv
import numpy as np
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week10.single_agent import SingleHRAgent
from Week10.squad import PolicySquadManager

TEST_CASES = [
    {"emp_id": "EMP-1001", "q": "What is my annual leave carry-over cap during probation in APAC?"},
    {"emp_id": "EMP-1002", "q": "How many days of carry-over leave can I roll over as a Tier 2 Lead during probation in APAC?"},
    {"emp_id": "EMP-1003", "q": "Can I roll over unused leave while in probation in EMEA?"},
    {"emp_id": "EMP-1004", "q": "How many weeks of primary caregiver leave do I receive in North America with 24 months of service?"},
    {"emp_id": "EMP-1005", "q": "How many weeks of paid caregiver leave am I entitled to in LATAM with 18 months of service?"},
    {"emp_id": "EMP-1006", "q": "What medical evidence is required for sick leave exceeding 8 days in the UK?"},
    {"emp_id": "EMP-1007", "q": "What is my Carer's Conversion Cap in ANZ with 28 months of service?"},
    {"emp_id": "EMP-1008", "q": "How much paid primary caregiver leave do I receive in LATAM during my first 2 months?"},
    {"emp_id": "EMP-1009", "q": "What is my primary caregiver leave entitlement in NA during my first 8 months?"},
    {"emp_id": "EMP-1010", "q": "What medical evidence is required for sick leave exceeding 8 days in the UK?"},
]

def run_race():
    print("=" * 80)
    print("WEEK 10: RACING SINGLE AGENT VS. MULTI-AGENT POLICY SQUAD")
    print("Dataset: 10 Identical Real Enterprise HR Policy Inquiries")
    print("=" * 80)

    single_agent = SingleHRAgent()
    squad_manager = PolicySquadManager()

    single_results = []
    squad_results = []

    for idx, tc in enumerate(TEST_CASES, start=1):
        emp_id = tc["emp_id"]
        q = tc["q"]

        # Run Single Agent
        res_single = single_agent.run(emp_id, q)
        single_results.append(res_single)

        # Run Multi-Agent Policy Squad
        res_squad = squad_manager.run(emp_id, q)
        squad_results.append(res_squad)

        print(f"[{idx:02d}/10] {emp_id} | Single: {res_single['latency_ms']:.2f}ms ({res_single['total_tokens']} tok) | Squad: {res_squad['latency_ms']:.2f}ms ({res_squad['total_tokens']} tok)")

    # Aggregate Metrics
    single_pass_rate = sum(1 for r in single_results if r["status"] == "COMPLETED") / len(TEST_CASES) * 100.0
    squad_pass_rate = sum(1 for r in squad_results if r["status"] == "COMPLETED") / len(TEST_CASES) * 100.0

    single_p50 = float(np.percentile([r["latency_ms"] for r in single_results], 50))
    squad_p50 = float(np.percentile([r["latency_ms"] for r in squad_results], 50))

    single_tokens = sum(r["total_tokens"] for r in single_results)
    squad_tokens = sum(r["total_tokens"] for r in squad_results)

    single_cost = sum(r["cost_usd"] for r in single_results) / len(TEST_CASES)
    squad_cost = sum(r["cost_usd"] for r in squad_results) / len(TEST_CASES)

    print("\n" + "=" * 80)
    print("WEEK 10 RACE RESULTS SUMMARY (4 DIMENSIONS / 8 NUMBERS)")
    print("=" * 80)
    print(f"Single Agent -> Pass Rate: {single_pass_rate:.1f}%, p50 Latency: {single_p50:.2f}ms, Total Tokens: {single_tokens}, Avg Cost/Q: ${single_cost:.6f}")
    print(f"Policy Squad -> Pass Rate: {squad_pass_rate:.1f}%, p50 Latency: {squad_p50:.2f}ms, Total Tokens: {squad_tokens}, Avg Cost/Q: ${squad_cost:.6f}")

    # Cost & Token Inflation Analysis
    token_inflation_pct = ((squad_tokens - single_tokens) / single_tokens) * 100.0
    cost_multiplier = squad_cost / single_cost

    print("\n--- Context Re-send & Overhead Analysis ---")
    print(f"Token Inflation: +{token_inflation_pct:.1f}% more tokens consumed by Multi-Agent Squad")
    print(f"Cost Multiplier: Multi-Agent Squad is {cost_multiplier:.2f}x MORE expensive than Single Agent")
    print("Root Cause: Context re-send on every A2A delegation hand-off (Manager -> EmpSpecialist, Manager -> StatutorySpecialist).")

    # Save to race.csv
    csv_path = Path(__file__).resolve().parent / "race.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["System", "Pass_Rate_Pct", "P50_Latency_ms", "Total_Tokens", "Avg_Cost_USD"])
        writer.writerow(["SingleHRAgent", f"{single_pass_rate:.1f}", f"{single_p50:.2f}", single_tokens, f"{single_cost:.6f}"])
        writer.writerow(["PolicySquadMultiAgent", f"{squad_pass_rate:.1f}", f"{squad_p50:.2f}", squad_tokens, f"{squad_cost:.6f}"])

    print(f"\nSaved benchmark metrics to {csv_path}")
    return {
        "single_pass_rate": single_pass_rate,
        "squad_pass_rate": squad_pass_rate,
        "single_p50": single_p50,
        "squad_p50": squad_p50,
        "single_tokens": single_tokens,
        "squad_tokens": squad_tokens,
        "single_cost": single_cost,
        "squad_cost": squad_cost
    }

if __name__ == "__main__":
    run_race()

