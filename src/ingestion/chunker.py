import re
from typing import List, Dict

def baseline_chunk(text: str, chunk_size: int = 350, overlap: int = 50) -> List[Dict[str, str]]:
    """
    Strategy A: Naive fixed sliding-window chunker.
    Splits purely on character counts without header, table, or section awareness.
    """
    text = text.replace('\r\n', '\n')
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        
        # Best-effort section extraction for baseline metadata
        sec_match = re.search(r'(?:Section\s+|##\s+|###\s+)(\d+(?:\.\d+)?)', chunk_text, re.IGNORECASE)
        section = sec_match.group(1) if sec_match else "GENERAL"
        
        chunks.append({
            "text": chunk_text,
            "section": section
        })
        
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

def extract_section_number(header_text: str) -> str:
    """Extract section identifier like '1', '2', '2.1', '3.2' from header line."""
    match = re.search(r'(\d+(?:\.\d+)?)', header_text)
    return match.group(1) if match else "GENERAL"

def structure_aware_chunk(text: str) -> List[Dict[str, str]]:
    """
    Strategy B: Structure-aware chunker.
    Splits hierarchically on markdown headers (H1/H2/H3), preserves section numbers,
    binds clauses and eligibility tables to their authoritative parent section,
    and prepends the policy title for full retrieval grounding.
    """
    text = text.replace('\r\n', '\n')
    lines = text.split('\n')
    
    doc_title = ""
    current_h2 = ""
    current_section = "1.0"
    current_buffer = []
    chunks = []

    def flush_buffer(sec_num: str, buffer_lines: List[str]):
        if not buffer_lines:
            return
        content = "\n".join(buffer_lines).strip()
        if not content:
            return
        
        # Prepend doc title and H2 if not already present in buffer
        header_prefix = []
        if doc_title and not content.startswith(doc_title):
            header_prefix.append(doc_title)
        if current_h2 and current_h2 != doc_title and current_h2 not in content:
            header_prefix.append(current_h2)
            
        if header_prefix:
            full_text = "\n\n".join(header_prefix) + "\n\n" + content
        else:
            full_text = content
            
        chunks.append({
            "text": full_text,
            "section": sec_num
        })

    for line in lines:
        if line.startswith("# "):
            # Document Title
            flush_buffer(current_section, current_buffer)
            current_buffer = []
            doc_title = line.strip()
            current_section = "1.0"
        elif line.startswith("## "):
            # H2 Section Header
            flush_buffer(current_section, current_buffer)
            current_buffer = [line]
            current_h2 = line.strip()
            current_section = extract_section_number(line)
        elif line.startswith("### "):
            # H3 Subsection Header (e.g., ### 3.2 Probationary Employee Carry-Over Cap)
            flush_buffer(current_section, current_buffer)
            current_buffer = [line]
            current_section = extract_section_number(line)
        else:
            current_buffer.append(line)

    flush_buffer(current_section, current_buffer)
    return chunks
