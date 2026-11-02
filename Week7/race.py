import os
import sys
import csv
import numpy as np
from pathlib import Path

# Ensure root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week7.agent import HRAgentLoop
from Week7.workflow import FixedHRWorkflow

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
    print("="*80)
    print("RUNNING WEEK 7 RACE: AGENT LOOP VS. FIXED WORKFLOW (10 EMPLOYEE QUESTIONS)")
    print("="*80)

    agent = HRAgentLoop()
    workflow = FixedHRWorkflow()

    agent_results = []
    wf_results = []

    for idx, tc in enumerate(TEST_CASES, start=1):
        emp_id = tc["emp_id"]
        q = tc["q"]

        # Run Agent
        res_a = agent.run(emp_id, q)
        agent_results.append(res_a)

        # Run Fixed Workflow
        res_w = workflow.run(emp_id, q)
        wf_results.append(res_w)

        print(f"[{idx:02d}/10] {emp_id} | Agent: {res_a['latency_ms']:.2f}ms ({res_a['total_tokens']} tok) | Workflow: {res_w['latency_ms']:.2f}ms ({res_w['total_tokens']} tok)")

    # Compute Aggregate Metrics
    agent_pass_rate = sum(1 for r in agent_results if r["status"] == "COMPLETED") / len(TEST_CASES) * 100.0
    wf_pass_rate = sum(1 for r in wf_results if r["status"] == "COMPLETED") / len(TEST_CASES) * 100.0

    agent_p50_lat = float(np.percentile([r["latency_ms"] for r in agent_results], 50))
    wf_p50_lat = float(np.percentile([r["latency_ms"] for r in wf_results], 50))

    agent_tot_tokens = sum(r["total_tokens"] for r in agent_results)
    wf_tot_tokens = sum(r["total_tokens"] for r in wf_results)

    agent_avg_cost = sum(r["total_cost"] for r in agent_results) / len(TEST_CASES)
    wf_avg_cost = sum(r["total_cost"] for r in wf_results) / len(TEST_CASES)

    print("\n" + "="*80)
    print("RACE RESULTS SUMMARY (8 METRICS)")
    print("="*80)
    print(f"Agent Loop     -> Pass Rate: {agent_pass_rate:.1f}%, p50 Latency: {agent_p50_lat:.2f}ms, Total Tokens: {agent_tot_tokens}, Cost/Q: ${agent_avg_cost:.6f}")
    print(f"Fixed Workflow -> Pass Rate: {wf_pass_rate:.1f}%, p50 Latency: {wf_p50_lat:.2f}ms, Total Tokens: {wf_tot_tokens}, Cost/Q: ${wf_avg_cost:.6f}")

    # Write race.csv
    csv_path = Path(__file__).resolve().parent / "race.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["System", "Pass_Rate_Pct", "P50_Latency_ms", "Total_Tokens", "Cost_Per_Question_USD"])
        writer.writerow(["HRAgentLoop", f"{agent_pass_rate:.1f}", f"{agent_p50_lat:.2f}", agent_tot_tokens, f"{agent_avg_cost:.6f}"])
        writer.writerow(["FixedHRWorkflow", f"{wf_pass_rate:.1f}", f"{wf_p50_lat:.2f}", wf_tot_tokens, f"{wf_avg_cost:.6f}"])

    print(f"\nSaved race metrics to {csv_path}")

    # Budget Termination Demonstration
    print("\n" + "="*80)
    print("DEMONSTRATING BUDGET-TRIGGERED TERMINATION (Max Iterations = 1)")
    print("="*80)
    tight_agent = HRAgentLoop(max_iterations=1)
    budget_res = tight_agent.run("EMP-1001", "What is my carry over cap?")
    print(f"Status: {budget_res['status']}")
    print(f"Error Message: {budget_res['error_msg']}")
    print(f"Answer: {budget_res['final_answer']}")

    return {
        "agent_pass_rate": agent_pass_rate,
        "wf_pass_rate": wf_pass_rate,
        "agent_p50_lat": agent_p50_lat,
        "wf_p50_lat": wf_p50_lat,
        "agent_tot_tokens": agent_tot_tokens,
        "wf_tot_tokens": wf_tot_tokens,
        "agent_avg_cost": agent_avg_cost,
        "wf_avg_cost": wf_avg_cost,
        "budget_res": budget_res
    }

if __name__ == "__main__":
    run_race()
