import pytest
from src.evals.dataset import get_eval_cases
from src.evals.deterministic_assertions import run_deterministic_assertions
from src.config import get_qdrant_client, STRUCTURE_COLLECTION

def test_eval_dataset_case_count_and_tagging():
    cases = get_eval_cases()
    assert len(cases) >= 25, f"Expected at least 25 evaluation cases, got {len(cases)}"
    
    # Assert every case has a taxonomy mode
    for c in cases:
        assert "taxonomy_mode" in c and c["taxonomy_mode"], f"Case {c.get('case_id')} missing taxonomy_mode"
        assert "expected_behavior" in c and c["expected_behavior"], f"Case {c.get('case_id')} missing expected_behavior"

def test_deterministic_assertions():
    qdrant = get_qdrant_client()
    records, _ = qdrant.scroll(collection_name=STRUCTURE_COLLECTION, limit=500, with_payload=True, with_vectors=False)
    chunk_index = {p.payload.get("chunk_id"): p.payload for p in records}

    # Test Answerable case assertion
    valid_answerable_case = {
        "case_id": "TEST-01",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.2",
        "required_terms": ["3 days", "Tier 1"]
    }
    mock_rag_res = {
        "status": "answered",
        "answer": "Tier 1 staff in APAC receive 3 days carry-over under HR-207 Section 3.2.",
        "citations": [{"chunk_id": "struct_HR-207_APAC_4", "policy_id": "HR-207", "section": "3.2"}]
    }
    res = run_deterministic_assertions(valid_answerable_case, mock_rag_res, chunk_index)
    assert res.passed is True
    assert res.assertion_count == 4

    # Test Refusal case assertion
    refusal_case = {
        "case_id": "TEST-02",
        "expected_status": "refused",
        "required_terms": ["don't have enough information"]
    }
    mock_refusal_res = {
        "status": "refused",
        "answer": "I don't have enough information in the provided HR policy documents to answer that.",
        "citations": []
    }
    res_ref = run_deterministic_assertions(refusal_case, mock_refusal_res, chunk_index)
    assert res_ref.passed is True
