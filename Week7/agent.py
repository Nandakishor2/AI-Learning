import time
from typing import Dict, Any, List
from Week7.tools import get_employee_record, search_handbook, get_jurisdiction_rules

PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.00060

class BudgetExceededException(Exception):
    def __init__(self, budget_name: str, current_val: float, limit_val: float):
        self.budget_name = budget_name
        self.current_val = current_val
        self.limit_val = limit_val
        super().__init__(f"BUDGET EXCEEDED: {budget_name} reached {current_val:.4f} (Limit: {limit_val:.4f})")

class HRAgentLoop:
    def __init__(
        self,
        max_iterations: int = 5,
        max_tokens: int = 2500,
        max_cost: float = 0.05,
        wall_clock_timeout_sec: float = 8.0
    ):
        self.max_iterations = max_iterations
        self.max_tokens = max_tokens
        self.max_cost = max_cost
        self.wall_clock_timeout_sec = wall_clock_timeout_sec

    def run(self, employee_id: str, question: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        iteration = 0
        total_tokens = 0
        total_cost = 0.0
        trajectory = []
        status = "IN_PROGRESS"
        final_answer = ""
        error_msg = ""

        try:
            # Step 1: Tool get_employee_record
            iteration += 1
            step_tokens = 320
            total_tokens += step_tokens
            total_cost += (step_tokens / 1000.0) * PRICE_PER_1K_INPUT_TOKENS
            self._check_budgets(iteration, total_tokens, total_cost, start_time)

            emp_rec = get_employee_record(employee_id)
            trajectory.append({"step": iteration, "tool": "get_employee_record", "args": {"employee_id": employee_id}, "result": emp_rec})

            if "error" in emp_rec:
                final_answer = f"Could not find employee record for {employee_id}."
                status = "COMPLETED"
            else:
                # Step 2: Tool get_jurisdiction_rules
                iteration += 1
                step_tokens = 380
                total_tokens += step_tokens
                total_cost += (step_tokens / 1000.0) * PRICE_PER_1K_INPUT_TOKENS
                self._check_budgets(iteration, total_tokens, total_cost, start_time)

                jurisdiction = emp_rec["jurisdiction"]
                rules = get_jurisdiction_rules(jurisdiction)
                trajectory.append({"step": iteration, "tool": "get_jurisdiction_rules", "args": {"jurisdiction": jurisdiction}, "result": rules})

                # Step 3: Tool search_handbook if needed or compute answer
                iteration += 1
                step_tokens = 450
                total_tokens += step_tokens
                total_cost += (step_tokens / 1000.0) * PRICE_PER_1K_INPUT_TOKENS
                self._check_budgets(iteration, total_tokens, total_cost, start_time)

                tier = emp_rec["tier"]
                is_prob = emp_rec["is_probationary"]

                if jurisdiction == "APAC":
                    cap = rules["probation_carry_over_cap"].get(tier, rules["confirmed_carry_over_cap"]) if is_prob else rules["confirmed_carry_over_cap"]
                    final_answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) has an annual leave carry-over cap of {cap} days under {rules['policy_id']}."
                elif jurisdiction == "EMEA":
                    cap = rules["probation_carry_over_cap"].get(tier, 0) if is_prob else rules["confirmed_carry_over_cap"]
                    final_answer = f"{emp_rec['name']} ({jurisdiction}) has a carry-over cap of {cap} days under {rules['policy_id']}."
                elif jurisdiction == "LATAM":
                    wks = rules["caregiver_paid_weeks"].get(tier, 6)
                    final_answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) is entitled to {wks} weeks of paid caregiver leave under {rules['policy_id']}."
                elif jurisdiction == "NA":
                    wks = rules["primary_caregiver_weeks"].get(tier, 8)
                    final_answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) is entitled to {wks} weeks of paid primary caregiver leave under {rules['policy_id']}."
                elif jurisdiction == "ANZ":
                    cap = rules["carer_conversion_cap"].get(tier, 5)
                    final_answer = f"{emp_rec['name']} ({tier}, {jurisdiction}) has a Carer's Conversion Cap of {cap} days under {rules['policy_id']}."
                elif jurisdiction == "UK":
                    threshold = rules["medical_absence_fit_note_threshold_days"]
                    final_answer = f"{emp_rec['name']} ({jurisdiction}) requires a GP Fit Note for medical absences exceeding {threshold} days under {rules['policy_id']}."
                else:
                    final_answer = f"Policy rules resolved for {jurisdiction}."

                status = "COMPLETED"

        except BudgetExceededException as e:
            status = "TERMINATED_BUDGET"
            error_msg = str(e)
            final_answer = f"Agent terminated early: {error_msg}"

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "employee_id": employee_id,
            "question": question,
            "status": status,
            "final_answer": final_answer,
            "iterations": iteration,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "latency_ms": latency_ms,
            "trajectory": trajectory,
            "error_msg": error_msg
        }

    def _check_budgets(self, iteration: int, total_tokens: int, total_cost: float, start_time: float):
        elapsed = time.perf_counter() - start_time
        if iteration > self.max_iterations:
            raise BudgetExceededException("max_iterations", iteration, self.max_iterations)
        if total_tokens > self.max_tokens:
            raise BudgetExceededException("max_tokens", total_tokens, self.max_tokens)
        if total_cost > self.max_cost:
            raise BudgetExceededException("max_cost", total_cost, self.max_cost)
        if elapsed > self.wall_clock_timeout_sec:
            raise BudgetExceededException("wall_clock_timeout", elapsed, self.wall_clock_timeout_sec)
