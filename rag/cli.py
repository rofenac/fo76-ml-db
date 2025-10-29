#!/usr/bin/env python3
"""
Interactive CLI for Hybrid RAG System

Combines SQL and Vector search for the best of both worlds!
"""

import os
import sys
from hybrid_query_engine import HybridFalloutRAG


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print("  🎮 FALLOUT 76 HYBRID BUILD ASSISTANT 🎮")
    print("=" * 70)
    print("\n🧠 Powered by:")
    print("   • SQL Database (exact queries)")
    print("   • Vector Search (conceptual queries)")
    print("   • Claude AI (intelligent responses)")
    print("\n💡 Try asking:")
    print("   • 'What's the damage of the Gauss Shotgun?' (SQL)")
    print("   • 'Best bloodied heavy gunner build' (Vector)")
    print("   • 'Mutations that work with stealth rifles' (Vector)")
    print("   • 'Weapons similar to The Fixer' (Vector)")
    print("\n📋 Commands:")
    print("   • Type your question and press Enter")
    print("   • Type 'exit', 'quit', or 'q' to leave")
    print("   • Type 'clear' to reset conversation history")
    print("=" * 70 + "\n")


def main():
    """Main interactive loop"""
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")
    engine = None

    try:
        # Initialize hybrid engine
        engine = HybridFalloutRAG(chroma_path)

        print_banner()

        # Interactive loop
        while True:
            try:
                # Get user input
                question = input("💬 You: ").strip()

                # Handle commands
                if not question:
                    continue

                if question.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Thanks for using the Fallout 76 Build Assistant!")
                    print("   Happy wasteland wandering! ☢️\n")
                    break

                if question.lower() == 'clear':
                    engine.conversation_history = []
                    print("\n✅ Conversation history cleared!\n")
                    continue

                # Process question
                print()  # Blank line for readability
                answer, method = engine.ask(question)

                # Display answer with method indicator
                if method == "SQL":
                    method_emoji = "🔍"
                    method_label = "SQL Search"
                elif method == "HYBRID":
                    method_emoji = "🎯"
                    method_label = "Hybrid Search (SQL + Vector)"
                else:
                    method_emoji = "🧠"
                    method_label = "Vector Search"

                print(f"\n{method_emoji} Assistant [{method_label}]:")
                print("-" * 70)
                print(answer)
                print("\n" + "=" * 70 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!\n")
                break

            except Exception as e:
                print(f"\n❌ Error processing question: {e}")
                print("Please try again.\n")
                continue

    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        print("\nMake sure:")
        print("  1. Vector database exists (run populate_vector_db.py)")
        print("  2. MySQL is running")
        print("  3. Environment variables are set:")
        print("     - OPENAI_API_KEY")
        print("     - ANTHROPIC_API_KEY")
        print("     - DB_PASSWORD (if needed)")
        sys.exit(1)

    finally:
        # Always cleanup resources on exit
        if engine:
            engine.cleanup()


if __name__ == "__main__":
    main()
