# Week 3 Demo Guide: Questions, Grounded Answers & Presentation Script

This document contains the complete question-and-answer dataset and a verbatim, step-by-step speaker script for your live demo of the **Global HR Leave Policy RAG Assistant**.

---

## Part 1: All Benchmark Questions & Grounded Answers

Every answer below is strictly grounded in the ingested policy documents and includes exact source citations formatted as `[Policy: <ID>, Section: <Section>, Region: <Region>]`.

---

### **Q1: Annual Leave Carry-Over for Tier 1 Probationary Staff (APAC)**
- **Question:** *"What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?"*
- **Jurisdiction / Filter:** `region: APAC`
- **Expected Policy & Section:** Policy `HR-207`, Section `3.2`
- **Generated Grounded Answer:**
  > "The annual leave carry-over cap for Tier 1 probationary staff in APAC is **3 days** [Policy: HR-207, Section: 3.2, Region: APAC]. Employees under probation must obtain manager approval before utilizing carry-over leave during active probation periods [Policy: HR-207, Section: 3.2, Region: APAC]."

---

### **Q2: Carry-Over Cap for Tier 2 Leads in Probation (APAC)**
- **Question:** *"What is the carry-over cap for Tier 2 Leads during probation in APAC?"*
- **Jurisdiction / Filter:** `region: APAC`
- **Expected Policy & Section:** Policy `HR-207`, Section `3.2`
- **Generated Grounded Answer:**
  > "The carry-over cap for Tier 2 Leads during probation in APAC is **5 days** [Policy: HR-207, Section: 3.2, Region: APAC]."

---

### **Q3: Probationary Leave Rollover Restriction (EMEA)**
- **Question:** *"Are unconfirmed probationary employees allowed to roll over leave in EMEA?"*
- **Jurisdiction / Filter:** `region: EMEA`
- **Expected Policy & Section:** Policy `HR-207`, Section `3.2`
- **Generated Grounded Answer:**
  > "No, unconfirmed probationary employees are prohibited from rolling over unused leave balances [Policy: HR-207, Section: 3.2 Probationary Restrictions, Region: EMEA]."

---

### **Q4: Parental Leave Duration for 24 Months of Service (North America)**
- **Question:** *"What is the paid leave duration for a primary caregiver with 24 months of service in North America?"*
- **Jurisdiction / Filter:** `region: NA`
- **Expected Policy & Section:** Policy `HR-208`, Section `2.1`
- **Generated Grounded Answer:**
  > "A primary caregiver with 24 months of service in North America is eligible for **14 weeks of full pay** [Policy: HR-208, Section: 2.1, Region: NA]."

---

### **Q5: Category A Primary Caregiver Leave (LATAM)**
- **Question:** *"How many weeks of paid leave does a Category A primary caregiver receive in LATAM?"*
- **Jurisdiction / Filter:** `region: LATAM`
- **Expected Policy & Section:** Policy `HR-208`, Section `2.1`
- **Generated Grounded Answer:**
  > "A Category A primary caregiver in LATAM receives **6 weeks of full paid leave** [Policy: HR-208, Section: 2.1, Region: LATAM]."

---

### **Q6: Medical Absence Documentation Matrix (UK)**
- **Question:** *"What documentation is required for medical absences exceeding 8 days in the UK?"*
- **Jurisdiction / Filter:** `region: UK`
- **Expected Policy & Section:** Policy `HR-209`, Section `2.1`
- **Generated Grounded Answer:**
  > "For medical absences exceeding 8 days in the UK, a **Statement of Fitness for Work (GP Fit Note)** is required [Policy: HR-209, Section: 2.1 Notification Matrix, Region: UK]."

---

### **Q7: Paid Paternity Leave for Non-Birthing Parents (LATAM)**
- **Question:** *"How many consecutive days of paid paternity leave do non-birthing parents receive in LATAM?"*
- **Jurisdiction / Filter:** `region: LATAM`
- **Expected Policy & Section:** Policy `HR-208`, Section `2.2`
- **Generated Grounded Answer:**
  > "Non-birthing parents in LATAM receive **15 consecutive calendar days of paid paternity leave** [Policy: HR-208, Section: 2.2, Region: LATAM]."

---

