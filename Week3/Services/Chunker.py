import re

def baseline_chunk(text: str, chunk_size: int = 350, overlap: int = 50) -> list[str]:
    """Strategy A: Naive fixed sliding-window chunker."""
    text = text.replace('\r\n', '\n')
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
    Splits by markdown headers or numbered sections (for PDFs), while maintaining
    the document title hierarchy, policy numbers, and keeping eligibility tables intact.
    """
    text = text.replace('\r\n', '\n')
    
    # Check if text contains markdown headers '# ' or '## '
    has_markdown_headers = bool(re.search(r'\n#{1,3}\s', text)) or text.startswith('# ')
    
    if has_markdown_headers:
        sections = re.split(r'\n(?=#{1,3}\s)', text)
    else:
        # Fallback for plain text / PDF extracts: split on numbered sections like "1. Scope", "3.2 Probationary..."
        # Requires mandatory period after section number so table numbers like "60 days" are not split.
        sections = re.split(r'\n(?=(?:Section\s+\d+|\d+\.(?:\d+)*\s+[A-Z]))', text)
        
    structured_chunks = []
    current_doc_title = ""
    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        
        # Identify title line from markdown header (# ...) or policy code line (HR-xxx: ...)
        title_match = re.search(r"(?:^#\s*(.+)|^((?:HR-\d+[:\s])[^\n]+))", sec, re.MULTILINE)
        if title_match and not current_doc_title:
            current_doc_title = (title_match.group(1) or title_match.group(2)).strip()
            # If sec only contained title/metadata, don't necessarily need a separate chunk unless it has body
            sec_lines = [l for l in sec.split("\n") if not l.startswith("Source File:") and not l.startswith("Policy Id:") and not l.startswith("Region:") and not l.startswith("Effective Date:")]
            if len(sec_lines) > 1:
                structured_chunks.append(sec)
        else:
            # Anchor parent title and policy context to sub-clauses
            full_chunk = f"{current_doc_title}\n\n{sec}" if current_doc_title else sec
            structured_chunks.append(full_chunk)
            
    if not structured_chunks and text.strip():
        structured_chunks.append(text.strip())
        
    return structured_chunks