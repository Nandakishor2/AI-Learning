# Week 6 Practical — Task Set C: Results & Evaluation Report

**Domain:** HR Policy (Multi-Region Leave Addenda)  
**Module:** M3 — Evals & Error Analysis · THE CORE  
**Taskset:** Week 6 Practical — Task Set C  
**Core Objective:** Offload deterministic criteria to code assertions, validate LLM judge agreement against blind human labels, and calibrate the judge via few-shot disagreement demonstrations.

---

## 1. Evaluation Architecture: Assertion vs. Judge Split

We decomposed the evaluation harness into **4 deterministic Python code assertions** and **1 LLM Judge semantic criterion**.

| Criterion | Implementation Layer | Deterministic Rule / Assertion Logic |
|---|---|---|
| **1. Policy Section Exists & Resolves** | Deterministic Code Assertion | Verifies that cited section numbers resolve to valid headers in the authoritative Qdrant index. |
| **2. Citation Chunk ID Integrity** | Deterministic Code Assertion | Enforces exact chunk ID resolution against the indexed corpus hash table (`chunks_missing_source_file == 0`). |
| **3. Out-of-Jurisdiction Refusal Trigger** | Deterministic Code Assertion | Matches exact standard refusal string on ungrounded inquiries. |
| **4. Numeric Entitlement Presence** | Deterministic Code Assertion | Regex and token parsing to confirm that statutory day/week integers appear in the answer. |
| **5. Semantic Factual Correctness** | LLM Judge (`gemini-2.5-flash`) | Contextual reasoning to evaluate whether the generated response accurately addresses the employee inquiry without hallucination. |

**Summary Metric:**  
- **Deterministic Assertion Count:** **4 criteria**
- **LLM Judged Criteria Count:** **1 criterion**

---

## 2. Blind Human Ground-Truth Labeling (`labels_25.json`)

To prevent evaluation circularity, 25 answers were evaluated blind by a human annotator on a single binary pass/fail criterion ($1 = \text{Pass}, 0 = \text{Fail}$) and committed to disk **before running the LLM judge**.

- **File Name:** `labels_25.json`
- **Total Labeled Cases:** 25 cases across all 4 taxonomy modes
- **Temporal Ordering Proof:** Git commit `ed6ca309b451` / Timestamp `2026-09-15T08:00:00Z` strictly predating the Judge V1 execution run.

---

## 3. Human-Judge Agreement Before vs. After Iteration

| Metric | Judge V1 (Zero-Shot) | Judge V2 (Few-Shot Calibrated) | Empirical Delta |
|---|---|---|---|
| **Human Agreement (%)** | **18/25 (72.0%)** | **24/25 (96.0%)** | **+24.0% (+6 cases aligned)** |
| **Refusal Handling Calibration** | False Failures on Refusals | Calibrated on strict refusal | Correctly scored 5/5 refusals |
| **Sub-Clause Precision** | Penalized omitted general clauses | Evaluated specific target tier | Correctly aligned on probation caps |
| **Judge Prompt Version** | `judge_v1.txt` | `judge_v2.txt` | +2 few-shot disagreement demos |

---

## 4. Deep-Dive on Disagreements: Who Was Right?

### Disagreement Case 1: Refusal on Unindexed Executive Equity Policy
- **Question:** `"Under HR-999 section 1.0, what is the executive equity vesting schedule upon acquisition?"`
- **Generated Answer:** `"I do not have sufficient information in the provided leave policy documents to answer this question."`
- **Human Label:** **1 (PASS)**
- **Judge V1 Label:** **0 (FAIL)**
- **Judge V1 Reasoning:** *"The response failed to provide the requested equity vesting schedule percentages."*
- **Verdict: HUMAN WAS RIGHT.**  
  *Analysis:* HR-999 is an ungrounded out-of-corpus query. Generating equity vesting percentages would represent severe legal hallucination. The assistant obeyed its non-negotiable refusal guardrail, which represents the legally correct behavior.

### Disagreement Case 2: Sub-Clause Tier Extraction vs. Parent Summary
- **Question:** `"What is the carry-over cap for unconfirmed probationary employees in EMEA under HR-207?"`
- **Generated Answer:** `"Under HR-207 EMEA Section 3.2, unconfirmed probationary employees have a carry-over cap of 0 days and are prohibited from rolling over leave."`
- **Human Label:** **1 (PASS)**
- **Judge V1 Label:** **0 (FAIL)**
- **Judge V1 Reasoning:** *"The answer omitted the general 5-day carry-over entitlement expiring June 30th for confirmed employees."*
- **Verdict: HUMAN WAS RIGHT.**  
  *Analysis:* The query specifically asked for probationary employee restrictions under Section 3.2, which mandates 0 days. Demanding mention of confirmed staff caps penalized precise answer conciseness.

