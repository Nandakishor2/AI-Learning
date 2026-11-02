"""
single_agent.py
Single Monolithic HR Policy Agent (Baseline).
Handles employee verification and policy statutory lookup within a single agent context.
"""

import time
from typing import Dict, Any
from Week7.tools import get_employee_record, get_jurisdiction_rules

PRICE_PER_1K_TOKENS = 0.00015

class SingleHRAgent:
    """Monolithic single-agent baseline."""

    def __init__(self, name: str = "SingleHRAgent"):
        self.name = name

    def run(self, emp_id: str, question: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        
        # Step 1: Employee record lookup
        # Tokens: System prompt (300) + query (50) + tool definition (150) = 500
        step1_tokens = 500
        emp_rec = get_employee_record(emp_id)
        if "error" in emp_rec:
            latency = (time.perf_counter() - start_time) * 1000.0
            return {
                "system": "SingleHRAgent",
                "status": "FAILED",
                "answer": f"Employee {emp_id} not found.",
                "latency_ms": latency,
                "total_tokens": step1_tokens,
                "cost_usd": (step1_tokens / 1000.0) * PRICE_PER_1K_TOKENS
            }

        # Step 2: Jurisdiction rules lookup
        # Context accumulates: 500 + tool result (150) + step 2 prompt = 850
        step2_tokens = 350
        rules = get_jurisdiction_rules(emp_rec["jurisdiction"])

        # Step 3: Synthesis
        # Synthesis tokens = 300
        step3_tokens = 300
        total_tokens = step1_tokens + step2_tokens + step3_tokens

        tier = emp_rec["tier"]
        jurisdiction = emp_rec["jurisdiction"]
        is_prob = emp_rec["is_probationary"]

        if jurisdiction == "APAC":
            cap = rules["probation_carry_over_cap"].get(tier, rules["confirmed_carry_over_cap"]) if is_prob else rules["confirmed_carry_over_cap"]
            answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) has an annual leave carry-over cap of {cap} days under {rules['policy_id']}."
        elif jurisdiction == "EMEA":
            cap = rules["probation_carry_over_cap"].get(tier, 0) if is_prob else rules["confirmed_carry_over_cap"]
            answer = f"{emp_rec['name']} ({jurisdiction}) has a carry-over cap of {cap} days under {rules['policy_id']}."
        elif jurisdiction == "LATAM":
            wks = rules["caregiver_paid_weeks"].get(tier, 6)
            answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) is entitled to {wks} weeks of paid caregiver leave under {rules['policy_id']}."
        elif jurisdiction == "NA":
            wks = rules["primary_caregiver_weeks"].get(tier, 8)
            answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) is entitled to {wks} weeks of paid primary caregiver leave under {rules['policy_id']}."
        elif jurisdiction == "ANZ":
            cap = rules["carer_conversion_cap"].get(tier, 5)
            answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) has a Carer's Conversion Cap of {cap} days under {rules['policy_id']}."
        elif jurisdiction == "UK":
            threshold = rules["medical_absence_fit_note_threshold_days"]
            answer = f"{emp_rec['name']} ({jurisdiction}) requires a GP Fit Note for medical absences exceeding {threshold} days under {rules['policy_id']}."
        else:
            answer = f"Resolved rules for {jurisdiction}."

        latency = (time.perf_counter() - start_time) * 1000.0
        cost = (total_tokens / 1000.0) * PRICE_PER_1K_TOKENS

        return {
            "system": "SingleHRAgent",
            "status": "COMPLETED",
            "answer": answer,
            "latency_ms": latency,
            "total_tokens": total_tokens,
            "cost_usd": cost
        }

