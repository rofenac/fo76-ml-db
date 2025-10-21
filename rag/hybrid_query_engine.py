#!/usr/bin/env python3
"""
Hybrid Query Engine - Combines SQL and Vector Search

This engine intelligently routes queries:
- EXACT queries → Pure SQL (fast, precise)
- CONCEPTUAL queries → Vector search → SQL enrichment → Claude formats

Examples:
- "What's the damage of Gauss Shotgun?" → SQL
- "Best bloodied build" → Vector + SQL
- "Weapons similar to The Fixer" → Vector + SQL
"""

import os
import sys
from typing import Dict, List, Any, Optional
import mysql.connector
from openai import OpenAI
import chromadb
from anthropic import Anthropic

# Import existing SQL-based RAG
from query_engine import FalloutRAG


class HybridFalloutRAG:
    """
    Hybrid RAG system that combines SQL queries with vector semantic search.

    Uses vector search for conceptual queries, SQL for exact lookups.
    """

    def __init__(self, chroma_path: str = "./chroma_db"):
        """
        Initialize hybrid RAG system.

        Args:
            chroma_path: Path to ChromaDB storage
        """
        print("🚀 Initializing Hybrid RAG System...")

        # Initialize SQL-based RAG (existing system)
        print("   📊 Loading SQL RAG engine...")
        self.sql_rag = FalloutRAG()

        # Initialize OpenAI for embeddings
        print("   🔑 Connecting to OpenAI (for embeddings)...")
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not set!")
        self.openai_client = OpenAI(api_key=openai_key)
        self.embedding_model = "text-embedding-3-small"

        # Initialize Claude (for responses)
        print("   🤖 Connecting to Anthropic Claude...")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not set!")
        self.claude_client = Anthropic(api_key=anthropic_key)

        # Initialize ChromaDB
        print(f"   💾 Loading vector database from {chroma_path}...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        try:
            self.collection = self.chroma_client.get_collection(name="fallout76")
            print(f"      ✓ Loaded {self.collection.count()} embeddings")
        except:
            raise ValueError(
                "Vector database not found! Run populate_vector_db.py first."
            )

        # Conversation history (same as SQL RAG)
        self.conversation_history = []

        print("   ✓ Hybrid RAG System ready!\n")

    def classify_intent(self, question: str) -> str:
        """
        Classify user intent to determine which search method to use.

        Returns:
            "EXACT" - Use SQL only (specific item lookups)
            "CONCEPTUAL" - Use vector search (concepts, recommendations, similarity)
        """
        # Keywords that indicate exact queries
        exact_keywords = [
            "what is", "what does", "show me", "list all", "how many",
            "damage of", "stats of", "effect of", "ranks of"
        ]

        # Keywords that indicate conceptual queries
        conceptual_keywords = [
            "best", "similar to", "like", "recommend", "build for",
            "good for", "synergize", "complement", "work with",
            "bloodied", "stealth", "tank", "vats", "heavy gunner",
            "rifleman", "commando", "melee", "unarmed"
        ]

        question_lower = question.lower()

        # Check for exact patterns first
        for keyword in exact_keywords:
            if keyword in question_lower:
                return "EXACT"

        # Check for conceptual patterns
        for keyword in conceptual_keywords:
            if keyword in question_lower:
                return "CONCEPTUAL"

        # Default: if question mentions specific item names, use SQL
        # Otherwise use vector search
        if any(char.isupper() for char in question):  # Has proper nouns
            return "EXACT"

        return "CONCEPTUAL"

    def vector_search(self, query: str, n_results: int = 10) -> Dict[str, Any]:
        """
        Perform semantic search using vector embeddings.

        Args:
            query: User's natural language query
            n_results: Number of results to return

        Returns:
            Dictionary with search results including IDs, metadata, distances
        """
        # Generate query embedding
        embedding_response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=query
        )
        query_embedding = embedding_response.data[0].embedding

        # Search vector database
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['metadatas', 'distances', 'documents']
        )

        return results

    def enrich_with_sql(self, vector_results: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Take vector search results and fetch full data from MySQL.

        Args:
            vector_results: Results from vector_search()

        Returns:
            Dictionary organized by type (weapons, armor, perks, etc.)
        """
        enriched = {
            'weapons': [],
            'armor': [],
            'perks': [],
            'legendary_perks': [],
            'mutations': [],
            'consumables': []
        }

        metadatas = vector_results['metadatas'][0]

        # Group IDs by type
        items_by_type = {}
        for metadata in metadatas:
            item_type = metadata.get('type', 'unknown')
            item_id = metadata.get('id')

            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item_id)

        # Fetch full data from MySQL for each type
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'secret'),
            database=os.getenv('DB_NAME', 'f76')
        )
        cursor = db.cursor(dictionary=True)

        # Weapons
        if 'weapon' in items_by_type:
            ids = ','.join(items_by_type['weapon'])
            cursor.execute(f"SELECT * FROM v_weapons_with_perks WHERE id IN ({ids})")
            enriched['weapons'] = cursor.fetchall()

        # Armor
        if 'armor' in items_by_type:
            ids = ','.join(items_by_type['armor'])
            cursor.execute(f"SELECT * FROM v_armor_complete WHERE id IN ({ids})")
            enriched['armor'] = cursor.fetchall()

        # Regular perks (need to handle rank)
        if 'perk' in items_by_type:
            ids = ','.join(items_by_type['perk'])
            cursor.execute(f"SELECT * FROM v_perks_all_ranks WHERE perk_id IN ({ids})")
            enriched['perks'] = cursor.fetchall()

        # Legendary perks
        if 'legendary_perk' in items_by_type:
            ids = ','.join(items_by_type['legendary_perk'])
            cursor.execute(f"SELECT * FROM v_legendary_perks_all_ranks WHERE legendary_perk_id IN ({ids})")
            enriched['legendary_perks'] = cursor.fetchall()

        # Mutations
        if 'mutation' in items_by_type:
            ids = ','.join(items_by_type['mutation'])
            cursor.execute(f"SELECT * FROM v_mutations_complete WHERE mutation_id IN ({ids})")
            enriched['mutations'] = cursor.fetchall()

        # Consumables
        if 'consumable' in items_by_type:
            ids = ','.join(items_by_type['consumable'])
            cursor.execute(f"SELECT * FROM v_consumables_complete WHERE consumable_id IN ({ids})")
            enriched['consumables'] = cursor.fetchall()

        cursor.close()
        db.close()

        return enriched

    def format_vector_results(self, question: str, enriched_data: Dict[str, List[Dict]]) -> str:
        """
        Use Claude to format vector search results into a helpful answer.

        Args:
            question: Original user question
            enriched_data: Full data from MySQL for relevant items

        Returns:
            Natural language answer from Claude
        """
        # Build context from enriched data
        context_parts = []

        for item_type, items in enriched_data.items():
            if items:
                context_parts.append(f"\n=== {item_type.upper()} ===")
                for item in items[:5]:  # Limit to top 5 per type
                    context_parts.append(str(item))

        context = "\n".join(context_parts)

        # Inject conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for entry in self.conversation_history[-3:]:
                history_context += f"Q: {entry['question']}\nA: {entry['summary']}\n\n"

        # Prompt Claude
        prompt = f"""You are a Fallout 76 build advisor. A user asked a conceptual question and we found relevant items using semantic search.

User's question: {question}
{history_context}
Relevant items from our database:
{context}

Please provide a helpful, detailed answer using ONLY the data above. Do not use your training data about Fallout 76 - only use the database results provided.

If the data doesn't fully answer the question, say so clearly.

Format your answer as:
1. Direct answer to the question
2. Specific recommendations with item names and stats
3. Brief explanation of why these items are relevant

Be concise but informative."""

        message = self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = message.content[0].text

        # Store in history
        self.conversation_history.append({
            'question': question,
            'method': 'vector',
            'summary': answer[:200] + "..." if len(answer) > 200 else answer
        })

        return answer

    def ask(self, question: str) -> tuple[str, str]:
        """
        Answer a question using hybrid approach.

        Args:
            question: User's question

        Returns:
            Tuple of (answer, method_used)
            method_used is either "SQL" or "VECTOR+SQL"
        """
        # Classify intent
        intent = self.classify_intent(question)

        if intent == "EXACT":
            # Use existing SQL RAG
            print("   🔍 Using SQL search (exact query)")
            answer = self.sql_rag.ask(question)
            return answer, "SQL"

        else:  # CONCEPTUAL
            # Use vector search + SQL enrichment
            print("   🧠 Using vector search (conceptual query)")

            # 1. Vector search
            vector_results = self.vector_search(question, n_results=15)

            # 2. Enrich with SQL
            enriched_data = self.enrich_with_sql(vector_results)

            # 3. Format with Claude
            answer = self.format_vector_results(question, enriched_data)

            return answer, "VECTOR+SQL"


def main():
    """Test the hybrid engine"""
    import sys

    chroma_path = os.path.join(os.path.dirname(__file__), "chroma_db")

    try:
        engine = HybridFalloutRAG(chroma_path)

        # Test queries
        test_queries = [
            "What's the damage of the Gauss Shotgun?",  # EXACT → SQL
            "Recommend a bloodied heavy gunner build",  # CONCEPTUAL → Vector
            "Best mutations for a stealth rifle build",  # CONCEPTUAL → Vector
        ]

        for query in test_queries:
            print("\n" + "=" * 60)
            print(f"Q: {query}")
            print("=" * 60)

            answer, method = engine.ask(query)

            print(f"\n[Method: {method}]")
            print(f"\nA: {answer}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
