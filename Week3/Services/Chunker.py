import re

def baseline_chunk(text: str, chunk_size: int = 350, overlap: int = 50) -> list[str]:
    """Strategy A: Naive fixed sliding-window chunker."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

def structure_aware_chunk(text: str) -> list[str]:
    """
    Strategy B: Structure-aware chunker.
    Splits by markdown headers while maintaining the header hierarchy,
    policy numbers, and keeping markdown eligibility tables fully intact.
    """
    sections = re.split(r'\n(?=#{1,3}\s)', text)
    structured_chunks = []
    
    current_doc_title = ""
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        if sec.startswith("# "):
            current_doc_title = sec.split("\n", 1)[0]
            if "\n" in sec:
                structured_chunks.append(sec)
        else:
            # Anchor parent title and policy context to sub-clauses
            full_chunk = f"{current_doc_title}\n\n{sec}" if current_doc_title else sec
            structured_chunks.append(full_chunk)
            
    return structured_chunks