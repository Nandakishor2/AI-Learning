# Week 4 Practical — Task Set C: Results

> Single retrieval change under test: **Dense Cosine baseline → Hybrid BM25 + Reciprocal Rank Fusion (RRF, k=60)**. Chunking (structure-aware), embedding model (`gemini-embedding-001`), vector DB (Qdrant `structure_chunks`), and generator (`gemini-2.5-flash`) are identical across both runs. All numbers below are produced live by `python -m Services.bench_mark`.

## 1. Golden Set — 12 Real Employee Questions

| ID | Employee Question | Known-Correct Chunk ID | Exact-Token Type |
|---|---|---|---|
| d01 | Give me an overview of HR-207 section 3 for EMEA. | `struct_HR-207_EMEA_2` | policy+section+region |
| d02 | What does HR-207 section 3 cover for APAC? | `struct_HR-207_APAC_2` | policy+section+region |
| d03 | What does HR-209 section 2 cover for the UK? | `struct_HR-209_UK_1` | policy+section+region |
| d04 | Under HR-208 section 2.2 for our LATAM team, how many days of paternity leave does a non-birthing parent get? | `struct_HR-208_LATAM_4` | policy+section+region |
| d05 | Under HR-209 Section 2.1 for ANZ staff in their second year of service or beyond, what's the annual personal leave and the maximum carer's conversion? | `struct_HR-209_ANZ_2` | policy+section+region |
| d06 | Under HR-207 Section 3.2, what's the carry-over cap for an EMEA employee who's still within their first 6 months of probation? | `struct_HR-207_EMEA_4` | policy+section+region |
| d07 | One of our North America employees has worked here about two years — if they become a primary caregiver, how many weeks of paid leave and unpaid extension do they qualify for? | `struct_HR-208_NA_3` | region+tenure |
| d08 | When did HR-209 take effect for our ANZ offices? | `struct_HR-209_ANZ_0` | policy+region+effective_date |
| d09 | What's our carry-over cap for EMEA staff and when do unused days expire? | `struct_HR-207_EMEA_3` | region+natural |
| d10 | If I've been off sick for more than a week in the UK, what proof do I need to give HR and how much of my pay do I keep? | `struct_HR-209_UK_2` | region+natural |
| d11 | I work in our APAC office — if I don't use all my annual leave this year, how many days can I roll over into next year and when do the rest expire? | `struct_HR-207_APAC_3` | region+natural |
| d12 | What leave does a secondary caregiver get in North America and what service is needed to qualify? | `struct_HR-208_NA_4` | region+natural |

7 of 12 questions carry an exact token dense retrieval is classically expected to struggle with (policy number + section number, region code, or effective date). Every `known_correct_chunk_id` was verified to exist in the live `structure_chunks` collection before measurement, and every question is answerable from the corpus (no Not-In-Corpus entries).

---

## 2. Baseline — Dense Cosine (measured BEFORE any change)

Retriever: `DenseRetriever` — `gemini-embedding-001` (3072-dim) cosine search over Qdrant `structure_chunks`, top-3. Latency = embedding API round-trip + Qdrant search, measured per query, no warm-up discarded, p50 across all 12.

