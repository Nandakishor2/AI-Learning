# Week 3 Practical — Task Set C: Results & Evaluation Report

**Domain:** HR Policy (Multi-Region Leave Addenda)  
**Module:** M2 — Retrieval & RAG  
**Taskset:** Week 3 Practical — Task Set C  
**Corpus Scope:** 6 regional addenda ingested independently (`HR-207_APAC.md`, `HR-207_EMEA.md`, `HR-208_LATAM.md`, `HR-208_NA.md`, `HR-209_ANZ.md`, `HR-209_UK.md`). Base handbook was NOT re-indexed, focusing purely on the new regional policy drop.

---

## 1. Ground-Truth 8 Questions & Target Locations

All 8 benchmark questions were written directly against the source policy documents before running retrieval. 6 of the 8 questions specifically test row-level precision inside eligibility markdown tables.

| Q# | Question Text | Policy ID | Target Section | Region | Table-Based? | Key Target Clause / Value |
|---|---|---|---|---|---|---|
| **Q1** | What is the annual leave carry-over cap for Tier 1 probationary staff in APAC? | `HR-207` | Section 3.2 | APAC | Yes | Cap = 3 days, forfeiture 60 days post-probation |
| **Q2** | What is the carry-over cap for Tier 2 Leads during probation in APAC? | `HR-207` | Section 3.2 | APAC | Yes | Cap = 5 days, forfeiture 90 days post-probation |
| **Q3** | Are unconfirmed probationary employees allowed to roll over leave in EMEA? | `HR-207` | Section 3.2 | EMEA | Yes | Cap = 0 days (prohibited from rolling over) |
| **Q4** | What is the paid leave duration for a primary caregiver with 24 months of service in North America? | `HR-208` | Section 2.1 | NA | Yes | Standard tenure (12-36 mos) = 14 weeks full pay |
| **Q5** | How many weeks of paid leave does a Category A primary caregiver receive in LATAM? | `HR-208` | Section 2.1 | LATAM | Yes | Category A (< 6 mos) = 6 weeks full pay |
| **Q6** | What documentation is required for medical absences exceeding 8 days in the UK? | `HR-209` | Section 2.1 | UK | Yes | Statement of Fitness for Work (GP Fit Note) |
| **Q7** | How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM? | `HR-208` | Section 2.2 | LATAM | No | 15 consecutive calendar days |
| **Q8** | What is the Carer's Conversion Cap for Year 2+ employees in ANZ? | `HR-209` | Section 2.1 | ANZ | Yes | Max 8 days conversion cap |

---

## 2. Hit-in-Top-5 Benchmark Table

Both chunking strategies were indexed into isolated Qdrant vector collections (`baseline_chunks` and `structure_chunks`) using `gemini-embedding-001` (3072 dimensions, Cosine distance). All 8 questions were evaluated in search-only mode against both collections.

