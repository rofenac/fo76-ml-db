#!/usr/bin/env python3
"""
Show actual embedding vectors from ChromaDB.

Warning: Embeddings are 1536 numbers each - output will be large!
"""

import os
import sys
import chromadb
import numpy as np


def main():
    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")

    if not os.path.exists(chroma_path):
        print(f"❌ ChromaDB not found at {chroma_path}")
        sys.exit(1)

    # Connect
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection(name="fallout76")

    # Get a specific item (or first few items)
    if len(sys.argv) > 1:
        # Get specific item by ID
        item_id = sys.argv[1]
        print(f"🔍 Looking up item: {item_id}")
        print("=" * 80)

        try:
            result = collection.get(
                ids=[item_id],
                include=['embeddings', 'metadatas', 'documents']
            )

            if not result['ids']:
                print(f"❌ Item '{item_id}' not found!")
                print("\nTry one of these IDs:")
                samples = collection.get(limit=5, include=['metadatas'])
                for sid, meta in zip(samples['ids'], samples['metadatas']):
                    print(f"  - {sid} ({meta.get('type')})")
                sys.exit(1)

            show_item_details(result, 0)

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    else:
        # Show first 3 items as examples
        print("📊 Showing first 3 items (run with item ID to see specific item)")
        print("=" * 80)
        print("Usage: python show_embeddings.py <item_id>")
        print("=" * 80)

        result = collection.get(
            limit=3,
            include=['embeddings', 'metadatas', 'documents']
        )

        for i in range(len(result['ids'])):
            show_item_details(result, i)
            print("\n" + "=" * 80 + "\n")


def show_item_details(result, index):
    """Display detailed info about an item including its embedding"""
    item_id = result['ids'][index]
    metadata = result['metadatas'][index]
    document = result['documents'][index]
    embedding = result['embeddings'][index]

    print(f"\n🆔 Item ID: {item_id}")
    print(f"📝 Type: {metadata.get('type', 'unknown')}")
    print(f"🏷️  Name: {metadata.get('name', 'unknown')}")

    print(f"\n📄 Document Text:")
    print(f"   {document}")

    print(f"\n🔢 Embedding Vector (1536 dimensions):")
    print(f"   First 10 values: {embedding[:10]}")
    print(f"   Last 10 values:  {embedding[-10:]}")

    # Stats about the embedding
    embedding_array = np.array(embedding)
    print(f"\n📈 Embedding Statistics:")
    print(f"   Dimensions: {len(embedding)}")
    print(f"   Min value:  {embedding_array.min():.6f}")
    print(f"   Max value:  {embedding_array.max():.6f}")
    print(f"   Mean:       {embedding_array.mean():.6f}")
    print(f"   Std Dev:    {embedding_array.std():.6f}")
    print(f"   Magnitude:  {np.linalg.norm(embedding_array):.6f}")

    # Show full embedding if requested
    print(f"\n💾 Full embedding vector:")
    print(f"   [")
    for i in range(0, len(embedding), 8):
        chunk = embedding[i:i+8]
        formatted = ", ".join(f"{v:9.6f}" for v in chunk)
        print(f"      {formatted},")
    print(f"   ]")


if __name__ == "__main__":
    main()
