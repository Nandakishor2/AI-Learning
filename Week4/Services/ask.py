import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from Services.rag_engine import answer_query

RETRIEVER_LABELS = {
    "cosine": "Dense Cosine (semantic / meaning-based)",
    "bm25": "BM25 (lexical / exact-keyword)",
    "hybrid": "Hybrid BM25 + Dense fused via RRF (k=60)",
}

def print_banner(retriever: str):
    print("\n" + "=" * 65)
    print("      GLOBAL HR LEAVE POLICY RAG ASSISTANT - INTERACTIVE CLI")
    print("=" * 65)
    print(f"Retriever: {RETRIEVER_LABELS.get(retriever, retriever)}")
    print("Ask any question across all regional leave policy documents.")
    print("Type 'exit' or 'q' anytime to quit.\n")

def process_question(question: str, retriever: str = "hybrid"):
    print("\n" + "-" * 65)
    print(f"🔎 Searching across all regional policies  [retriever: {retriever}]...")
    print("-" * 65)

    # Unrestricted query across all documents
    result = answer_query(question, region=None, retriever=retriever)

    print("\n📚 RETRIEVED SOURCES:")
    if result.get("top_sources"):
        for i, source in enumerate(result["top_sources"], 1):
            if len(source) == 3:
                chunk_id, policy, reg = source
                print(f"   [{i}] Chunk: {chunk_id} | Policy: {policy} | Region: {reg}")
            else:
                policy, reg = source
                print(f"   [{i}] Policy: {policy} | Region: {reg}")
    else:
        print("   No matching source chunks found.")
        
    print("\n💬 ASSISTANT ANSWER:")
    print("-" * 65)
    print(result["answer"])
    print("-" * 65)

def interactive_loop(retriever: str = "hybrid"):
    print_banner(retriever)
    while True:
        try:
            print("\n" + "=" * 65)
            question = input("📝 Enter your question: ").strip()

            if not question:
                continue

            if question.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!\n")
                break

            process_question(question, retriever=retriever)

        except KeyboardInterrupt:
            print("\n\nSession ended by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ask questions to Global HR Leave Policy RAG Assistant")
    parser.add_argument("question", nargs="?", type=str, help="Question to ask (optional; starts interactive mode if omitted)")
    parser.add_argument(
        "-r", "--retriever",
        choices=["cosine", "bm25", "hybrid"],
        default="hybrid",
        help="Retrieval method: cosine (dense only), bm25 (lexical only), or hybrid (BM25+Dense RRF, default)",
    )

    args = parser.parse_args()

    if args.question:
        process_question(args.question, retriever=args.retriever)
    else:
        interactive_loop(retriever=args.retriever)

if __name__ == "__main__":
    main()