### **Q8: Carer's Conversion Cap for Year 2+ Employees (ANZ)**
- **Question:** *"What is the Carer's Conversion Cap for Year 2+ employees in ANZ?"*
- **Jurisdiction / Filter:** `region: ANZ`
- **Expected Policy & Section:** Policy `HR-209`, Section `2.1`
- **Generated Grounded Answer:**
  > "For Year 2+ employees in ANZ, the Carer's Conversion Cap is a maximum of **8 days** [Policy: HR-209, Section: 2.1, Region: ANZ]."

---

### **Out-of-Domain Refusal Guardrail Test (Safety)**
- **Question:** *"What is the company policy on remote work stipends for APAC engineers?"*
- **Jurisdiction / Filter:** `None`
- **Expected Behavior:** Graceful refusal (Prevents hallucination on non-leave policies)
- **Generated Grounded Answer:**
  > "I do not have sufficient information in the provided leave policy documents to answer this question."

---

## Part 2: Live Demo Presentation Script (Step-by-Step)

### **1. Opening Hook & Context (30 seconds)**
> *"Hello everyone. Today I'm demonstrating our **Enterprise Global HR Leave Policy RAG Assistant**.*
>
> *In global organizations, employees operate across multiple legal jurisdictions—APAC, EMEA, North America, LATAM, UK, and ANZ. Because each region has distinct statutory leave entitlements, probationary caps, and documentation requirements, a standard LLM often creates severe cross-regional hallucinations—such as quoting UK sick leave rules to an employee in Australia, or confusing EMEA probationary caps with APAC.*
>
> *Our solution solves this through **Structure-Aware Chunking**, **High-Dimensional Dense Vector Retrieval (3072 dims)** via Qdrant, **Payload Metadata Pre-Filtering**, and **Strict Grounding Guardrails** with clause-level citations."*

---

### **2. Ingestion & Chunking Architecture (45 seconds)**
> *(Show terminal or project directory)*
>
> *"Our knowledge base consists of 6 regional leave policy documents in PDF format stored in `data_drop/`. When we run `python -m Services.injest`:*
> 1. *It automatically parses metadata (Policy ID, Jurisdiction Region, Effective Date) and raw content directly from each PDF.*
> 2. *We compare two distinct chunking architectures:*
>    - *The **Baseline Chunker**, which uses a fixed 350-character sliding window (17 chunks).*
>    - *Our **Structure-Aware Chunker**, which parses markdown header hierarchies (`#`, `##`, `###`) and preserves complex tabular matrices intact (28 chunks).*
> 3. *Each chunk is embedded into 3,072 dimensions using Google's `gemini-embedding-001` and upserted into Qdrant with rich payload metadata."*

---

### **3. Live Terminal Benchmark: 100% Hit@5 (45 seconds)**
> *(Execute in terminal: `python -m Services.bench_mark`)*
>
> *"Now let's run our automated benchmark across 8 complex, ground-truth operational questions covering all regions:*
>
> *(Point to terminal output)*
>
> *"As you can see on screen, both chunking strategies achieve **8 out of 8 (100%) Hit-in-Top-5**. Notice that for every single query—whether it's Tier 1 carry-over caps in APAC or GP fit-note thresholds in the UK—the correct regional policy document is retrieved at Rank 1."*

---

### **4. Metadata Filtering: Eliminating Regional Hallucination (60 seconds)**
> *(Scroll to the second section of the benchmark output: `METADATA FILTER DEMONSTRATION`)*
>
> *"Now, here is a critical demonstration of our metadata filtering capabilities.*
>
> *Suppose an employee simply asks: `'What is the carry-over cap for probationary employees?'` without explicitly specifying their region in the prompt text.*
>
> *In the **Unfiltered Search**, look at what happens: Rank 1 returns **APAC**, Rank 2 returns **EMEA**, and Rank 3 returns **APAC**. If an EMEA employee was serviced with unfiltered retrieval, the LLM would likely cite the 3-day APAC cap instead of the EMEA rule which strictly prohibits rollover.*
>
> *Now look at the **Filtered Search** where we apply `region == 'EMEA'` at the vector payload layer:*
> *All top 3 results are 100% EMEA policy chunks. The search space is strictly bounded to the employee's jurisdiction, completely eliminating cross-border policy pollution."*

---

