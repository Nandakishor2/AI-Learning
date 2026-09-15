import os
from pathlib import Path
from typing import Dict, List, Tuple
from src.config import DATA_DROP_DIR

def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Extract YAML frontmatter metadata and markdown body.
    """
    meta = {}
    body = content
    content = content.replace("\r\n", "\n")
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
    return meta, body

def load_policy_documents(data_dir: Path = None) -> List[Dict]:
    """
    Loads all regional policy addenda markdown files from data_drop directory.
    """
    directory = data_dir or DATA_DROP_DIR
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Policy data directory not found: {directory}")

    files = sorted([f for f in os.listdir(directory) if f.endswith(".md")])
    if len(files) != 6:
        print(f"Warning: Expected exactly 6 policy addenda files, found {len(files)}: {files}")

    documents = []
    for filename in files:
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        meta, body = parse_frontmatter(raw_text)
        
        # Ensure mandatory source_file is always attached
        source_file = meta.get("source_file", filename)
        policy_id = meta.get("policy_id", "UNKNOWN")
        region = meta.get("region", "UNKNOWN")
        effective_date = meta.get("effective_date", "UNKNOWN")

        documents.append({
            "filename": filename,
            "filepath": filepath,
            "source_file": source_file,
            "policy_id": policy_id,
            "region": region,
            "effective_date": effective_date,
            "body": body,
            "raw_text": raw_text
        })

    return documents
