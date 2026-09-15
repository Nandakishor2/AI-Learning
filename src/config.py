import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from qdrant_client import QdrantClient

# Base Directory Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DROP_DIR = ROOT_DIR / "data_drop"
QDRANT_STORAGE_DIR = ROOT_DIR / "qdrant_storage"
TRACES_FILE = ROOT_DIR / "traces.jsonl"
GOLDEN_SET_FILE = ROOT_DIR / "golden_set.jsonl"
LABELS_FILE = ROOT_DIR / "labels_25.json"

# Load Environment Variables (.env)
if (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
elif (ROOT_DIR / "Week3" / ".env").exists():
    load_dotenv(ROOT_DIR / "Week3" / ".env")
elif (ROOT_DIR / "Week4" / ".env").exists():
    load_dotenv(ROOT_DIR / "Week4" / ".env")
else:
    load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Model Names and Hyperparameters
EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 3072
GENERATION_MODEL = "gemini-2.5-flash"
JUDGE_MODEL = "gemini-2.5-flash"

# Collection Names
BASELINE_COLLECTION = "baseline_chunks"
STRUCTURE_COLLECTION = "structure_chunks"

SYSTEM_INSTRUCTION = """You are an authoritative People Operations Policy Assistant.
Your task is to answer employee HR and leave policy questions STRICTLY and SOLELY based on the provided policy context snippets.

STRICT GROUNDING & CITATION RULES:
1. Every factual claim must be backed by a specific citation in the format:
   [Citation: chunk_id=<chunk_id>, policy_id=<policy_id>, section=<section>, source_file=<source_file>]
2. If the user question cannot be directly and completely answered using ONLY the provided policy context, or if the context does not contain the answer, you MUST refuse immediately and exactly with:
   "I don't have enough information in the provided HR policy documents to answer that."
3. NEVER guess, speculate, infer unsupported numbers, or invent policies.
"""

def get_gemini_client() -> genai.Client:
    """Returns an authenticated Gemini client."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=GEMINI_API_KEY)

_qdrant_client_instance = None

def get_qdrant_client(storage_path: Path = None) -> QdrantClient:
    """Returns a shared QdrantClient instance."""
    global _qdrant_client_instance
    if _qdrant_client_instance is None:
        try:
            path = str(storage_path or QDRANT_STORAGE_DIR)
            os.makedirs(path, exist_ok=True)
            _qdrant_client_instance = QdrantClient(path=path)
        except Exception:
            _qdrant_client_instance = QdrantClient(":memory:")
    return _qdrant_client_instance