| Q# | Question Summary | Target Policy & Section | Baseline Chunker (Strategy A) Hit@5 | Structure-Aware Chunker (Strategy B) Hit@5 | Top-1 Policy (Strategy B) |
|---|---|---|---|---|---|
| **Q1** | APAC Tier 1 Probation Carry-Over | `HR-207` §3.2 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-207` |
| **Q2** | APAC Tier 2 Lead Probation Carry-Over | `HR-207` §3.2 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-207` |
| **Q3** | EMEA Probation Roll-Over Rule | `HR-207` §3.2 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-207` |
| **Q4** | NA 24-Month Caregiver Leave Duration | `HR-208` §2.1 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-208` |
| **Q5** | LATAM Category A Caregiver Weeks | `HR-208` §2.1 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-208` |
| **Q6** | UK 8+ Days Absence Doctor Fit Note | `HR-209` §2.1 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-209` |
| **Q7** | LATAM Non-Birthing Paternity Leave | `HR-208` §2.2 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-208` |
| **Q8** | ANZ Year 2+ Carer Conversion Cap | `HR-209` §2.1 | **HIT** (Rank 1) | **HIT** (Rank 1) | `HR-209` |

### Benchmark Summary Score
- **Baseline Sliding-Window Chunker (350 chars, 50 overlap)**: **8/8 (100%)**
- **Structure-Aware Header/Table Chunker**: **8/8 (100%)**

---

## 3. Metadata Filtering Proof (Region Isolation)

**Query:** `"What is the carry-over cap for probationary employees?"`

### 3.1 Unfiltered Search Results (Cross-Regional Ambiguity)
Without metadata filtering, the retriever returns conflicting regional addenda based purely on semantic similarity:

```plaintext
Rank 1 [Score: 0.7930] Region: APAC | Policy: HR-207 | Chunk ID: struct_HR-207_APAC_3
Snippet:
# HR-207: Regional Leave Policy Addendum - APAC
### 3.2 Probationary Employee Carry-Over Cap
| Employee Tier | Probation Status | Carry-Over Cap (Days) | Forfeiture Window |
| Tier 1 Staff | In Probation (<6 mos) | 3 | 60 days post-probation |
| Tier 2 Leads | In Probation (<6 mos) | 5 | 90 days post-probation |

Rank 2 [Score: 0.7748] Region: EMEA | Policy: HR-207 | Chunk ID: struct_HR-207_EMEA_3
Snippet:
# HR-207: Regional Leave Policy Addendum - EMEA
### 3.2 Probationary Restrictions
| Employee Tier | Probation Status | Carry-Over Cap (Days) | Mandatory Usage Date |
| All Tiers | In Probation (<6 mos) | 0 | Not Applicable |
| All Tiers | Confirmed (>6 mos) | 5 | June 30th |

Rank 3 [Score: 0.7325] Region: EMEA | Policy: HR-207 | Chunk ID: struct_HR-207_EMEA_2
Snippet:
# HR-207: Regional Leave Policy Addendum - EMEA
### 3.1 General Caps
Employees may carry over a maximum of 5 days into the following year, expiring June 30th.
```

### 3.2 Filtered Search Results (`region == "EMEA"`)
Applying the payload filter `{"region": "EMEA"}` eliminates APAC results and shifts EMEA Rank 2 directly to Top-1:

```plaintext
Rank 1 [Score: 0.7748] Region: EMEA | Policy: HR-207 | Chunk ID: struct_HR-207_EMEA_3
Snippet:
# HR-207: Regional Leave Policy Addendum - EMEA
### 3.2 Probationary Restrictions
| Employee Tier | Probation Status | Carry-Over Cap (Days) | Mandatory Usage Date |
| All Tiers | In Probation (<6 mos) | 0 | Not Applicable |
| All Tiers | Confirmed (>6 mos) | 5 | June 30th |

Rank 2 [Score: 0.7325] Region: EMEA | Policy: HR-207 | Chunk ID: struct_HR-207_EMEA_2
Snippet:
# HR-207: Regional Leave Policy Addendum - EMEA
### 3.1 General Caps
Employees may carry over a maximum of 5 days into the following year, expiring June 30th.

Rank 3 [Score: 0.6912] Region: EMEA | Policy: HR-207 | Chunk ID: struct_HR-207_EMEA_1
Snippet:
# HR-207: Regional Leave Policy Addendum - EMEA
## 2. Annual Leave Entitlements
Standard annual leave allocation is fixed at 25 working days per calendar year.
```

**Observation:** The Top-1 result correctly switched from APAC (Score 0.7930) to EMEA (Score 0.7748), preventing an EMEA employee from receiving APAC policy terms.

---

## 4. End-to-End Grounded Generation & Exact Citations

All queries executed through `gemini-2.5-flash` at `temperature: 0.0` with strict context grounding and required citation formatting: `[Policy: <policy_id>, Section: <section>, Region: <region>]`.

### Answerable Question 1 (APAC Probation Carry-Over)
- **Question:** `"What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?"`
- **Region Filter:** `APAC`
- **Retrieved Chunk ID:** `struct_HR-207_APAC_3` (`file:///d:/AI%20Learning/AI-Learning/Week3/data_drop/HR-207_APAC.md#L19-L26`)
- **Generated Answer:**
  > Tier 1 probationary staff in the APAC region have an annual leave carry-over cap of 3 days, with a forfeiture window of 60 days post-probation [Policy: HR-207, Section: 3.2, Region: APAC]. Additionally, employees must obtain manager approval prior to utilizing carry-over leave during active probation periods [Policy: HR-207, Section: 3.2, Region: APAC].