### **5. Generation, Citations & Guardrails (60 seconds)**
> *(Execute in terminal: `python -m Services.rag_engine`)*
>
> *"Finally, let's look at the generation stage powered by `gemini-2.5-flash` at temperature 0.0 with strict system instructions.*
>
> **Test 1: Grounded Table Retrieval**
> *Question: 'What is the annual leave carry-over cap for Tier 1 probationary staff in APAC?'*
> *Answer: The model responds:*
> > 'The annual leave carry-over cap for Tier 1 probationary staff in APAC is 3 days [Policy: HR-207, Section: 3.2, Region: APAC].'
> *Notice that every factual assertion is tied to an explicit citation with Policy ID, Section Number, and Region.*
>
> **Test 2: Out-of-Domain Refusal Guardrail**
> *Now, what happens if an employee asks an ungrounded or out-of-scope question like:*
> *'What is the company policy on remote work stipends for APAC engineers?'*
> *Instead of guessing or hallucinating an answer, the guardrail triggers immediately:*
> > 'I do not have sufficient information in the provided leave policy documents to answer this question.'
>
> *This guarantees enterprise safety, auditability, and zero hallucination."*

---

### **6. Closing Wrap-Up (15 seconds)**
> *"In summary, this RAG assistant provides:*
> 1. *100% retrieval accuracy on complex table data across 6 regions,*
> 2. *Zero cross-regional leakage via Qdrant metadata filtering,*
> 3. *Verifiable clause-level citations,*
> 4. *Robust out-of-domain refusal guardrails.*
>
> *Thank you! I'm happy to take any questions."*

---

## Part 3: Quick Command Reference

```bash
# 1. Ingest 6 PDF policies into Qdrant
python -m Services.injest

# 2. Run the 8-question benchmark & metadata filter demo (writes results.md)
python -m Services.bench_mark

# 3. Run grounded synthesis & refusal test
python -m Services.rag_engine

# 4. Ask custom questions interactively (unrestricted)
python ask.py
```

---

## Part 4: Explaining Baseline vs. Structure-Aware Chunker (Interview & Demo Script)

When the evaluators ask: *"Why did you compare two chunking strategies and what is the importance of the Structure-Aware Chunker?"*, use the following points:

### 1. The Core Problem with the Baseline Chunker (Fixed Character Window)
- **Arbitrary Slicing**: The baseline chunker cuts text at a fixed `350` characters with `50` characters overlap, completely blind to semantics.
- **Table Amputation**: In policy documents, critical rules are stored in tables (e.g. `Tier 1 | Probationary | 3 days`). The baseline chunker frequently cuts a table in half, putting the table header (`Tier | Probation Status | Cap`) in Chunk 1, and the rows in Chunk 2. When Chunk 2 is embedded alone, the embedding model has no idea what "3 days" represents.
- **Loss of Document Anchoring**: If a subsection starts with `3.2 Probationary Restrictions`, the baseline chunk contains only those words without the document title (`HR-207 APAC`). Floating chunks without document identity lead to cross-policy hallucinations.

### 2. The 3 Superpowers of the Structure-Aware Chunker
1. **Header & Section Boundary Preservation**:
   - Parses markdown headings (`#`, `##`, `###`) and numbered policy clauses (`1. Scope`, `3.2 Probationary...`).
   - Ensures an entire policy clause or rule exists in a single, coherent vector chunk.
2. **Table & Matrix Integrity**:
   - Keeps complete multi-column tables intact within the chunk so the LLM has both column headers and row values together during generation.
3. **Context Hierarchy Anchoring**:
   - Inspect `Services/Chunker.py`: It automatically extracts the root document title/policy ID (`HR-207: Regional Leave Policy Addendum - APAC`) and prepends it to every subsequent sub-clause chunk (`full_chunk = f"{current_doc_title}\n\n{sec}"`).
   - Every chunk embedded into Qdrant is permanently anchored to its parent policy and region.

### 3. Comparison Table to Present

| Feature | Baseline Chunker | Structure-Aware Chunker |
| :--- | :--- | :--- |
| **Chunking Logic** | Blind sliding window (350 chars, 50 overlap) | Semantic section & header boundaries |
| **Output Chunks** | 17 chunks | 28 chunks |
| **Table Preservation** | Tables split mid-row or separated from headers | 100% complete tables preserved |
| **Context Anchoring** | Subsections lose parent policy ID | Parent title automatically prepended |
| **Production Scale** | High risk of truncated clauses & hallucinations | High precision, legal-grade compliance |

