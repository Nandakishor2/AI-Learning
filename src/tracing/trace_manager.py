import json
import os
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pathlib import Path
from src.config import TRACES_FILE, GENERATION_MODEL
from src.tracing.privacy import redact_pii, validate_privacy_cleanliness

PROMPT_VERSION = "v1.2.0-hr-grounded-strict"

@dataclass
class TraceRecord:
    trace_id: str
    timestamp: str
    question: str
    prompt_version: str
    retrieved_chunks: List[Dict]
    retrieval_scores: List[float]
    retrieval_strategy: str
    model: str
    model_parameters: Dict
    raw_output: str
    final_output: str
    citations: List[Dict]
    status: str
    latency_ms: float

class TraceManager:
    def __init__(self, trace_file: Path = TRACES_FILE):
        self.trace_file = Path(trace_file)
        os.makedirs(self.trace_file.parent, exist_ok=True)

    def log_interaction(
        self,
        question: str,
        retrieved_chunks: List[Dict],
        raw_output: str,
        final_output: str,
        citations: List[Dict],
        status: str,
        latency_ms: float,
        retrieval_strategy: str = "dense",
        model: str = GENERATION_MODEL,
        model_params: Optional[Dict] = None,
        trace_id: Optional[str] = None,
    ) -> TraceRecord:
        # Pre-redact user question, outputs, and any employee identifiers
        clean_question = redact_pii(question)
        clean_raw = redact_pii(raw_output)
        clean_final = redact_pii(final_output)
        
        chunk_summaries = [
            {"chunk_id": c.get("chunk_id"), "score": float(c.get("score", 0.0))}
            for c in retrieved_chunks
        ]
        scores = [float(c.get("score", 0.0)) for c in retrieved_chunks]

        record = TraceRecord(
            trace_id=trace_id or f"trace_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            question=clean_question,
            prompt_version=PROMPT_VERSION,
            retrieved_chunks=chunk_summaries,
            retrieval_scores=scores,
            retrieval_strategy=retrieval_strategy,
            model=model,
            model_parameters=model_params or {"temperature": 0.0, "top_p": 0.95},
            raw_output=clean_raw,
            final_output=clean_final,
            citations=citations,
            status=status,
            latency_ms=round(latency_ms, 2)
        )

        # Validate that no unredacted PII remains
        record_dict = asdict(record)
        pii_count, violations = validate_privacy_cleanliness(record_dict)
        if pii_count > 0:
            raise ValueError(f"Privacy validation failed before write! Violations: {violations}")

        # Append to JSONL file
        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record_dict) + "\n")

        return record

    def load_traces(self) -> List[Dict]:
        if not self.trace_file.exists():
            return []
        traces = []
        with open(self.trace_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    traces.append(json.loads(line))
        return traces