### Answerable Question 2 (North America Primary Caregiver Benefit)
- **Question:** `"What is the paid leave duration for a primary caregiver with 24 months of service in North America?"`
- **Region Filter:** `NA`
- **Retrieved Chunk ID:** `struct_HR-208_NA_2` (`file:///d:/AI%20Learning/AI-Learning/Week3/data_drop/HR-208_NA.md#L12-L19`)
- **Generated Answer:**
  > Under the North America Parental & Family Support Addendum, a primary caregiver with 24 months of continuous service falls into the Standard tenure category (12 to 36 months) and is eligible for 14 weeks of fully paid leave benefit [Policy: HR-208, Section: 2.1, Region: NA]. Employees are also entitled to up to 6 weeks of unpaid extension [Policy: HR-208, Section: 2.1, Region: NA].

### Answerable Question 3 (UK Sick Leave Medical Certification)
- **Question:** `"What documentation is required for medical absences exceeding 8 days in the UK?"`
- **Region Filter:** `UK`
- **Retrieved Chunk ID:** `struct_HR-209_UK_2` (`file:///d:/AI%20Learning/AI-Learning/Week3/data_drop/HR-209_UK.md#L12-L19`)
- **Generated Answer:**
  > For medical absences of 8 or more consecutive days in the UK, employees are required to provide a Statement of Fitness for Work (GP Fit Note) [Policy: HR-209, Section: 2.1, Region: UK]. Under this tier, employees receive 100% salary for up to 4 weeks, followed by 50% pay for the subsequent 8 weeks [Policy: HR-209, Section: 2.1, Region: UK].

---

## 5. Refusal Transcripts (Out-of-Corpus / Ungrounded Questions)

The system strictly enforces the refusal guardrail when queries address topics not present in the indexed addenda.

### Refusal Transcript 1: Remote Work / Home Office Stipend
```plaintext
USER QUERY:
What is the company policy on remote work stipends and ergonomic equipment reimbursement for APAC engineers?

RETRIEVED CONTEXTS:
- struct_HR-207_APAC_1 (HR-207 §1 Scope & §2 Annual Leave Accrual)
- struct_HR-207_APAC_2 (HR-207 §3.1 Standard Carry-Over)

SYSTEM RESPONSE:
I do not have sufficient information in the provided leave policy documents to answer this question.
```

### Refusal Transcript 2: Unpaid Sabbatical Policy
```plaintext
USER QUERY:
How many months of unpaid sabbatical leave can an employee take after 5 years of continuous service in EMEA?

RETRIEVED CONTEXTS:
- struct_HR-207_EMEA_1 (HR-207 §1 Scope & §2 Annual Leave Entitlements)
- struct_HR-207_EMEA_3 (HR-207 §3.2 Probationary Restrictions)

SYSTEM RESPONSE:
I do not have sufficient information in the provided leave policy documents to answer this question.
```

### Refusal Transcript 3: Cash Conversion of Unused Sick Leave
```plaintext
USER QUERY:
Can unused personal sick leave days in ANZ be cashed out for monetary compensation at the end of the financial year?

RETRIEVED CONTEXTS:
- struct_HR-209_ANZ_2 (HR-209 §2.1 Personal Leave Accumulation Schedule)
- struct_HR-209_ANZ_3 (HR-209 §2.2 Unplanned Absence Evidence)

SYSTEM RESPONSE:
I do not have sufficient information in the provided leave policy documents to answer this question.
```

---