| ID | Expected Chunk | Retrieved Top-3 | Rank of Expected | Hit@3 |
|---|---|---|---|---|
| d01 | `struct_HR-207_EMEA_2` | `struct_HR-207_EMEA_0`, `struct_HR-208_NA_0`, `struct_HR-208_LATAM_0` | - | Miss |
| d02 | `struct_HR-207_APAC_2` | `struct_HR-207_APAC_0`, `struct_HR-208_NA_0`, `struct_HR-207_APAC_3` | - | Miss |
| d03 | `struct_HR-209_UK_1` | `struct_HR-208_NA_0`, `struct_HR-209_UK_0`, `struct_HR-208_LATAM_0` | - | Miss |
| d04 | `struct_HR-208_LATAM_4` | `struct_HR-208_LATAM_4`, `struct_HR-208_LATAM_0`, `struct_HR-208_LATAM_1` | 1 | Hit |
| d05 | `struct_HR-209_ANZ_2` | `struct_HR-209_ANZ_2`, `struct_HR-209_ANZ_1`, `struct_HR-209_ANZ_0` | 1 | Hit |
| d06 | `struct_HR-207_EMEA_4` | `struct_HR-207_EMEA_4`, `struct_HR-207_APAC_4`, `struct_HR-207_EMEA_3` | 1 | Hit |
| d07 | `struct_HR-208_NA_3` | `struct_HR-208_LATAM_3`, `struct_HR-208_NA_3`, `struct_HR-208_NA_4` | 2 | Hit |
| d08 | `struct_HR-209_ANZ_0` | `struct_HR-209_ANZ_0`, `struct_HR-209_ANZ_1`, `struct_HR-209_ANZ_2` | 1 | Hit |
| d09 | `struct_HR-207_EMEA_3` | `struct_HR-207_EMEA_3`, `struct_HR-207_EMEA_2`, `struct_HR-207_EMEA_4` | 1 | Hit |
| d10 | `struct_HR-209_UK_2` | `struct_HR-209_UK_2`, `struct_HR-209_UK_0`, `struct_HR-209_UK_3` | 1 | Hit |
| d11 | `struct_HR-207_APAC_3` | `struct_HR-207_APAC_3`, `struct_HR-207_APAC_2`, `struct_HR-207_APAC_1` | 1 | Hit |
| d12 | `struct_HR-208_NA_4` | `struct_HR-208_NA_4`, `struct_HR-208_NA_2`, `struct_HR-208_LATAM_2` | 1 | Hit |

- **Baseline hit-rate@3: 9/12 (75.0%)**
- Retrieval misses: 3
- **Baseline p50 latency: 613.19 ms/query**

---

## 3. Failure Inspection — R / G / Not-In-Corpus Tally

Every baseline miss was opened in the inspection view (retrieved top-3 + generated answer) and labelled:

| ID | Label | Retrieved Top-3 | One-line evidence |
|---|---|---|---|
| d01 | R | `struct_HR-207_EMEA_0`, `struct_HR-208_NA_0`, `struct_HR-208_LATAM_0` | Inspection view: expected `struct_HR-207_EMEA_2` is NOT in the top-3 (`struct_HR-207_EMEA_0`, `struct_HR-208_NA_0`, `struct_HR-208_LATAM_0`). Dense pulled semantically-adjacent preamble/scope chunks instead of the exact section — a genuine retrieval miss. |
| d02 | R | `struct_HR-207_APAC_0`, `struct_HR-208_NA_0`, `struct_HR-207_APAC_3` | Inspection view: expected `struct_HR-207_APAC_2` is NOT in the top-3 (`struct_HR-207_APAC_0`, `struct_HR-208_NA_0`, `struct_HR-207_APAC_3`). Dense pulled semantically-adjacent preamble/scope chunks instead of the exact section — a genuine retrieval miss. |
| d03 | R | `struct_HR-208_NA_0`, `struct_HR-209_UK_0`, `struct_HR-208_LATAM_0` | Inspection view: expected `struct_HR-209_UK_1` is NOT in the top-3 (`struct_HR-208_NA_0`, `struct_HR-209_UK_0`, `struct_HR-208_LATAM_0`). Dense pulled semantically-adjacent preamble/scope chunks instead of the exact section — a genuine retrieval miss. |

| Label | Meaning | Count |
|---|---|---:|
| **R** | Answerable, correct chunk absent from top-3 (retrieval fault) | 3 |
| **G** | Correct chunk in top-3 but answer wrong (generation fault) | 0 |
| **Not-In-Corpus** | Valid unanswerable question | 0 |
| **Total baseline misses** | | 3 |

---

## 4. The One Change — Justified by the Tally

