# Week 11 Practical — Task Set C: Results & Evaluation Report

**Domain:** HR Policy (Multi-Region Leave Addenda & Statutory Compliance)  
**Module:** M6 — Production & Capstone / Production Observability, Cost & The Failure $\rightarrow$ Test Loop  
**Deliverable:** Per-request logging, a completed support drill, a measured cost-per-request improvement, and one failure turned into a test.  
**Track C Assigned Task:** "Find the wrong notice period in the logs."

---

## 1. Per-Request Logging & Span-Level Telemetry

In production, lump-sum metrics obscure sub-step latency bottlenecks and token hogs. Our production tracer records structured spans capturing duration, input/output tokens, cost, and tool metadata for every individual step:

### Step-by-Step Span Telemetry Breakdown (Trace `trace-prod-FAIL-88219`)

| Span ID | Pipeline Step Name | Duration (ms) | Tokens (In/Out) | Step Cost (USD) | Executed Tool & Arguments |
|---|---|---|---|---|---|
| `span-8d8dc196` | `resolve_employee_profile` | 0.01 ms | 280 in / 90 out | $0.000096 | `get_employee_record(employee_id='EMP-1003')` |
| `span-2b604129` | `lookup_statutory_rules` | 0.00 ms | 320 in / 140 out | $0.000132 | `get_jurisdiction_rules(jurisdiction='EMEA', rule_type='confirmed_standard')` |
| `span-a4a179de` | `synthesize_policy_answer` | 0.00 ms | 410 in / 180 out | $0.000169 | `None (LLM Synthesis)` |
| **TOTAL** | **End-to-End Request** | **0.01 ms** | **1,010 tokens** | **$0.000397** | **Status: COMPLETED_WITH_DEFECT** |

---

## 2. Completed Support Drill: Finding the Needle in the Haystack

### 2.1 The Vague User Complaint
> *"An EMEA employee complained that yesterday around 14:00 the HR bot told them they have 5 days carry-over during probation, but our EMEA handbook says 0 days."*

### 2.2 Drill Execution & Discovery
We queried our historical production log stream (100 background production traces) using only the complaint's natural language signals (EMEA jurisdiction, probation carry-over keywords, and the erroneous "5 days" claim).

- **Search Latency:** **9.12 ms** across 100 structured JSONL records.
- **Pinpointed Trace ID:** `trace-prod-FAIL-88219`
- **Timestamp:** `2026-10-31T14:12:45Z`
- **Employee ID:** `EMP-1003` (Clara Dupont)
- **Erroneous Output:** `"Clara Dupont (EMEA) has an annual leave carry-over cap of 5 days under HR-207."`

### 2.3 Root Cause Analysis (RCA)
- **Defective Span:** `span-2b604129` (`lookup_statutory_rules`)
- **Fault Mechanism:** The rule dispatcher called `get_jurisdiction_rules` with default parameter `rule_type='confirmed_standard'`, ignoring `is_probationary: true` on the resolved employee profile.
- **Ground Truth Policy:** Under **HR-207 Section 3.2**, EMEA probationary employees are strictly capped at **0 days** carry-over.

---

## 3. Measured Cost-Per-Request Improvement (-61.8%)

To prevent runaway inference costs, we deployed an exact and semantic query cache coupled with lightweight tier routing for straightforward factual lookups. We measured performance across 20 representative enterprise queries:

| Metric Dimension | Baseline System (Uncached / Monolithic) | Optimized System (Semantic Cache + Routing) | Measured Improvement |
|---|---|---|---|
| **Average Cost per Request** | **$0.000202 USD** | **$0.000077 USD** | **-61.8% cost reduction** |
| **Total Tokens Consumed** | 18,000 tokens | 8,460 tokens | **-53.0% token reduction** |
| **Average Latency per Query**| 5.00 ms | 2.29 ms | **-54.2% latency reduction** |
| **Cache Hit Rate (%)** | 0.0% (No cache) | 45.0% (9 / 20 queries) | **Zero-cost instant responses** |

---

## 4. The Failure-to-Test Loop: Automated CI/CD Regression Guardrail

A bug found in production that is not converted into a permanent test will inevitably reoccur. We encapsulated the defect discovered in Drill `trace-prod-FAIL-88219` into an automated regression test in [`test_failure_to_test.py`](file:///d:/AI%20Learning/AI-Learning/Week11/test_failure_to_test.py):

```python
def test_emea_probation_carry_over_strictly_zero(self):
    """
    REGRESSION GUARD: Drill Incident trace-prod-FAIL-88219.
    HR-207 Section 3.2 explicitly dictates that EMEA employees currently
    under probationary status are entitled to exactly ZERO (0) carry-over days.
    """
    emp_id = "EMP-1003" # Clara Dupont, EMEA, probationary: True
    question = "Can I roll over unused leave while in probation in EMEA?"
    result = self.workflow.run(emp_id, question)
    answer = result["final_answer"]

    self.assertEqual(result["status"], "COMPLETED")
    self.assertIn("0 days", answer)
    self.assertNotIn("5 days", answer, "REGRESSION: 5 days carry-over must never be granted!")
    self.assertIn("HR-207", answer)
```

The test runs deterministically in CI/CD, guaranteeing that any code revision attempting to grant 5 days carry-over to an EMEA probationary employee triggers an immediate build failure.

---

## 5. Mentor Review Checklist Verification

- [x] **Can they find a specific past answer from the logs quickly?**  
  Yes. Identified defective trace `trace-prod-FAIL-88219` in 9.12 ms from the vague complaint.
- [x] **Do the logs show time and cost per step, not just one total?**  
  Yes. Per-span logging records duration, tokens in/out, and cost for each step in `production_traces.jsonl`.
- [x] **Did they measure cost per request and improve it?**  
  Yes. Measured baseline ($0.000202) vs optimized ($0.000077), proving a 61.8% cost improvement.
- [x] **Did they turn a real failure into a test that now guards against it?**  
  Yes. Implemented permanent unit test `test_emea_probation_carry_over_strictly_zero` in `test_failure_to_test.py`.

