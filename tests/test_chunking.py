import pytest
from src.ingestion.chunker import baseline_chunk, structure_aware_chunk

SAMPLE_POLICY = """# HR-207: Regional Leave Policy Addendum - APAC

## 1. Scope and Applicability
Applies to all permanent and probationary staff.

## 3. Carry-Over Rules
### 3.2 Probationary Employee Carry-Over Cap
| Employee Tier | Probation Status | Carry-Over Cap (Days) | Forfeiture Window |
|---|---|---|---|
| Tier 1 Staff | In Probation (<6 mos) | 3 | 60 days post-probation |
| Tier 2 Leads | In Probation (<6 mos) | 5 | 90 days post-probation |
"""

def test_structure_aware_chunker_preserves_tables_and_headers():
    chunks = structure_aware_chunk(SAMPLE_POLICY)
    
    # Assert section numbers are extracted
    sections = [c["section"] for c in chunks]
    assert "3.2" in sections or "3" in sections
    
    # Assert table rows remain intact inside the section chunk
    table_chunk = next(c for c in chunks if "Tier 1 Staff" in c["text"])
    assert "Tier 2 Leads" in table_chunk["text"]
    assert "HR-207" in table_chunk["text"]

def test_baseline_chunker_splits_arbitrarily():
    chunks = baseline_chunk(SAMPLE_POLICY, chunk_size=150, overlap=20)
    assert len(chunks) > 1