---

## 5. Pre-Iteration Prediction & Outcome Verification

### Written Prediction (`prediction.txt`)
```text
Date: 2026-09-15
Planned Change: Incorporating 2 few-shot demonstration examples into Judge V2 prompt to calibrate refusal detection and sub-clause table lookups.
Baseline Agreement: 72.0%
Expected Agreement: >= 96.0%
Success Threshold: Human-Judge agreement reaches at least 92.0%.
```

### Outcome Verification
- **Actual Agreement After:** **96.0% (24/25)**
- **Prediction Verdict:** **CONFIRMED** — Adding few-shot demonstration anchors eliminated Judge V1's false failure classifications on legitimate refusals and granular sub-clause table lookups.

---

## 6. Prompt Diff: `judge_v1.txt` vs. `judge_v2.txt`

```diff
--- Week6/judge_v1.txt
+++ Week6/judge_v2.txt
@@ -7,6 +7,22 @@
 Evaluate ONLY semantic correctness: Does the generated answer accurately provide the policy entitlement or correctly refuse when unsupported?
 
+FEW-SHOT EXAMPLES OF TRICKY EVALUATION CASES:
+Example 1:
+Question: "Under HR-999 section 1.0, what is the executive equity vesting schedule upon acquisition?"
+Expected Behavior: "Must refuse because HR-999 is not in the corpus."
+Generated Answer: "I do not have sufficient information in the provided leave policy documents to answer that."
+Judgment: 1
+Reasoning: "The model correctly and strictly refused to fabricate out-of-corpus policy information."
+
+Example 2:
+Question: "What is the carry-over cap for unconfirmed probationary employees in EMEA under HR-207?"
+Expected Behavior: "Must state 0 days (unconfirmed probationary employees are prohibited from rolling over leave)."
+Generated Answer: "Employees in EMEA can carry over a maximum of 5 days expiring June 30th."
+Judgment: 0
+Reasoning: "The answer quoted the confirmed employee cap (5 days) instead of the probationary restriction (0 days/prohibited)."
+
 NOW EVALUATE THE FOLLOWING:
 QUESTION:
 {question}
```

---

## 7. Single-Command Evaluation Suite: Pass Rate by Taxonomy Mode

Running `python -m evals.run` produces the following deterministic mode breakdown:

```plaintext
====================================================================================================
AI ENGINEERING LEAGUE — EVALUATION SUITE RESULTS SUMMARY (Track C: HR Policy)
====================================================================================================
Taxonomy Mode Breakdown:
----------------------------------------------------------------------------------------------------
  Mode 1: Exact Policy Section Retrieval Lookup       | Total:  6 | Passed:  6 | Pass Rate: 100.0%
  Mode 2: Eligibility Matrix & Tenure Tier Extraction | Total:  7 | Passed:  7 | Pass Rate: 100.0%
  Mode 3: Regional Jurisdiction Disambiguation        | Total:  6 | Passed:  6 | Pass Rate: 100.0%
  Mode 4: Out-of-Corpus Query Handling & Refusal      | Total:  7 | Passed:  7 | Pass Rate: 100.0%
----------------------------------------------------------------------------------------------------
OVERALL SUITE PERFORMANCE:
  Total Evaluation Cases : 26
  Total Passed           : 26
  Total Failed           : 0
  Overall Pass Rate      : 100.0%
====================================================================================================
```

---

## 8. Bonus Challenge: RAGAS Faithfulness vs. Temporal Accuracy

**Query:** `"What is the annual leave carry-over limit for APAC staff?"`
- **Retrieved Chunk (Superseded Policy):** `HR-207_APAC_2023.md` (stating 15 days).
- **Generated Answer:** `"APAC employees may carry over up to 15 days of annual leave [Policy: HR-207-2023, Section: 3.1]."`
- **RAGAS Faithfulness Score:** **0.96 (Near Perfect)**
- **RAGAS Context Precision Score:** **0.92 (High)**
- **Ground-Truth Correctness Score:** **0.0 (FAILED — Legally Incorrect)**

### Insight on Evaluation Averaging
RAGAS Faithfulness measures purely whether the generated answer is supported by the *retrieved context*, not whether the retrieved context is legally active or superseded. A system can be **100% faithful to outdated context while being 100% wrong in reality**. This proves why deterministic version assertions (`assert_effective_date >= 2026-01-01`) must guard the retrieval pipeline before LLM generation.
