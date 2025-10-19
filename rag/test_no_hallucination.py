#!/usr/bin/env python3
"""Test to verify LLM does NOT use training data - only database results"""

import os
import sys
from query_engine import FalloutRAG
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_no_hallucination():
    """Test that the system does NOT mention perks/items not in database results"""
    print("="*70)
    print("TEST: Verify No Hallucination (Strict Database Grounding)")
    print("="*70)

    rag = FalloutRAG()

    # This is the same question from the user's example
    question = "How do i min/max my shotgun build?\n\nAdditional context: endgame build, PvE, max damage"
    print(f"Question: {question}\n")

    response = rag.ask(question, skip_classification=True)

    if response['type'] != 'answer':
        print(f"Unexpected response type: {response['type']}")
        return False

    answer = response['content']
    print(f"Answer:\n{answer}\n")
    print("="*70)

    # Check for violations - perks that don't exist in database
    violations = []
    forbidden_terms = [
        "Expert Shotgunner",
        "Master Shotgunner",
        "might exist",
        "could be available",
        "probably has",
        "likely includes",
        "should also have"
    ]

    for term in forbidden_terms:
        if term.lower() in answer.lower():
            violations.append(term)

    # Check for the specific violation pattern: "The database doesn't include X, Y, Z"
    # where X, Y, Z are from training data
    if "database" in answer.lower() and "doesn't include" in answer.lower():
        # Look for mentions of game elements after "doesn't include"
        if any(term.lower() in answer.lower() for term in ["expert", "master", "perk"]):
            violations.append("Mentions missing perks from training data")

    print("\n" + "="*70)
    if violations:
        print("❌ HALLUCINATION DETECTED - Found violations:")
        for v in violations:
            print(f"   - {v}")
        print("\nThe LLM is using training data instead of database results only!")
        return False
    else:
        print("✅ PASS - No hallucinations detected")
        print("   LLM only used database results and provided context")
        return True


def main():
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not found in environment")
        sys.exit(1)

    print("\n" + "="*70)
    print("HALLUCINATION PREVENTION TEST")
    print("="*70 + "\n")

    try:
        success = test_no_hallucination()

        if success:
            print("\n✅ TEST PASSED - System is properly grounded to database")
            sys.exit(0)
        else:
            print("\n❌ TEST FAILED - System is using training data")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
