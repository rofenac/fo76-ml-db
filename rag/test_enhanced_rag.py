#!/usr/bin/env python3
"""Test script for enhanced RAG system"""

import os
import sys
from query_engine import FalloutRAG
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_specific_query():
    """Test a specific, clear query"""
    print("="*70)
    print("TEST 1: Specific Query (should answer directly)")
    print("="*70)

    rag = FalloutRAG()
    question = "What perks affect the Gauss shotgun?"
    print(f"Question: {question}\n")

    response = rag.ask(question)
    print(f"Response Type: {response['type']}")

    if response['type'] == 'answer':
        print(f"\nAnswer:\n{response['content']}")
    else:
        print(f"\nUnexpected response: {response}")

    print("\n")


def test_vague_query():
    """Test a vague query that should trigger clarification"""
    print("="*70)
    print("TEST 2: Vague Query (should ask for clarification)")
    print("="*70)

    rag = FalloutRAG()
    question = "What is the best weapon?"
    print(f"Question: {question}\n")

    response = rag.ask(question)
    print(f"Response Type: {response['type']}")

    if response['type'] == 'clarification':
        print(f"\nReason: {response['reason']}")
        print("\nClarifying Questions:")
        for i, q in enumerate(response['questions'], 1):
            print(f"  {i}. {q}")
    else:
        print(f"\nUnexpected response: {response}")

    print("\n")


def test_build_query():
    """Test a build-related query"""
    print("="*70)
    print("TEST 3: Build Query (should ask about playstyle)")
    print("="*70)

    rag = FalloutRAG()
    question = "What's a good rifle build?"
    print(f"Question: {question}\n")

    response = rag.ask(question)
    print(f"Response Type: {response['type']}")

    if response['type'] == 'clarification':
        print(f"\nReason: {response['reason']}")
        print("\nClarifying Questions:")
        for i, q in enumerate(response['questions'], 1):
            print(f"  {i}. {q}")
    else:
        print(f"\nUnexpected response: {response}")

    print("\n")


def test_weapon_damage_explanation():
    """Test that weapon damage values are explained properly"""
    print("="*70)
    print("TEST 4: Weapon Damage Explanation (should explain level tiers)")
    print("="*70)

    rag = FalloutRAG()
    question = "What is the damage of the Pipe revolver?"
    print(f"Question: {question}\n")

    response = rag.ask(question)
    print(f"Response Type: {response['type']}")

    if response['type'] == 'answer':
        print(f"\nAnswer:\n{response['content']}")
        # Check if explanation mentions levels
        if 'level' in response['content'].lower():
            print("\n✅ PASS: Answer includes level explanation")
        else:
            print("\n⚠️  WARNING: Answer may be missing level explanation")
    else:
        print(f"\nUnexpected response: {response}")

    print("\n")


def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in your .env file or export it")
        sys.exit(1)

    print("\n" + "="*70)
    print("TESTING ENHANCED RAG SYSTEM")
    print("="*70 + "\n")

    try:
        # Run tests
        test_specific_query()
        test_vague_query()
        test_build_query()
        test_weapon_damage_explanation()

        print("="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)

    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