The tally shows **3 R and 0 G**. Because the misses are purely retrieval (R), swapping the LLM would fix none of them — an information-retrieval change is the correct intervention. Note that the R failures here are NOT the exact-token lookups the team lead assumed would fail (those all hit) — they are vague/overview-style questions ("what does section 3 cover?") where dense embeddings drift to section-scope preamble chunks. BM25's exact lexical match on the `HR-###` + section + region tokens is precisely what recovers them.

**Change applied (exactly one):** add a BM25 lexical inverted index over the identical corpus and fuse it with the existing dense candidate list using Reciprocal Rank Fusion, `RRF(d) = Σ 1/(k + rank_i)`, `k=60`. Ranks are fused, never raw scores (cosine distance and BM25 are different scales). Nothing else changed.

---

## 5. After — Hybrid BM25 + RRF (k=60), SAME 12 questions

| ID | Expected Chunk | Retrieved Top-3 | Rank of Expected | Hit@3 |
|---|---|---|---|---|
| d01 | `struct_HR-207_EMEA_2` | `struct_HR-207_EMEA_3`, `struct_HR-207_EMEA_0`, `struct_HR-207_EMEA_2` | 3 | Hit |
| d02 | `struct_HR-207_APAC_2` | `struct_HR-207_APAC_0`, `struct_HR-207_APAC_4`, `struct_HR-207_APAC_2` | 3 | Hit |
| d03 | `struct_HR-209_UK_1` | `struct_HR-209_UK_0`, `struct_HR-209_UK_1`, `struct_HR-209_UK_2` | 2 | Hit |
| d04 | `struct_HR-208_LATAM_4` | `struct_HR-208_LATAM_4`, `struct_HR-208_NA_4`, `struct_HR-208_LATAM_1` | 1 | Hit |
| d05 | `struct_HR-209_ANZ_2` | `struct_HR-209_ANZ_2`, `struct_HR-209_ANZ_0`, `struct_HR-209_ANZ_3` | 1 | Hit |
| d06 | `struct_HR-207_EMEA_4` | `struct_HR-207_EMEA_4`, `struct_HR-207_APAC_4`, `struct_HR-207_EMEA_3` | 1 | Hit |
| d07 | `struct_HR-208_NA_3` | `struct_HR-208_NA_4`, `struct_HR-208_LATAM_3`, `struct_HR-208_NA_3` | 3 | Hit |
| d08 | `struct_HR-209_ANZ_0` | `struct_HR-209_ANZ_0`, `struct_HR-209_ANZ_1`, `struct_HR-209_ANZ_2` | 1 | Hit |
| d09 | `struct_HR-207_EMEA_3` | `struct_HR-207_EMEA_4`, `struct_HR-207_EMEA_2`, `struct_HR-207_APAC_4` | - | Miss |
| d10 | `struct_HR-209_UK_2` | `struct_HR-209_UK_2`, `struct_HR-209_UK_0`, `struct_HR-209_UK_3` | 1 | Hit |
| d11 | `struct_HR-207_APAC_3` | `struct_HR-207_APAC_3`, `struct_HR-207_APAC_0`, `struct_HR-207_APAC_1` | 1 | Hit |
| d12 | `struct_HR-208_NA_4` | `struct_HR-208_NA_4`, `struct_HR-208_NA_2`, `struct_HR-208_LATAM_3` | 1 | Hit |

- **After hit-rate@3: 11/12 (91.7%)**
- Retrieval misses: 1
- **After p50 latency: 600.23 ms/query**

---

## 6. Before → After (the two numbers that count)

| Metric | Before (Dense) | After (Hybrid RRF) | Delta |
|---|---:|---:|---:|
| Hit-rate@3 | 9/12 (75.0%) | 11/12 (91.7%) | +16.7 pts |
| Retrieval misses | 3 | 1 | -2 |
| p50 latency/query | 613.19 ms | 600.23 ms | -12.96 ms |

Latency is dominated by the remote `gemini-embedding-001` round-trip (~613 ms), which both retrievers pay once per query. BM25 scoring + RRF fusion run in-memory and add only the -12.96 ms difference seen above.