## 6. Defended Chunking Choice & Embarrassing Failure Diagnosis

### 6.1 Chunking Strategy Decision: Why Structure-Aware Ships
We are deploying **Strategy B (Structure-Aware Markdown Chunker)** to production. While both strategies achieved 8/8 on top-5 retrieval for isolated short queries, the baseline sliding-window chunker creates legal and operational liabilities by arbitrarily severing markdown tables across character offsets. When table headers (e.g., `Carry-Over Cap (Days)`) become detached from corresponding row values (e.g., `Tier 1 | 3`), the LLM is forced to infer schema semantics, risking hallucinations in compensation and compliance domains. Structure-aware chunking keeps sections, table syntax, and hierarchical breadcrumbs (`# Document Title -> ### Section`) bound together as a single atomic unit of truth, guaranteeing accurate citations and zero schema truncation.

### 6.2 The Embarrassing Retrieval Failure & Diagnosis
- **Failure Case:** In the baseline sliding-window run on `HR-207_EMEA.md`, chunk `base_HR-207_EMEA_1` split midway through Section 3.2 at character position 350.
- **Symptom:** Chunk 1 contained the table headers and the first half of the column names, while Chunk 2 contained the data row `| All Tiers | In Probation (<6 mos) | 0 | Not Applicable |` with zero column headers and no reference to `### 3.2 Probationary Restrictions`.
- **Diagnosis:** When queried with `"What are the probationary restrictions for EMEA leave carry over?"`, Chunk 2 was retrieved with an embedding score of 0.68, but because the column header `Carry-Over Cap (Days)` was severed, the generator had to guess whether `0` represented days permitted, days forfeited, or months of probation. This boundary bisection failure proved that naive sliding-window chunking is fundamentally unsafe for structured tabular HR policies.

---

## 7. Search-Only Dump for All 8 Questions Under Both Strategies

### Strategy A: Baseline Sliding Window (350 char, 50 overlap)
```plaintext
[Q1] 'What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?'
  - Rank 1 [Score: 0.7812] Chunk: base_HR-207_APAC_1 | Policy: HR-207 | Region: APAC [HIT]
  - Rank 2 [Score: 0.7450] Chunk: base_HR-207_APAC_0 | Policy: HR-207 | Region: APAC

[Q2] 'What is the carry-over cap for Tier 2 Leads during probation in APAC?'
  - Rank 1 [Score: 0.7789] Chunk: base_HR-207_APAC_1 | Policy: HR-207 | Region: APAC [HIT]
  - Rank 2 [Score: 0.7301] Chunk: base_HR-207_APAC_0 | Policy: HR-207 | Region: APAC

[Q3] 'Are unconfirmed probationary employees allowed to roll over leave in EMEA?'
  - Rank 1 [Score: 0.7645] Chunk: base_HR-207_EMEA_1 | Policy: HR-207 | Region: EMEA [HIT]
  - Rank 2 [Score: 0.7288] Chunk: base_HR-207_EMEA_0 | Policy: HR-207 | Region: EMEA

[Q4] 'What is the paid leave duration for a primary caregiver with 24 months of service in North America?'
  - Rank 1 [Score: 0.7910] Chunk: base_HR-208_NA_1 | Policy: HR-208 | Region: NA [HIT]
  - Rank 2 [Score: 0.7150] Chunk: base_HR-208_NA_0 | Policy: HR-208 | Region: NA

[Q5] 'How many weeks of paid leave does a Category A primary caregiver receive in LATAM?'
  - Rank 1 [Score: 0.7834] Chunk: base_HR-208_LATAM_1 | Policy: HR-208 | Region: LATAM [HIT]
  - Rank 2 [Score: 0.7021] Chunk: base_HR-208_LATAM_0 | Policy: HR-208 | Region: LATAM

[Q6] 'What documentation is required for medical absences exceeding 8 days in the UK?'
  - Rank 1 [Score: 0.8122] Chunk: base_HR-209_UK_1 | Policy: HR-209 | Region: UK [HIT]
  - Rank 2 [Score: 0.7405] Chunk: base_HR-209_UK_0 | Policy: HR-209 | Region: UK

[Q7] 'How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM?'
  - Rank 1 [Score: 0.8041] Chunk: base_HR-208_LATAM_1 | Policy: HR-208 | Region: LATAM [HIT]
  - Rank 2 [Score: 0.7118] Chunk: base_HR-208_LATAM_0 | Policy: HR-208 | Region: LATAM

[Q8] 'What is the Carer's Conversion Cap for Year 2+ employees in ANZ?'
  - Rank 1 [Score: 0.7895] Chunk: base_HR-209_ANZ_1 | Policy: HR-209 | Region: ANZ [HIT]
  - Rank 2 [Score: 0.7214] Chunk: base_HR-209_ANZ_0 | Policy: HR-209 | Region: ANZ
```

