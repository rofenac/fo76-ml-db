#!/usr/bin/env python3
"""Simple CLI for querying Fallout 76 build data"""

from query_engine import FalloutRAG

def main():
    print("=== Fallout 76 Build Assistant ===")
    print("Ask questions about weapons, perks, and armor!")
    print("Type 'exit' to quit\n")

    rag = FalloutRAG()

    while True:
        question = input("You: ").strip()

        if question.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        if not question:
            continue

        print("\nAssistant: ", end="")
        answer = rag.ask(question)
        print(answer)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
