# Evaluation Report: Multi-Region RAG Benchmarks & Q&A

This document summarizes the retrieval benchmark results, chunking comparison, metadata filtering proof, and end-to-end grounded generation outputs for the 6 regional leave policy addenda.

## 1. Ground-Truth Retrieval Benchmark (Hit-in-Top-5)

8 ground-truth operational queries were evaluated across both chunking collections in Qdrant:

| Q# | Question Text | Target Policy | Target Section | Region | Table-Based? | Baseline Hit@5 | Structure Hit@5 | Top-1 Policy |
|---|---|---|---|---|---|---|---|---|
| Q1 | What is the annual leave carry-over cap for Tier 1 probationary staff in APAC? | HR-207 | Section 3.2 | APAC | Yes | HIT | HIT | HR-207 |
| Q2 | What is the carry-over cap for Tier 2 Leads during probation in APAC? | HR-207 | Section 3.2 | APAC | Yes | HIT | HIT | HR-207 |
| Q3 | Are unconfirmed probationary employees allowed to roll over leave in EMEA? | HR-207 | Section 3.2 | EMEA | Yes | HIT | HIT | HR-207 |
| Q4 | What is the paid leave duration for a primary caregiver with 24 months of service in North America? | HR-208 | Section 2.1 | NA | Yes | HIT | HIT | HR-208 |
| Q5 | How many weeks of paid leave does a Category A primary caregiver receive in LATAM? | HR-208 | Section 2.1 | LATAM | Yes | HIT | HIT | HR-208 |
| Q6 | What documentation is required for medical absences exceeding 8 days in the UK? | HR-209 | Section 2.1 | UK | Yes | HIT | HIT | HR-209 |
| Q7 | How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM? | HR-208 | Section 2.2 | LATAM | No | HIT | HIT | HR-208 |
| Q8 | What is the Carer's Conversion Cap for Year 2+ employees in ANZ? | HR-209 | Section 2.1 | ANZ | Yes | HIT | HIT | HR-209 |

### Aggregate Score
- **Baseline Chunker Hit-in-Top-5**: 8/8 (100%)
- **Structure-Aware Chunker Hit-in-Top-5**: 8/8 (100%)

---

## 2. Chunking Strategy Analysis

| Metric / Dimension | Strategy A: Baseline Chunker | Strategy B: Structure-Aware Chunker |
|---|---|---|
| **Total Chunks Produced** | 17 chunks | 26 chunks |
| **Chunking Logic** | Naive sliding window (350 chars, 50 overlap) | Markdown heading hierarchy (#, ##, ###) |
| **Context Preservation** | Heading context lost across boundaries | Top-level document title & section path attached to all chunks |
| **Table Integrity** | Tables can be bisected across chunk limits | Complete markdown table rows remain intact in single chunks |
| **LLM Generation Safety** | High hallucination risk from sliced tables | High grounding confidence from self-contained clauses |

---

## 3. Metadata Filtering Proof

Query: `"What is the carry-over cap for probationary employees?"`

### Unfiltered Search Results (Cross-regional match)

```plaintext
Rank 1 [Score: 0.7930] Region: APAC | Policy: HR-207
Snippet: # HR-207: Regional Leave Policy Addendum - APAC
### 3.2 Probationary Employee Carry-Over Cap
| Employee Tier | Probation Carry-Over Limit | Approval Required | ...

Rank 2 [Score: 0.7748] Region: EMEA | Policy: HR-207
Snippet: # HR-207: Regional Leave Policy Addendum - EMEA
### 3.2 Probationary Restrictions
| Employee Tier | Probation Carry-Over Limit | Approval Required | ...
```

### Filtered Search Results (where region == 'EMEA')

```plaintext
Rank 1 [Score: 0.7748] Region: EMEA | Policy: HR-207
Snippet: # HR-207: Regional Leave Policy Addendum - EMEA
### 3.2 Probationary Restrictions
| Employee Tier | Probation Carry-Over Limit | Approval Required | ...

Rank 2 [Score: 0.7325] Region: EMEA | Policy: HR-207
Snippet: # HR-207: Regional Leave Policy Addendum - EMEA
### 3.1 General Caps
Employees may carry over a maximum of 5 unused days into the next calendar year...
```

---

## 4. End-to-End Grounded Q&A and Refusal Outputs

### Test Case 1: Grounded Table Query (with region="APAC")
- **Question**: `"What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?"`
- **Retrieved Target**: `HR-207_APAC.md` (Section 3.2 table)
- **Generated Answer**:
  > Tier 1 probationary staff in the APAC region have an annual leave carry-over limit of up to 3 days, subject to direct manager approval [Policy: HR-207, Section: 3.2, Region: APAC].

### Test Case 2: Out-of-Domain Refusal Query (with region="APAC")
- **Question**: `"What is the company policy on remote work stipends for APAC engineers?"`
- **Retrieved Chunks**: General leave addenda (unrelated)
- **Generated Answer**:
  > I do not have sufficient information in the provided leave policy documents to answer this question.
