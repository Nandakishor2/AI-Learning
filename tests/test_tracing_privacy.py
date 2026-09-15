import pytest
from src.tracing.privacy import redact_pii, validate_privacy_cleanliness
from src.tracing.trace_manager import TraceManager
from src.config import TRACES_FILE

def test_privacy_redaction():
    raw_query = "My name is John Doe (EMP-9876) and my email is john.doe@example.com. What is my leave balance?"
    clean_text = redact_pii(raw_query)
    
    assert "John Doe" not in clean_text
    assert "EMP-9876" not in clean_text
    assert "john.doe@example.com" not in clean_text
    assert "[REDACTED_EMP_ID]" in clean_text
    assert "[REDACTED_EMAIL]" in clean_text

def test_privacy_cleanliness_validation():
    clean_data = {
        "user": "[REDACTED_EMPLOYEE_NAME]",
        "id": "[REDACTED_EMP_ID]",
        "question": "What is the parental leave policy in North America?"
    }
    pii_count, violations = validate_privacy_cleanliness(clean_data)
    assert pii_count == 0
    assert len(violations) == 0

def test_trace_manager_logs_cleanly(tmp_path):
    tm = TraceManager(trace_file=tmp_path / "test_traces.jsonl")
    record = tm.log_interaction(
        question="What is the leave policy for Jane Smith (EMP-1122)?",
        retrieved_chunks=[{"chunk_id": "struct_HR-207_APAC_4", "score": 0.95}],
        raw_output="Jane Smith has 3 days carry over.",
        final_output="Jane Smith has 3 days carry over.",
        citations=[{"chunk_id": "struct_HR-207_APAC_4"}],
        status="answered",
        latency_ms=120.5
    )
    
    traces = tm.load_traces()
    assert len(traces) == 1
    assert "Jane Smith" not in traces[0]["question"]
    assert "EMP-1122" not in traces[0]["question"]
