from dataclasses import dataclass
from typing import List, Dict

@dataclass
class IngestionValidationReport:
    total_files: int
    total_chunks: int
    chunks_missing_source_file: int
    chunks_missing_policy_id: int
    chunks_missing_region: int
    chunks_missing_effective_date: int
    chunks_missing_section: int
    is_valid: bool

    def to_dict(self) -> Dict:
        return {
            "total_files": self.total_files,
            "total_chunks": self.total_chunks,
            "chunks_missing_source_file": self.chunks_missing_source_file,
            "chunks_missing_policy_id": self.chunks_missing_policy_id,
            "chunks_missing_region": self.chunks_missing_region,
            "chunks_missing_effective_date": self.chunks_missing_effective_date,
            "chunks_missing_section": self.chunks_missing_section,
            "is_valid": self.is_valid
        }

def validate_chunks(chunks: List[Dict], total_files: int = 6) -> IngestionValidationReport:
    """
    Validates that all chunks contain mandatory metadata fields.
    Hard requirement: chunks_missing_source_file == 0.
    """
    missing_source = 0
    missing_policy = 0
    missing_region = 0
    missing_effective = 0
    missing_section = 0

    for ch in chunks:
        payload = ch.get("payload", ch)
        if not payload.get("source_file"):
            missing_source += 1
        if not payload.get("policy_id") or payload.get("policy_id") == "UNKNOWN":
            missing_policy += 1
        if not payload.get("region") or payload.get("region") == "UNKNOWN":
            missing_region += 1
        if not payload.get("effective_date") or payload.get("effective_date") == "UNKNOWN":
            missing_effective += 1
        if not payload.get("section"):
            missing_section += 1

    is_valid = (missing_source == 0 and missing_policy == 0 and missing_region == 0 and missing_effective == 0)
    
    return IngestionValidationReport(
        total_files=total_files,
        total_chunks=len(chunks),
        chunks_missing_source_file=missing_source,
        chunks_missing_policy_id=missing_policy,
        chunks_missing_region=missing_region,
        chunks_missing_effective_date=missing_effective,
        chunks_missing_section=missing_section,
        is_valid=is_valid
    )
