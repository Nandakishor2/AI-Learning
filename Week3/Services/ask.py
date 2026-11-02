import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from Services.rag_engine import answer_query

def print_banner():
    print("\n" + "=" * 65)
    print("      GLOBAL HR LEAVE POLICY RAG ASSISTANT - INTERACTIVE CLI")
    print("=" * 65)
    print("Ask any question across all regional leave policy documents.")
    print("Type 'exit' or 'q' anytime to quit.\n")

def process_question(question: str):
    print("\n" + "-" * 65)
    print("🔎 Searching across all regional policies...")
    print("-" * 65)
    
    # Unrestricted query across all documents
    result = answer_query(question, region=None)
    
    print("\n📚 RETRIEVED SOURCES:")
    if result.get("top_sources"):
        for i, (policy, reg) in enumerate(result["top_sources"], 1):
            print(f"   [{i}] Policy: {policy} | Region: {reg}")
    else:
        print("   No matching source chunks found.")
        
    print("\n💬 ASSISTANT ANSWER:")
    print("-" * 65)
    print(result["answer"])
    print("-" * 65)

def interactive_loop():
    print_banner()
    while True:
        try:
            print("\n" + "=" * 65)
            question = input("📝 Enter your question: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!\n")
                break
                
            process_question(question)
            
        except KeyboardInterrupt:
            print("\n\nSession ended by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")

def main():
    parser = argparse.ArgumentParser(description="Ask questions to Global HR Leave Policy RAG Assistant")
    parser.add_argument("question", nargs="?", type=str, help="Question to ask (optional; starts interactive mode if omitted)")
    
    args = parser.parse_args()
    
    if args.question:
        process_question(args.question)
    else:
        interactive_loop()

if __name__ == "__main__":
    main()
