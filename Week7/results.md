# Week 7 Practical — Task Set C: Results & Evaluation Report

**Domain:** HR Policy (Multi-Region Leave Addenda)  
**Module:** M4 — Agents / Agent Loops & Workflows  
**Taskset:** Week 7 Practical — Task Set C  
**Core Objective:** Race an autonomous agent loop against a deterministic fixed workflow over 10 employee entitlement queries, enforce 4 operational budgets, and deliver a data-backed architecture verdict.

---

## 1. Race Benchmark Results (8 Metrics Table)

Both systems evaluated over the exact same 10 employee questions across APAC, EMEA, NA, LATAM, UK, and ANZ jurisdictions.

| Metric Dimension | Autonomous Agent Loop (`HRAgentLoop`) | Deterministic Fixed Workflow (`FixedHRWorkflow`) | Efficiency Delta / Advantage |
|---|---|---|---|
| **1. Pass Rate (%)** | **100.0% (10/10)** | **100.0% (10/10)** | **Parity (0.0% delta)** |
| **2. p50 Latency (ms)** | **0.01 ms** | **0.00 ms** | **Workflow is faster** |
| **3. Total Tokens Consumed** | **11,500 tokens** | **3,100 tokens** | **Workflow saves 73.0% tokens** |
| **4. Average Cost per Question ($)** | **$0.000172 USD** | **$0.000046 USD** | **Workflow is 3.74x cheaper** |

### Benchmark File: [`race.csv`](file:///d:/AI%20Learning/AI-Learning/Week7/race.csv)
```csv
System,Pass_Rate_Pct,P50_Latency_ms,Total_Tokens,Cost_Per_Question_USD
HRAgentLoop,100.0,0.01,11500,0.000172
FixedHRWorkflow,100.0,0.00,3100,0.000046
```

---

## 2. Third Tool Implementation & Diff

We added the third tool `get_jurisdiction_rules` with strict enum typing (`JurisdictionType = Literal["APAC", "EMEA", "LATAM", "NA", "ANZ", "UK"]`) and zero functional overlap with `get_employee_record` or `search_handbook`.

```diff
--- Week7/tools_baseline.py
+++ Week7/tools_with_third_tool.py
@@ -1,15 +1,28 @@
 from typing import Literal, Dict, Any
 
+JurisdictionType = Literal["APAC", "EMEA", "LATAM", "NA", "ANZ", "UK"]
+
 def get_employee_record(employee_id: str) -> Dict[str, Any]:
     """Fetch an employee's employment metadata by ID."""
     ...
 
 def search_handbook(query: str, policy_id: str) -> Dict[str, Any]:
     """Search specific policy handbook text clauses by policy ID."""
     ...
+
+def get_jurisdiction_rules(jurisdiction: JurisdictionType) -> Dict[str, Any]:
+    """
+    Lookup regional leave statutory parameters and threshold rules for a given jurisdiction.
+    Job: Retrieve structured statutory constants and calculation caps for an exact jurisdiction.
+    """
+    if jurisdiction not in JURISDICTION_RULES:
+        return {"error": f"Unknown jurisdiction: {jurisdiction}"}
+    return JURISDICTION_RULES[jurisdiction]
```

---

## 3. Four Budgets Enforced & Termination Log

The agent loop actively monitors four hard operational bounds:
1. `max_iterations = 5`
2. `max_tokens = 2500`
3. `max_cost = $0.05`
4. `wall_clock_timeout_sec = 8.0s`

### Budget Termination Log Excerpt
When `max_iterations` was configured to $1$, the agent aborted cleanly at iteration 2 without looping infinitely:

```plaintext
================================================================================
DEMONSTRATING BUDGET-TRIGGERED TERMINATION (Max Iterations = 1)
================================================================================
Status: TERMINATED_BUDGET
Error Message: BUDGET EXCEEDED: max_iterations reached 2.0000 (Limit: 1.0000)
Answer: Agent terminated early: BUDGET EXCEEDED: max_iterations reached 2.0000 (Limit: 1.0000)
```

---

## 4. Architecture Verdict (<150 Words)

**Verdict:** We deploy the **Deterministic Fixed Workflow**.  
Across all 10 employee entitlement questions, the workflow matched the agent’s 100% accuracy while reducing token consumption by 73.0% (3,100 vs. 11,500 tokens) and slashing cost by 3.74x with sub-millisecond execution. The decision rule states: *use an agent only when the execution path cannot be statically predetermined by input state.* Because HR entitlement determination follows a strictly ordered, three-step dependency chain (read employee $\rightarrow$ fetch regional rules $\rightarrow$ calculate entitlement), dynamic LLM re-planning introduces non-deterministic tool thrash without adding value. An autonomous agent is only warranted for unstructured multi-turn escalation cases involving cross-policy dispute arbitration.
