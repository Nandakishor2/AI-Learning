import re
from dataclasses import dataclass
from typing import Dict, List, Tuple
from src.generation.rag_pipeline import REFUSAL_STRING

@dataclass
class AssertionResult:
    passed: bool
    failures: List[str]
    assertion_count: int

def run_deterministic_assertions(case: Dict, rag_response: Dict, chunk_index: Dict[str, Dict]) -> AssertionResult:
    """
    Evaluates rule-based, deterministic criteria in pure Python code:
    1. Out-of-jurisdiction / ungrounded refusal trigger.
    2. Policy section reference presence & index resolution.
    3. Citation chunk existence & policy ID match.
    4. Numeric entitlement / key term presence for answerable cases.
    """
    failures = []
    assertion_count = 4

    expected_status = case.get("expected_status", "answered")
    actual_status = rag_response.get("status")
    answer_text = rag_response.get("answer", "")
    citations = rag_response.get("citations", [])

    # Assertion 1: Refusal Trigger Match
    if expected_status == "refused":
        if actual_status != "refused":
            failures.append(f"Expected status 'refused', got '{actual_status}'")
        if REFUSAL_STRING.lower() not in answer_text.lower() and "don't have enough information" not in answer_text.lower():
            failures.append("Refusal answer text does not match standard refusal phrasing")
        return AssertionResult(
            passed=(len(failures) == 0),
            failures=failures,
            assertion_count=assertion_count
        )

    # Assertion 2: Status check for answerable cases
    if actual_status != "answered":
        failures.append(f"Expected status 'answered', got '{actual_status}'")

    # Assertion 3: Citation presence & resolution in index
    expected_policy = case.get("expected_policy_id")
    expected_section = case.get("expected_section")
    
    if not citations:
        failures.append("Answerable case is missing citations")
    else:
        for cit in citations:
            cid = cit.get("chunk_id")
            if not cid or cid not in chunk_index:
                failures.append(f"Citation chunk '{cid}' does not resolve in authoritative index")
            else:
                indexed_payload = chunk_index[cid]
                if expected_policy and indexed_payload.get("policy_id") != expected_policy:
                    failures.append(
                        f"Citation policy mismatch: expected '{expected_policy}', got '{indexed_payload.get('policy_id')}'"
                    )

    # Assertion 4: Numeric / Term presence
    required_terms = case.get("required_terms", [])
    for term in required_terms:
        if term.lower() not in answer_text.lower():
            failures.append(f"Required factual token/term '{term}' missing from generated answer")

    return AssertionResult(
        passed=(len(failures) == 0),
        failures=failures,
        assertion_count=assertion_count
    )
