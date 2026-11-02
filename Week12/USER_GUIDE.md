# Policy Answer Desk — User & Operator Guide

> **Welcome to the Policy Answer Desk (Track C Capstone).**  
> This guide is written for a first-time operator or evaluator. Follow these simple steps to go from zero to a verified, citations-backed HR policy answer in under 2 minutes.

---

## 1. Prerequisites & Environment

1. **Python:** Python 3.10+ (Tested on Python 3.11).
2. **Terminal:** PowerShell, Command Prompt, or Bash.
3. **Repository Directory:** Ensure you are in the project root directory:
   ```powershell
   cd "D:\AI Learning\AI-Learning"
   ```

---

## 2. Quickstart: 3 Essential Commands

### Command 1: Run the Interactive Four-Part Capstone Demo
Experience the complete demo showing a live run, a caught and handled failure, quantitative improvements, and architecture defenses:
```powershell
python -m Week12.main demo
```

### Command 2: Query the Policy Answer Desk Directly
Submit an employee inquiry from the command line:
```powershell
python -m Week12.main query --emp EMP-1001 --query "What is my annual leave carry-over cap in APAC?"
```

**Expected JSON Response:**
```json
{
  "trace_id": "trace-desk-7a19bc8f",
  "status": "COMPLETED",
  "answer": "Alice Chen (Tier 1 Staff, APAC) has an annual leave carry-over cap of 3 days under HR-207 Section 3.2.",
  "citations": [
    "HR-207 Section 3.2"
  ],
  "duration_ms": 1.15,
  "cost_usd": 0.000185,
  "cached": false
}
```

### Command 3: Execute the Full End-to-End Evaluation Suite
Run all 10 automated test cases spanning retrieval, citations, refusal safety, and regression checks:
```powershell
python -m Week12.main eval
```

---

## 3. Supported Employee Test Profiles

You can query the desk with any of the following pre-indexed employee profiles:

| Employee ID | Name | Jurisdiction | Tier | Probationary? | Key Policy Focus |
|---|---|---|---|---|---|
| `EMP-1001` | Alice Chen | APAC | Tier 1 Staff | True | HR-207 Sec 3.2: 3 days carry-over |
| `EMP-1002` | Bob Smith | APAC | Tier 2 Lead | True | HR-207 Sec 3.2: 5 days carry-over |
| `EMP-1003` | Clara Dupont | EMEA | All Tiers | True | HR-207 Sec 3.2: Strictly 0 days carry-over |
| `EMP-1004` | David Miller | NA | Standard | False | HR-208 Sec 2.1: 14 weeks caregiver leave |
| `EMP-1005` | Elena Gomez | LATAM | Category B | False | HR-208 Sec 2.1: 12 weeks caregiver leave |
| `EMP-1006` | Frank Wright | UK | Standard | False | HR-209 Sec 4.1: GP Fit Note required for >7 days |
| `EMP-1007` | Grace Hopper | ANZ | Year 2+ | False | HR-209 Sec 5.2: 8 days carer conversion cap |

---

## 4. Safety & Refusal Contract

If an inquiry requests policies outside the 6 regional addenda (such as sabbaticals, equity stock vesting, or car leases), the system strictly triggers its **Refusal Guardrail**:
```plaintext
Query: "Can I take a 1-year sabbatical leave?"
Response Status: REFUSED
Answer: "I don't have enough information in the provided HR policy documents to answer that."
Citations: []
```
*Zero speculation. Zero hallucination. 100% auditable compliance.*

---

## 5. Troubleshooting & FAQ

- **Q: Where are the execution logs stored?**  
  A: Every query appends a structured telemetry trace with fine-grained per-step spans to [`Week11/production_traces.jsonl`](file:///d:/AI%20Learning/AI-Learning/Week11/production_traces.jsonl).
- **Q: Can I run queries without providing `--emp`?**  
  A: Yes! The system's entity resolution step automatically extracts employee IDs matching `EMP-XXXX` from the natural language query text.

