#!/usr/bin/env python3
"""
Inspect ChromaDB vector database contents.

Simple CLI tool to explore what's in your vector database.
"""

import os
import sys
import chromadb
from chromadb.config import Settings
from collections import Counter


def main():
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")

    if not os.path.exists(chroma_path):
        print(f"❌ ChromaDB not found at {chroma_path}")
        print("Run populate_vector_db.py first!")
        sys.exit(1)

    print("🔍 Inspecting ChromaDB Vector Database")
    print("=" * 60)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=chroma_path)

    try:
        collection = client.get_collection(name="fallout76")
    except:
        print("❌ Collection 'fallout76' not found!")
        print("Run populate_vector_db.py first!")
        sys.exit(1)

    # Get all items (metadata only, not embeddings)
    all_items = collection.get(include=['metadatas'])

    total = len(all_items['ids'])
    metadatas = all_items['metadatas']

    print(f"\n📊 Total Items: {total}")
    print("=" * 60)

    # Count by type
    types = Counter(m.get('type', 'unknown') for m in metadatas)

    print("\n🏷️  Items by Type:")
    for item_type, count in sorted(types.items()):
        print(f"   {item_type:20s}: {count:4d}")

    # Show some examples
    print("\n" + "=" * 60)
    print("📝 Sample Items (first 5 of each type):")
    print("=" * 60)

    shown = {}
    for i, metadata in enumerate(metadatas):
        item_type = metadata.get('type', 'unknown')

        if item_type not in shown:
            shown[item_type] = 0

        if shown[item_type] < 5:
            print(f"\n[{item_type.upper()}] {all_items['ids'][i]}")
            for key, value in sorted(metadata.items()):
                if key != 'type':
                    print(f"  {key}: {value}")
            shown[item_type] += 1

    print("\n" + "=" * 60)
    print("💡 Vector Search Example:")
    print("=" * 60)
    print("\nSearching for items similar to 'bloodied high damage build'...\n")

    # Do a sample semantic search
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key:
            openai_client = OpenAI(api_key=api_key)

            # Generate query embedding
            query = "bloodied high damage build"
            embedding_response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding

            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10
            )

            print(f"Top 10 results for '{query}':\n")
            for i, (doc_id, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                score = 1 / (1 + distance)  # Convert distance to similarity score
                print(f"{i}. [{metadata.get('type', '?').upper()}] {metadata.get('name', 'Unknown')}")
                print(f"   ID: {doc_id}")
                print(f"   Similarity: {score:.3f}")
                print()
        else:
            print("⚠️  OPENAI_API_KEY not set - skipping semantic search demo")
            print("Set it with: export OPENAI_API_KEY='your-key'")

    except ImportError:
        print("⚠️  OpenAI package not installed - skipping semantic search demo")
    except Exception as e:
        print(f"⚠️  Error during semantic search: {e}")

    print("\n" + "=" * 60)
    print("✅ Inspection Complete!")


if __name__ == "__main__":
    main()
