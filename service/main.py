#!/usr/bin/env python3
"""
Legal Assistant Agent - Main Entry Point

Commands:
    python main.py build    - Build vector index from CUAD dataset
    python main.py run      - Run interactive agent
    python main.py eval     - Run evaluation
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Disable tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
INDEX_PATH = DATA_DIR / "embeddings" / "faiss_index"


def build_index(max_contracts: int = 20):
    """Build vector index from CUAD dataset."""
    from utils import get_embedder, build_vectorstore, save_vectorstore, load_documents

    print("Building vector index...")
    texts, metadatas = load_documents(str(DATA_DIR), max_contracts=max_contracts)

    print("Creating embeddings...")
    embedder = get_embedder()
    vector_db = build_vectorstore(texts, metadatas, embedder)

    print(f"Saving index to {INDEX_PATH}...")
    save_vectorstore(vector_db, str(INDEX_PATH))
    print("Done!")


def run_agent():
    """Run interactive legal assistant."""
    from utils import get_embedder, load_vectorstore
    from agents import build_graph, run_query, format_response

    print("=" * 60)
    print("    LEGAL ASSISTANT AGENT")
    print("=" * 60)

    # Load vector store
    vector_db = None
    if INDEX_PATH.exists():
        print("\nLoading knowledge base...")
        embedder = get_embedder()
        vector_db = load_vectorstore(str(INDEX_PATH), embedder)
        print("Knowledge base loaded!")
    else:
        # print(f"\nNo index found. Run 'python main.py build' first.")
        print("\nNo index found. Run 'python main.py build' first.")
        return

    # Build agent
    print("\nInitializing agents...")
    app = build_graph(vector_db=vector_db)
    print("Ready!\n")

    # Interactive loop
    print("Type your question (or 'quit' to exit):")
    print("-" * 60)

    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break
        if not query:
            continue

        print("\nProcessing...")
        result = run_query(app, query)
        print(format_response(result))


def run_evaluation():
    """Run evaluation metrics."""
    from utils import get_embedder, load_vectorstore
    from agents import build_graph, run_query
    from evaluation.metrics import evaluate_agent_response, EvaluationRunner, print_evaluation_report

    if not INDEX_PATH.exists():
        print("No index found. Run 'python main.py build' first.")
        return

    embedder = get_embedder()
    vector_db = load_vectorstore(str(INDEX_PATH), embedder)
    app = build_graph(vector_db=vector_db)

    queries = [
        "What are the termination conditions?",
        "Explain the indemnification clause.",
        "Are there non-compete restrictions?",
    ]

    runner = EvaluationRunner()
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Evaluating: {query}")
        print("-" * 60)
        result = run_query(app, query)
        eval_result = evaluate_agent_response(
            query=query,
            retrieved_docs=result["retrieved_documents"],
            reasoning_chain=result["reasoning_chain"],
            final_explanation=result["final_explanation"]
        )
        runner.add_result(eval_result)

        # Print detailed report for each query
        print(print_evaluation_report(eval_result, verbose=True))
        print("\n")

    # Print aggregate summary at the end
    print("\n" + "=" * 60)
    print("FINAL AGGREGATE SUMMARY")
    print("=" * 60)
    print(runner.print_summary())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "build":
        max_contracts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        build_index(max_contracts)
    elif command == "run":
        run_agent()
    elif command == "eval":
        run_evaluation()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
