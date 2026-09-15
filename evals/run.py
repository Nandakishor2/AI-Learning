import sys
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.evals.eval_runner import run_evaluation_suite

def main():
    judge_ver = "v2"
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["v1", "v2"]:
        judge_ver = sys.argv[1].lower()
    run_evaluation_suite(judge_version=judge_ver)

if __name__ == "__main__":
    main()