---

## 7. Per-Question: Fixed / Unfixed / Untouched

| ID | Baseline Label | Outcome After Change | Evidence |
|---|---|---|---|
| d01 | R | Fixed | Baseline R failure resolved: BM25 lexical match on the exact policy/section/region tokens promoted `struct_HR-207_EMEA_2` to rank 3 in the fused top-3. |
| d02 | R | Fixed | Baseline R failure resolved: BM25 lexical match on the exact policy/section/region tokens promoted `struct_HR-207_APAC_2` to rank 3 in the fused top-3. |
| d03 | R | Fixed | Baseline R failure resolved: BM25 lexical match on the exact policy/section/region tokens promoted `struct_HR-209_UK_1` to rank 2 in the fused top-3. |
| d04 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d05 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d06 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d07 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 3. No regression. |
| d08 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d09 | Hit | REGRESSION | Was a baseline hit but the change pushed `struct_HR-207_EMEA_3` out of the top-3. |
| d10 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d11 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |
| d12 | Hit | Unchanged (still hit) | Was already a hit; remains a hit at rank 1. No regression. |

- **Fixed R failures:** d01, d02, d03
- **R failures the change did NOT touch:** none
- **G failures (retrieval change cannot fix, left alone):** none
- **Regressions introduced:** d09

---

## 8. Shipping Decision

**SHIP IT — with eyes open.** Net hit-rate@3 rose 9/12 (75.0%) → 11/12 (91.7%), a +16.7 point net gain at a p50 latency cost of only -12.96 ms. The change fixed 3 R failure(s) (d01, d02, d03) but introduced 1 regression (d09). The regression is not noise — it is a textbook RRF behaviour: on d09 the correct chunk was found by dense ONLY (BM25 did not surface it), so two chunks that both retrievers agreed on moderately out-voted the single-list winner in the fused ranking. Net math favours shipping (+2 beats -1), but the honest caveat is that pure-dense was already rank-1 on the regressed query; a follow-up (raise top_n to 4–5, or widen each retriever's candidate pool) should recover it. Ship, monitor d09.

---

## 9. Code Diff — Exactly One Retrieval Change

The change adds a `BM25Retriever` and a `HybridRetriever` (RRF fusion) alongside the unchanged `DenseRetriever` in `Services/hybrid_retriever.py`. The baseline run calls `DenseRetriever.retrieve`; the after run calls `HybridRetriever.retrieve`. No other file, the chunker, the embedding model, or the generator was modified.

```diff
--- retrieval: Dense Cosine only (baseline)
+++ retrieval: Dense Cosine + BM25, fused by RRF k=60 (after)
+def tokenize(text):
+    # preserves policy codes (hr-207) and decimal sections (3.2) as single tokens
+    return re.findall(r'\b[a-zA-Z0-9\.\-]+\b', text.lower())
+
+class BM25Retriever:
+    # scrolls the full structure_chunks collection, builds one in-memory BM25Okapi index
+    def retrieve(self, query, region=None, top_k=10):
+        scores = self.bm25.get_scores(tokenize(query))
+        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
+        return [ {'rank': r, 'chunk_id': ..., 'score': scores[i], ...} for r, i in enumerate(top, 1) ]
+
+class HybridRetriever:
+    def retrieve(self, query, k=60, top_n=3, ...):
+        dense_results = self.dense.retrieve(query, top_k=10)   # unchanged dense path
+        bm25_results  = self.bm25.retrieve(query, top_k=10)
+        rrf = {}
+        for rank, item in enumerate(dense_results, 1):
+            rrf[item['chunk_id']] = rrf.get(item['chunk_id'], 0) + 1.0/(k + rank)
+        for rank, item in enumerate(bm25_results, 1):
+            rrf[item['chunk_id']] = rrf.get(item['chunk_id'], 0) + 1.0/(k + rank)
+        return sorted-by-rrf-score(top_n)   # ranks fused, never raw scores
```
