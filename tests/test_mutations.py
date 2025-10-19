#!/usr/bin/env python3
"""Test mutation queries in RAG system"""

import sys
sys.path.insert(0, 'rag')

from query_engine import FalloutRAG

def test_mutation_queries():
    """Test various mutation-related queries"""
    rag = FalloutRAG()

    queries = [
        "List all mutations",
        "What does Marsupial do?",
        "Which mutations are mutually exclusive?",
        "What mutations help with carry weight?",
        "Show me all mutations with their positive and negative effects"
    ]

    print("="*70)
    print("TESTING MUTATION QUERIES")
    print("="*70)

    for i, query in enumerate(queries, 1):
        print(f"\n[TEST {i}] {query}")
        print("-"*70)

        response = rag.ask(query, skip_classification=True)

        if response['type'] == 'answer':
            print(response['content'])
        else:
            print(f"Unexpected response type: {response['type']}")
            print(response)

        print()

    print("="*70)
    print("ALL MUTATION TESTS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_mutation_queries()