### Strategy B: Structure-Aware Markdown Chunker
```plaintext
[Q1] 'What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?'
  - Rank 1 [Score: 0.8120] Chunk: struct_HR-207_APAC_3 | Policy: HR-207 | Region: APAC [HIT]
  - Rank 2 [Score: 0.7650] Chunk: struct_HR-207_APAC_2 | Policy: HR-207 | Region: APAC

[Q2] 'What is the carry-over cap for Tier 2 Leads during probation in APAC?'
  - Rank 1 [Score: 0.8094] Chunk: struct_HR-207_APAC_3 | Policy: HR-207 | Region: APAC [HIT]
  - Rank 2 [Score: 0.7511] Chunk: struct_HR-207_APAC_2 | Policy: HR-207 | Region: APAC

[Q3] 'Are unconfirmed probationary employees allowed to roll over leave in EMEA?'
  - Rank 1 [Score: 0.7981] Chunk: struct_HR-207_EMEA_3 | Policy: HR-207 | Region: EMEA [HIT]
  - Rank 2 [Score: 0.7432] Chunk: struct_HR-207_EMEA_2 | Policy: HR-207 | Region: EMEA

[Q4] 'What is the paid leave duration for a primary caregiver with 24 months of service in North America?'
  - Rank 1 [Score: 0.8245] Chunk: struct_HR-208_NA_2 | Policy: HR-208 | Region: NA [HIT]
  - Rank 2 [Score: 0.7380] Chunk: struct_HR-208_NA_1 | Policy: HR-208 | Region: NA

[Q5] 'How many weeks of paid leave does a Category A primary caregiver receive in LATAM?'
  - Rank 1 [Score: 0.8170] Chunk: struct_HR-208_LATAM_2 | Policy: HR-208 | Region: LATAM [HIT]
  - Rank 2 [Score: 0.7290] Chunk: struct_HR-208_LATAM_1 | Policy: HR-208 | Region: LATAM

[Q6] 'What documentation is required for medical absences exceeding 8 days in the UK?'
  - Rank 1 [Score: 0.8350] Chunk: struct_HR-209_UK_2 | Policy: HR-209 | Region: UK [HIT]
  - Rank 2 [Score: 0.7580] Chunk: struct_HR-209_UK_1 | Policy: HR-209 | Region: UK

[Q7] 'How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM?'
  - Rank 1 [Score: 0.8280] Chunk: struct_HR-208_LATAM_3 | Policy: HR-208 | Region: LATAM [HIT]
  - Rank 2 [Score: 0.7410] Chunk: struct_HR-208_LATAM_2 | Policy: HR-208 | Region: LATAM

[Q8] 'What is the Carer's Conversion Cap for Year 2+ employees in ANZ?'
  - Rank 1 [Score: 0.8195] Chunk: struct_HR-209_ANZ_2 | Policy: HR-209 | Region: ANZ [HIT]
  - Rank 2 [Score: 0.7460] Chunk: struct_HR-209_ANZ_1 | Policy: HR-209 | Region: ANZ
```

---

## 8. Code Diff: Chunker & Metadata Architecture

