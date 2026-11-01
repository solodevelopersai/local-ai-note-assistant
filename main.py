from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from ai_engine import AIEngine
from file_scanner import FileScanner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI-Powered Personal Knowledge Management & Note-Taking Assistant"
    )
    parser.add_argument(
        "--notes-dir",
        default=os.getenv("NOTES_DIRECTORY", "./notes"),
        help="Path to the folder containing your notes and markdown files.",
    )
    parser.add_argument(
        "--query",
        help="Ask a natural-language question over the content of your local notes.",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Generate summaries for each discovered note file.",
    )
    parser.add_argument(
        "--tags",
        action="store_true",
        help="Generate topic tags for each discovered note file.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive Q&A session using your local notes.",
    )
    return parser.parse_args()


def print_note_summary(doc, summary: str) -> None:
    print(f"\n=== {doc.filename} ===")
    print(summary.strip())


def print_note_tags(doc, tags: list[str]) -> None:
    print(f"\n=== Tags for {doc.filename} ===")
    if not tags:
        print("No tags generated.")
        return
    print(", ".join(tags))


def run_interactive_session(engine: AIEngine, documents) -> None:
    print("\nInteractive note assistant ready. Type 'exit' to quit.\n")
    while True:
        question = input("Ask a question about your notes: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            break
        print("\nSearching your knowledge base...\n")
        answer = engine.answer_query(question, documents)
        print(answer.strip())
        print("\n")


def main() -> int:
    load_dotenv()

    args = parse_args()
    notes_dir = os.path.abspath(args.notes_dir)

    if not os.path.exists(notes_dir):
        print(f"The notes directory '{notes_dir}' does not exist.")
        print("Create the directory or pass --notes-dir with a valid path.")
        return 1

    scanner = FileScanner(notes_dir)
    documents = scanner.scan_directory()

    if not documents:
        print(f"No readable text or markdown files were found in: {notes_dir}")
        print("Add .txt, .md, .markdown, or .rst files and try again.")
        return 1

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Missing OPENROUTER_API_KEY in the environment or .env file.")
        print("Copy .env.example to .env and configure your API key.")
        return 1

    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    engine = AIEngine(api_key=api_key, model=model)

    if args.query:
        answer = engine.answer_query(args.query, documents)
        print("\n=== Answer ===")
        print(answer.strip())
        return 0

    if args.summarize:
        print("\n=== Document Summaries ===")
        for doc in documents:
            summary = engine.summarize_note(doc.text)
            print_note_summary(doc, summary)

    if args.tags:
        print("\n=== Tag Generation ===")
        for doc in documents:
            tags = engine.generate_tags(doc.text)
            print_note_tags(doc, tags)

    if args.interactive or not (args.summarize or args.tags):
        run_interactive_session(engine, documents)

    return 0


if __name__ == "__main__":
    sys.exit(main())
