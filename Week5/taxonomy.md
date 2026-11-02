# Week 5 Practical — Task Set C: Failure Taxonomy (One-Page Overview)

**Domain:** HR Policy (Multi-Region Leave Addenda)  
**Module:** M3 — Evals & Error Analysis · THE CORE  
**Taskset:** Week 5 Practical — Task Set C  
**Sample Methodology:** Seeded random sample of 20 traces (`random.seed(42)`) drawn from persistent operational trace logs (`traces.jsonl`).

---

## Ranked Failure Taxonomy

| Rank | Named Failure Mode | Count | Frequency (%) | Severity & Operational Impact | Example Trace ID | Priority Score (Freq × Sev) |
|---|---|---|---|---|---|---|
| **#1** | **Eligibility Matrix & Tenure Tier Extraction** | 5 | 25.0% | **Critical Legal Exposure** (Confusing probationary vs. confirmed entitlement violates statutory policy and employee contractual rights) | `trace_7a4f91e2` | **125.0** |
| **#2** | **Out-of-Corpus Query Handling & Refusal** | 5 | 25.0% | **Critical Misinformation Risk** (Fabricating ungrounded policies exposes the enterprise to binding legal liability) | `trace_1d8c339a` | **125.0** |
| **#3** | **Exact Policy Section Retrieval Lookup** | 5 | 25.0% | **High Compliance Risk** (Misquoting exact legal clauses results in ungrounded employee benefit claims) | `trace_9b2e041f` | **100.0** |
| **#4** | **Regional Jurisdiction Disambiguation** | 5 | 25.0% | **High Regional Risk** (Cross-border policy confusion causes payroll errors across EMEA/APAC/LATAM/NA) | `trace_4c1e873b` | **100.0** |

---

### One-Screen Operational Summary
- **Total Sampled Traces:** 20 (Seeded: 42)
- **Top Attack Mode for Next Week:** **Mode #1 (Eligibility Matrix & Tenure Tier Extraction)**
- **Planned Engineering Action:** Move section & numeric tenure criteria out of prompt judging into deterministic code assertions and calibrate Judge V2 with few-shot disagreement anchors.
