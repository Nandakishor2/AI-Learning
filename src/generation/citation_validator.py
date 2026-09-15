import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
from src.config import get_qdrant_client, STRUCTURE_COLLECTION

@dataclass
class CitationValidationResult:
    is_valid: bool
    total_citations: int
    valid_citations: int
    invalid_citations: int
    errors: List[str]
    citations: List[Dict]

class CitationValidator:
    def __init__(self, collection_name: str = STRUCTURE_COLLECTION):
        self.collection_name = collection_name
        self.qdrant_client = get_qdrant_client()
        
        # Load all points into a chunk map for fast lookup
        records, _ = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            limit=500,
            with_payload=True,
            with_vectors=False
        )
        self.chunk_index = {p.payload.get("chunk_id"): p.payload for p in records}

    def parse_citations_from_text(self, text: str) -> List[Dict]:
        """
        Parses citations formatted like:
        [Citation: chunk_id=struct_HR-207_APAC_2, policy_id=HR-207, section=3.2, source_file=HR-207_APAC.md]
        or [Policy: HR-207, Section: 3.2, Region: APAC]
        """
        citations = []
        pattern = r'\[Citation:\s*chunk_id=([^,]+),\s*policy_id=([^,]+),\s*section=([^,]+),\s*source_file=([^\]]+)\]'
        matches = re.findall(pattern, text)
        for m in matches:
            citations.append({
                "chunk_id": m[0].strip(),
                "policy_id": m[1].strip(),
                "section": m[2].strip(),
                "source_file": m[3].strip()
            })
        return citations

    def validate_citations(self, citations: List[Dict], answer_text: str = "") -> CitationValidationResult:
        """
        Validates all citations against the authoritative index.
        Rules:
        1. chunk_id must exist in index.
        2. policy_id must match indexed chunk.
        3. section must match indexed chunk.
        4. source_file must match indexed chunk.
        """
        errors = []
        valid_count = 0
        invalid_count = 0

        for c in citations:
            cid = c.get("chunk_id")
            if not cid or cid not in self.chunk_index:
                errors.append(f"Citation chunk_id '{cid}' does not exist in vector index.")
                invalid_count += 1
                continue

            indexed_payload = self.chunk_index[cid]
            if c.get("policy_id") != indexed_payload.get("policy_id"):
                errors.append(
                    f"Policy mismatch for chunk {cid}: citation has '{c.get('policy_id')}', index has '{indexed_payload.get('policy_id')}'"
                )
                invalid_count += 1
                continue

            if c.get("source_file") != indexed_payload.get("source_file"):
                errors.append(
                    f"Source file mismatch for chunk {cid}: citation has '{c.get('source_file')}', index has '{indexed_payload.get('source_file')}'"
                )
                invalid_count += 1
                continue

            valid_count += 1

        is_valid = (invalid_count == 0 and len(citations) > 0) if citations else True
        return CitationValidationResult(
            is_valid=is_valid,
            total_citations=len(citations),
            valid_citations=valid_count,
            invalid_citations=invalid_count,
            errors=errors,
            citations=citations
        )