```diff
--- Services/Chunker_Baseline.py
+++ Services/Chunker_StructureAware.py
@@ -1,14 +1,30 @@
+import re
+
 def baseline_chunk(text: str, chunk_size: int = 350, overlap: int = 50) -> list[str]:
-    """Strategy A: Naive fixed sliding-window chunker."""
+    """Strategy A: Naive fixed sliding-window chunker (splits mid-table)."""
     text = text.replace('\r\n', '\n')
     chunks = []
     start = 0
     while start < len(text):
         end = min(start + chunk_size, len(text))
         chunks.append(text[start:end])
         if end == len(text):
             break
         start += chunk_size - overlap
     return chunks
+
+def structure_aware_chunk(text: str) -> list[str]:
+    """
+    Strategy B: Structure-aware chunker.
+    Splits on Markdown headings (#, ##, ###) while retaining document title context
+    and keeping eligibility tables completely unbroken within clause chunks.
+    """
+    text = text.replace('\r\n', '\n')
+    sections = re.split(r'\n(?=#{1,3}\s)', text)
+    structured_chunks = []
+    
+    current_doc_title = ""
+    for sec in sections:
+        sec = sec.strip()
+        if not sec:
+            continue
+        if sec.startswith("# "):
+            current_doc_title = sec.split("\n", 1)[0]
+            if "\n" in sec:
+                structured_chunks.append(sec)
+        else:
+            # Prefix parent document title to provide autonomous authority
+            full_chunk = f"{current_doc_title}\n\n{sec}" if current_doc_title else sec
+            structured_chunks.append(full_chunk)
+            
+    return structured_chunks
```

```diff
--- Services/injest_metadata_payload.py
+++ Services/injest_metadata_payload.py
@@ -70,12 +70,14 @@
         meta, body = parse_frontmatter(content)
         
-        # Missing metadata causes un-routable chunks
+        # Strict mandatory chunk metadata schema
         base_meta = {
             "source_file": meta.get("source_file", filename),
             "policy_id": meta.get("policy_id", "UNKNOWN"),
             "region": meta.get("region", "GLOBAL"),
-            "effective_date": meta.get("effective_date", "UNKNOWN")
+            "effective_date": meta.get("effective_date", "UNKNOWN"),
+            "chunk_id": f"struct_{meta.get('policy_id')}_{meta.get('region')}_{idx}"
         }
```

---

## 9. Bonus Challenge: Retrieval Precision vs. Generation Completeness Tension

**Test Question:** `"What are the primary caregiver leave benefits for employees with continuous service in LATAM?"`

### Side-by-Side Comparison

| Dimension | Strategy A (Baseline Window Chunking) | Strategy B (Structure-Aware Clause Chunking) |
|---|---|---|
| **Retrieved Content** | Retrieves a wide 350-char window spanning Section 1 (Scope) and Section 2.1 (Table). Includes mention of entity scope and statutory background. | Retrieves precisely Section 2.1 (`struct_HR-208_LATAM_2`), containing only the Primary Caregiver table (`Category A: <6 mos -> 6 wks`, `Category B: 6+ mos -> 12 wks`). |
| **Retrieval Score** | 0.7420 (Moderate semantic match) | **0.8170 (High precision match)** |
| **Generated Answer** | Explains that LATAM operating entities provide 6 or 12 weeks of leave based on tenure, noting general applicability across LATAM entities. | Cites the exact table rows for Category A and B, but cannot clarify whether probationary or contractor periods count toward 'continuous service' because the preamble scope was left in Chunk 1. |

### Tension Analysis
Structure-aware chunking maximizes semantic precision by isolating individual clauses and tables, which drastically improves retrieval rank for targeted queries. However, extreme clause atomization creates a completeness deficit when an eligibility rule relies on definitional context located in an earlier introductory paragraph. This creates an engineering trade-off: **atomic chunks guarantee high precision and table integrity, but hierarchical context-injection or parent-document retrieval is necessary to prevent definitional stranding during generation.**
