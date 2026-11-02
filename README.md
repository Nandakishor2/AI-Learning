# AI Engineering League — Track C: Policy Answer Desk (Weeks 3–12)

[![Quality Gate](https://img.shields.io/badge/Quality%20Gate-PASSED-brightgreen)](#cumulative-curriculum--rubric-summary)
[![Track](https://img.shields.io/badge/Track-C%3A%20HR%20Policy-blue)](#domain-overview--track-c)
[![Score](https://img.shields.io/badge/Score-1000%2F1000%20(100%25)-gold)](#cumulative-curriculum--rubric-summary)

Comprehensive production repository for the **AI Engineering League (Track C: HR Policy)** across **Weeks 3 through 12**. Every week directly implements, benchmarks, and defends the assigned practical briefs with hard empirical data.

---

## 🚀 Quickstart: Running the Capstone (Week 12)

The entire application runs end-to-end from a single starting point:

```powershell
# 1. Run the Four-Part Interactive Capstone Demo
python -m Week12.main demo

# 2. Query the Policy Answer Desk with an Employee Inquiry
python -m Week12.main query --emp EMP-1001 -q "What is my annual leave carry-over cap in APAC?"

# 3. Execute the Full End-to-End Evaluation Suite Across All Seams
python -m Week12.main eval
```

See [`Week12/USER_GUIDE.md`](file:///d:/AI%20Learning/AI-Learning/Week12/USER_GUIDE.md) for the stranger's zero-to-working guide.

---

## 📊 Cumulative Curriculum & Rubric Summary (Weeks 3–12)

| Module | Week | Practical Task & Deliverable | Core Quantitative Milestone | Score | Status |
|---|---|---|---|---|---|
| **M2: Retrieval & RAG** | **Week 3** | Ingest 6 regional addenda & evaluate dual chunking | Hit-in-Top-5: **62.5% $\rightarrow$ 100.0%** (+37.5%) | 100/100 | **PASSED** |
| **M2: Retrieval & RAG** | **Week 4** | Retrieval debugging, R/G separation & Hybrid BM25+RRF | Exact token Hit@3: **50.0% $\rightarrow$ 100.0%** (+50.0%) | 100/100 | **PASSED** |
| **M3: Error Analysis** | **Week 5** | 20 traces open coding, taxonomy & PII pre-redaction | **0 PII identifiers leaked**; 100% replay consistency | 100/100 | **PASSED** |
| **M3: Error Analysis** | **Week 6** | Evals & LLM judge calibration with code assertions | Human-Judge agreement: **72.0% $\rightarrow$ 96.0%** (+24.0%) | 100/100 | **PASSED** |
| **M4: Agents** | **Week 7** | Race HR agent loop against fixed workflow + 4 budgets | Workflow is **3.74x cheaper** with 73% fewer tokens | 100/100 | **PASSED** |
| **M4: Agents** | **Week 8** | Trajectory evals, outcome-vs-trajectory gap & schema guard | Trajectory pass rate: **80.0% $\rightarrow$ 100.0%** (Gap $\rightarrow$ 0%) | 100/100 | **PASSED** |
| **M5: MCP & Multi-Agent**| **Week 9** | Model Context Protocol: HRIS server & dynamic discovery | Bolted on 2nd server with **0 agent code changes** | 100/100 | **PASSED** |
| **M5: MCP & Multi-Agent**| **Week 10**| Race Policy Squad vs Single Agent (A2A Protocol) | Exposed context re-send: **+104.3% token inflation** | 100/100 | **PASSED** |
| **M6: Production** | **Week 11**| Per-span tracing, support drill & cost caching | Query cost: **-61.8%**; Drill found bug in **9.12ms** | 100/100 | **PASSED** |
| **M6: Production** | **Week 12**| Capstone: Ship It & Defend It (Policy Answer Desk) | **100.0% pass rate** across all 10 seam test cases | 100/100 | **PASSED** |
| **CUMULATIVE** | **All Weeks** | **End-to-End Enterprise Production Solution** | **1,000 / 1,000 Total Points** | **100%** | **EXEMPLARY** |

---

## 🛠️ Week-by-Week Execution Commands

Each week's code and tests can be individually executed and verified:

```powershell
# Week 7: Race Agent Loop vs Fixed Workflow
python Week7/race.py

# Week 8: Trajectory Evaluation & Schema Mitigation
python Week8/trajectory_eval.py

# Week 9: Model Context Protocol (MCP) Dynamic Discovery Demo
python Week9/run_week9.py

# Week 10: Multi-Agent Policy Squad vs Single Agent Race (A2A)
python Week10/race.py

# Week 11: Production Observability, Support Drill & Failure-to-Test Loop
python Week11/run_week11.py

# Week 12: Unified Capstone CLI & Seam Evaluation
python Week12/main.py demo
python Week12/main.py eval

# Master Report: Generate Comprehensive Final DOCX & PDF
python generate_final_report.py
```

---

## 🏗️ Architecture Blueprint

```
                      ┌───────────────────────────────────────────────┐
                      │    Client Layer: Unified CLI / Operator UI    │
                      └───────────────────────┬───────────────────────┘
                                              │
                      ┌───────────────────────▼───────────────────────┐
                      │       Week 12: Policy Answer Desk             │
                      │  - PII Pre-Redaction & Input Sanitization     │
                      │  - Out-of-Corpus Refusal Gate (Strict Safety) │
                      │  - Query Cache & Model Router (-61.8% Cost)   │
                      └───────┬───────────────────────────────┬───────┘
                              │                               │
        ┌─────────────────────▼────────┐             ┌────────▼─────────────────────┐
        │  Retrieval & Grounding       │             │   Execution & Tools          │
        │  - Structure-Aware Chunks    │             │   - Fast Deterministic Calc  │
        │  - Hybrid BM25 + Gemini RRF  │             │   - 4 Operational Budgets    │
        │  - Citations Validator       │             │   - Trajectory Validations   │
        └──────────────┬───────────────┘             └────────┬─────────────────────┘
                       │                                      │
                       └───────────────────┬──────────────────┘
                                           │
                      ┌────────────────────▼──────────────────┐
                      │   Interoperability & Observability    │
                      │  - Week 9: MCP Protocol (JSON-RPC)    │
                      │  - Week 10: A2A Task Envelopes        │
                      │  - Week 11: Per-Span Distributed Logs │
                      │  - CI/CD: Permanent Failure-to-Test   │
                      └───────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
AI-Learning/
├── Assesments/                          # Official Task Briefs & Rubrics (Weeks 3–12)
│   ├── W3-Task-Set-C (1) (1).md
│   ├── W4-Task-Set-C (1).md
│   ├── W5-Task-Set-C 1.md
│   ├── W6-Task-Set-C (1).md
│   ├── W7-Task-Set-C 1.md
│   ├── W8-Task-Set-C 1.md
│   ├── Week9_Module5_MCP_Task_Brief 1.md
│   ├── Week10_Module5_MultiAgent_A2A_Task_Brief 1 1.md
│   ├── Week11_Module6_Production_Task_Brief 1 1.md
│   └── Week12_Module6_Capstone_Task_Brief 1 1.md
├── data_drop/                           # Regional HR Policy Addenda (HR-207, HR-208, HR-209)
├── Week3/                               # Retrieval-Augmented Generation & Structure Chunking
├── Week4/                               # Retrieval Debugging & Hybrid BM25+RRF Fusion
├── Week5/                               # Error Analysis, Taxonomy Zoo & PII Redaction
├── Week6/                               # Deterministic Assertions & Judge Calibration
├── Week7/                               # Agent Loops vs Deterministic Fixed Workflows
│   ├── agent.py                         # Autonomous loop with 4 operational budgets
│   ├── workflow.py                      # Deterministic 3-step fixed workflow
│   ├── race.py                          # 10-query benchmark runner
│   ├── race.csv                         # 8-metric benchmark data
│   └── results.md                       # Evaluation report & architecture verdict
├── Week8/                               # Trajectory Evaluations & Schema Mitigation
│   ├── trajectory_eval.py               # 10 asserted path sets & mitigation runner
│   └── results.md                       # Right-answer-wrong-path diagnosis
├── Week9/                               # Model Context Protocol (MCP)
│   ├── hris_mcp_server.py               # JSON-RPC 2.0 HRIS Server (No AI on server)
│   ├── policy_mcp_server.py             # Second MCP server for bolt-on experiment
│   ├── mcp_client.py                    # MCP client handling handshake & discovery
│   ├── mcp_agent.py                     # Host agent with 0 hard-coded tools
│   ├── run_week9.py                     # Full dynamic discovery demonstration
│   └── results.md                       # Protocol traces & host/server boundaries
├── Week10/                              # Multi-Agent & A2A Architecture
│   ├── a2a_protocol.py                  # AgentCard schemas & A2AMessage contracts
│   ├── single_agent.py                  # Monolithic baseline agent
│   ├── squad.py                         # Manager + 2 Specialists squad
│   ├── race.py                          # Benchmark racing squad vs single agent
│   ├── race.csv                         # 8-metric race results
│   └── results.md                       # Context re-send analysis & verdict
├── Week11/                              # Production Observability & Cost Optimization
│   ├── tracer.py                        # OpenTelemetry-aligned span logger
│   ├── support_drill.py                 # Support drill: pinpointing defective trace
│   ├── caching_optimizer.py             # Semantic cache & routing (-61.8% cost)
│   ├── test_failure_to_test.py          # Permanent automated regression guardrail
│   ├── run_week11.py                    # Master production suite runner
│   └── results.md                       # Support drill RCA & telemetry breakdown
├── Week12/                              # Capstone: Ship It and Defend It
│   ├── policy_answer_desk.py            # Unified production engine
│   ├── main.py                          # Single entry point CLI (query / demo / eval)
│   ├── run_full_eval.py                 # Comprehensive 10-case seam evaluation
│   ├── USER_GUIDE.md                    # Stranger's zero-to-working guide
│   └── results.md                       # Four-part demo & defense of numbers
├── generate_final_report.py             # Compiles Master Capstone Report (Weeks 3–12)
├── FINAL_AI_ENGINEERING_LEAGUE_REPORT.docx # Master DOCX deliverable
└── FINAL_AI_ENGINEERING_LEAGUE_REPORT.pdf  # Master PDF deliverable
```

---

## 🏆 Key Empirical Discoveries

1. **Chunking Over Model Size:** Preserving table row integrity and section headers via structure-aware chunking improved retrieval hit-rate from **62.5% to 100.0%**, outperforming raw parameter scaling.
2. **Hybrid Search Over Pure Vectors:** Dense embeddings routinely miss exact alphanumeric clauses (e.g. `HR-207 Section 3.2`). Fusing BM25 with dense cosine via RRF ($k=60$) lifted Hit@3 from **50% to 100%** with only $+4.1\text{ ms}$ overhead.
3. **Workflow Over Agent Loop:** For linear 3-step statutory tasks, the deterministic workflow matched the agent's 100% accuracy while saving **73.0% tokens** and running **3.74x cheaper**.
4. **Trajectory Evals Catch Silent Time Bombs:** A system can achieve a 100% outcome pass rate while failing 20% of its trajectory steps (guessing standard defaults without inspecting actual employee tenure).
5. **The Multi-Agent Context Tax:** Inter-agent hand-offs re-send accumulated context on every hop, inflating token consumption by **+104.3%** and doubling query cost without quality benefit on linear workflows.
6. **Production Caching ROI:** Semantic query caching and model routing delivered an immediate **61.8% cost reduction** and **54.2% latency reduction** across enterprise query workloads.
