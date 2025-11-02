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
from openai import OpenAI
import chromadb
from anthropic import Anthropic

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import database utility and SQL-based RAG
from database.db_utils import get_db
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

        # Initialize database utility
        self.db = get_db()

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

    def cleanup(self):
        """
        Cleanup resources to prevent hanging on exit.
        Closes database connections and ChromaDB client.
        """
        try:
            # ChromaDB client cleanup
            if hasattr(self, 'chroma_client'):
                # ChromaDB's persistent client doesn't need explicit cleanup,
                # but we can remove the reference to help garbage collection
                self.chroma_client = None
                self.collection = None
        except Exception as e:
            print(f"⚠️  Warning during cleanup: {e}")

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context"""
        self.cleanup()
        return False

    def detect_category_filter(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Detect if the query is asking about a specific item category.

        Returns:
            Dict with 'type' and 'filter' info, or None if no category detected
        """
        question_lower = question.lower()

        # Weapon class filters
        # Use LIKE pattern to catch variations (e.g., "Shotgun", "Automatic heavy shotgun")
        weapon_classes = {
            'shotgun': {'type': 'weapon', 'class_pattern': '%shotgun%'},
            'rifle': {'type': 'weapon', 'class_pattern': '%rifle%'},
            'pistol': {'type': 'weapon', 'class_pattern': '%pistol%'},
            'heavy gun': {'type': 'weapon', 'class_pattern': '%heavy gun%'},
            'melee': {'type': 'weapon', 'class_pattern': '%melee%'},
        }

        for keyword, filter_info in weapon_classes.items():
            if keyword in question_lower:
                return filter_info

        return None

    def classify_intent(self, question: str) -> str:
        """
        Classify user intent to determine which search method to use.

        Returns:
            "EXACT" - Use SQL only (specific item lookups)
            "CONCEPTUAL" - Use vector search (concepts, recommendations, similarity)
        """
        question_lower = question.lower()

        # Keywords that indicate conceptual queries (CHECK THESE FIRST!)
        # These take priority because they indicate complex/comparative questions
        conceptual_keywords = [
            "best", "worst", "top", "similar to", "like", "recommend",
            "build for", "good for", "synergize", "complement", "work with",
            "compare", "versus", "vs", "better than",
            "bloodied", "stealth", "tank", "vats", "heavy gunner",
            "rifleman", "commando", "melee", "unarmed", "shotgunner",
            "mutations for", "perks for", "weapons for", "armor for"
        ]

        # Keywords that indicate exact queries
        # More specific now - looking for pure lookup queries
        exact_keywords = [
            "show me all", "list all", "how many",
            "damage of", "stats of", "effect of", "ranks of",
            "what are the stats", "what are the effects", "what are the ranks"
        ]

        # PRIORITY 1: Check for conceptual patterns FIRST
        # This fixes "What is the best..." going to SQL mode
        for keyword in conceptual_keywords:
            if keyword in question_lower:
                return "CONCEPTUAL"

        # PRIORITY 2: Check for exact patterns
        for keyword in exact_keywords:
            if keyword in question_lower:
                return "EXACT"

        # PRIORITY 3: If asking about a specific named item, use SQL
        # "What is Gauss Shotgun?" or "What does The Fixer do?"
        if ("what is" in question_lower or "what does" in question_lower):
            # Check if there's a proper noun (likely an item name)
            if any(char.isupper() for char in question):
                return "EXACT"
            # Otherwise it might be conceptual: "what is good for stealth?"
            else:
                return "CONCEPTUAL"

        # PRIORITY 4: Default to vector search for open-ended questions
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

    def hybrid_category_search(self, question: str, category_filter: Dict[str, Any], n_results: int = 30) -> Dict[str, List[Dict]]:
        """
        Hybrid search: SQL pre-filter by category + vector ranking.
        Ensures ALL items in a category are considered, then ranked by relevance.

        Args:
            question: User's question
            category_filter: Dict with 'type' and filter criteria
            n_results: Max results to return

        Returns:
            Dictionary organized by type with ranked results
        """
        enriched = {
            'weapons': [],
            'armor': [],
            'perks': [],
            'legendary_perks': [],
            'mutations': [],
            'consumables': []
        }

        # SQL pre-filter to get ALL items in the category (with mechanics)
        if category_filter['type'] == 'weapon':
            class_pattern = category_filter['class_pattern']
            all_weapons = self.db.execute_query(f"""
                SELECT
                    wpv.*,
                    GROUP_CONCAT(
                        CONCAT(
                            wmt.name,
                            CASE
                                WHEN wm.numeric_value IS NOT NULL
                                THEN CONCAT(' (', wm.numeric_value, COALESCE(CONCAT(' ', wm.unit), ''), ')')
                                ELSE ''
                            END,
                            ': ',
                            COALESCE(wm.notes, wmt.description)
                        )
                        SEPARATOR '; '
                    ) AS mechanics
                FROM v_weapons_with_perks wpv
                LEFT JOIN weapon_mechanics wm ON wpv.id = wm.weapon_id
                LEFT JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
                WHERE wpv.weapon_class LIKE '{class_pattern}'
                GROUP BY wpv.id, wpv.weapon_name, wpv.weapon_type, wpv.weapon_class,
                         wpv.level, wpv.damage, wpv.regular_perks, wpv.legendary_perks, wpv.source_url
            """)

            # Get display name from pattern (strip wildcards)
            display_name = class_pattern.replace('%', '').title()
            print(f"      📊 SQL pre-filter found {len(all_weapons)} weapons matching '{class_pattern}'")

            # Now rank these weapons by vector similarity
            weapon_ids = [str(w['id']) for w in all_weapons]
            if weapon_ids:
                # Get embeddings and rank
                query_embedding_response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=question
                )
                query_embedding = query_embedding_response.data[0].embedding

                # Query ALL weapon embeddings (we'll filter afterwards)
                # ChromaDB filter syntax is tricky, so we filter post-query
                vector_results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=1000,  # Get many results to ensure we capture all weapons
                    where={"type": "weapon"},  # Filter to weapons only
                    include=['metadatas', 'distances']
                )

                # Filter to only our shotguns and get rank order
                weapon_id_set = set(weapon_ids)
                ranked_ids = [m['id'] for m in vector_results['metadatas'][0]
                             if m['id'] in weapon_id_set][:n_results]

                # Order weapons by vector rank
                id_to_weapon = {str(w['id']): w for w in all_weapons}
                enriched['weapons'] = [id_to_weapon[wid] for wid in ranked_ids if wid in id_to_weapon]

                # Log top ranked weapons
                top_5 = [w['weapon_name'] for w in enriched['weapons'][:5]]
                print(f"         • Top 5 by vector rank: {', '.join(top_5)}")

                # Add any weapons that weren't in top N vector results
                remaining = [w for w in all_weapons if str(w['id']) not in ranked_ids]
                if remaining:
                    print(f"         • Additional {len(remaining)} weapons below top {n_results}")
                enriched['weapons'].extend(remaining)

        return enriched

    def extract_named_items(self, question: str) -> Dict[str, List[str]]:
        """
        Extract potential item names from the user's question.
        Looks for capitalized phrases that might be item names.

        Args:
            question: User's question

        Returns:
            Dict with lists of potential item names by type
        """
        import re

        item_names = []

        # Strategy 1: Extract multi-word capitalized phrases (3+ words first for specificity)
        # e.g., "Lock and Load", "Bringing the Big Guns"
        pattern_long = r'\b([A-Z][a-z]+(?:\s+(?:and|the|of)\s+[A-Z][a-z]+)+)\b'
        long_phrases = re.findall(pattern_long, question)
        item_names.extend(long_phrases)

        # Remove long phrases from question to avoid substring matches
        question_without_long = question
        for phrase in long_phrases:
            question_without_long = question_without_long.replace(phrase, '')

        # Strategy 2: Extract 2-word capitalized phrases
        pattern_short = r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        short_phrases = re.findall(pattern_short, question_without_long)
        item_names.extend(short_phrases)

        # Strategy 3: Look for quoted strings (exact item names)
        quoted_pattern = r'["\']([^"\']+)["\']'
        quoted_names = re.findall(quoted_pattern, question)
        item_names.extend(quoted_names)

        # Filter out common words/phrases that aren't items
        stop_phrases = {'What', 'The', 'How', 'Why', 'When', 'Where', 'Which', 'Who',
                       'Best', 'Good', 'Better', 'Weapons', 'Perks', 'Armor', 'About',
                       'Other', 'Most', 'That', 'This', 'These', 'Those', 'Such'}

        filtered_names = [name for name in item_names
                         if name not in stop_phrases and len(name) > 2]

        return {'potential_names': filtered_names}

    def fetch_named_items_from_sql(self, item_names: List[str]) -> Dict[str, List[Dict]]:
        """
        Fetch items directly from SQL by name.

        Args:
            item_names: List of potential item names to search for

        Returns:
            Dictionary organized by type with matching items
        """
        if not item_names:
            return {
                'weapons': [],
                'armor': [],
                'perks': [],
                'legendary_perks': [],
                'mutations': [],
                'consumables': []
            }

        enriched = {
            'weapons': [],
            'armor': [],
            'perks': [],
            'legendary_perks': [],
            'mutations': [],
            'consumables': []
        }

        # Build LIKE clauses for each name
        name_conditions = " OR ".join([f"weapon_name LIKE '%{name}%'" for name in item_names])

        # Search weapons
        enriched['weapons'] = self.db.execute_query(f"SELECT * FROM v_weapons_with_perks WHERE {name_conditions}")

        # Search armor
        enriched['armor'] = self.db.execute_query(f"SELECT * FROM v_armor_complete WHERE {name_conditions.replace('weapon_name', 'name')}")

        # Search perks
        enriched['perks'] = self.db.execute_query(f"SELECT * FROM v_perks_all_ranks WHERE {name_conditions.replace('weapon_name', 'perk_name')}")

        # Search legendary perks
        enriched['legendary_perks'] = self.db.execute_query(f"SELECT * FROM v_legendary_perks_all_ranks WHERE {name_conditions.replace('weapon_name', 'perk_name')}")

        # Search mutations
        enriched['mutations'] = self.db.execute_query(f"SELECT * FROM v_mutations_complete WHERE {name_conditions.replace('weapon_name', 'mutation_name')}")

        # Search consumables
        enriched['consumables'] = self.db.execute_query(f"SELECT * FROM v_consumables_complete WHERE {name_conditions.replace('weapon_name', 'consumable_name')}")

        return enriched

    def enrich_with_sql(self, vector_results: Dict[str, Any], named_items: Optional[Dict[str, List[Dict]]] = None) -> Dict[str, List[Dict]]:
        """
        Take vector search results and fetch full data from MySQL.

        Args:
            vector_results: Results from vector_search()
            named_items: Optional dict of items fetched by name to merge in

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
        distances = vector_results.get('distances', [[]])[0]

        # Log what was found by vector search
        print(f"      📊 Vector search returned {len(metadatas)} items")

        # Group IDs by type
        items_by_type = {}
        for idx, metadata in enumerate(metadatas):
            item_type = metadata.get('type', 'unknown')
            item_id = metadata.get('id')

            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item_id)

        # Fetch full data from MySQL for each type using new DB utility

        # Weapons (with mechanics)
        if 'weapon' in items_by_type:
            ids = ','.join(items_by_type['weapon'])
            enriched['weapons'] = self.db.execute_query(f"""
                SELECT
                    wpv.*,
                    GROUP_CONCAT(
                        CONCAT(
                            wmt.name,
                            CASE
                                WHEN wm.numeric_value IS NOT NULL
                                THEN CONCAT(' (', wm.numeric_value, COALESCE(CONCAT(' ', wm.unit), ''), ')')
                                ELSE ''
                            END,
                            ': ',
                            COALESCE(wm.notes, wmt.description)
                        )
                        SEPARATOR '; '
                    ) AS mechanics
                FROM v_weapons_with_perks wpv
                LEFT JOIN weapon_mechanics wm ON wpv.id = wm.weapon_id
                LEFT JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
                WHERE wpv.id IN ({ids})
                GROUP BY wpv.id, wpv.weapon_name, wpv.weapon_type, wpv.weapon_class,
                         wpv.level, wpv.damage, wpv.regular_perks, wpv.legendary_perks, wpv.source_url
            """)
            print(f"         • Weapons: {', '.join([w['weapon_name'] for w in enriched['weapons']])}")

        # Armor
        if 'armor' in items_by_type:
            ids = ','.join(items_by_type['armor'])
            enriched['armor'] = self.db.execute_query(f"SELECT * FROM v_armor_complete WHERE id IN ({ids})")

        # Regular perks (need to handle rank)
        if 'perk' in items_by_type:
            ids = ','.join(items_by_type['perk'])
            enriched['perks'] = self.db.execute_query(f"SELECT * FROM v_perks_all_ranks WHERE perk_id IN ({ids})")

        # Legendary perks
        if 'legendary_perk' in items_by_type:
            ids = ','.join(items_by_type['legendary_perk'])
            enriched['legendary_perks'] = self.db.execute_query(f"SELECT * FROM v_legendary_perks_all_ranks WHERE legendary_perk_id IN ({ids})")

        # Mutations
        if 'mutation' in items_by_type:
            ids = ','.join(items_by_type['mutation'])
            enriched['mutations'] = self.db.execute_query(f"SELECT * FROM v_mutations_complete WHERE mutation_id IN ({ids})")

        # Consumables
        if 'consumable' in items_by_type:
            ids = ','.join(items_by_type['consumable'])
            enriched['consumables'] = self.db.execute_query(f"SELECT * FROM v_consumables_complete WHERE consumable_id IN ({ids})")

        # Merge in named items if provided (prevents duplicates using dict keying)
        if named_items:
            for item_type in enriched.keys():
                if named_items[item_type]:
                    # Create a set of IDs already in enriched results
                    existing_ids = set()
                    id_field_map = {
                        'weapons': 'id',
                        'armor': 'id',
                        'perks': 'perk_id',
                        'legendary_perks': 'legendary_perk_id',
                        'mutations': 'mutation_id',
                        'consumables': 'consumable_id'
                    }
                    id_field = id_field_map.get(item_type)

                    if id_field:
                        existing_ids = {item.get(id_field) for item in enriched[item_type]}

                        # Add named items that aren't already present
                        for named_item in named_items[item_type]:
                            item_id = named_item.get(id_field)
                            if item_id not in existing_ids:
                                enriched[item_type].append(named_item)
                                name_key = 'name' if item_type == 'armor' else f"{item_type.rstrip('s')}_name"
                                item_name = named_item.get(name_key, 'unknown')
                                print(f"         ➕ Added named item: {item_name}")

        return enriched

    def format_vector_results(self, question: str, enriched_data: Dict[str, List[Dict]], is_category_search: bool = False) -> str:
        """
        Use Claude to format vector search results into a helpful answer.

        Args:
            question: Original user question
            enriched_data: Full data from MySQL for relevant items
            is_category_search: If True, include ALL items (no limit)

        Returns:
            Natural language answer from Claude
        """
        # Build context from enriched data
        context_parts = []

        for item_type, items in enriched_data.items():
            if items:
                context_parts.append(f"\n=== {item_type.upper()} ===")
                # For category searches, include ALL items to ensure completeness
                # For named items, also include all to honor user's explicit request
                limit = len(items) if (is_category_search or len(items) <= 15) else 10

                # Log what's being included
                if item_type in ['perks', 'legendary_perks']:
                    perk_names = [p.get('perk_name', 'unknown') for p in items[:limit]]
                    unique_names = list(set(perk_names))[:8]
                    print(f"         📋 Including {len(items[:limit])} {item_type}: {', '.join(unique_names)}")

                for item in items[:limit]:
                    context_parts.append(str(item))

        context = "\n".join(context_parts)

        # Inject conversation history
        history_context = ""
        if self.conversation_history:
            history_context = "\n\nPrevious conversation:\n"
            for entry in self.conversation_history[-3:]:
                history_context += f"Q: {entry['question']}\nA: {entry['summary']}\n\n"

        # Prompt Claude with strict anti-hallucination instructions
        prompt = f"""You are a Fallout 76 build advisor. A user asked a conceptual question and we found relevant items using semantic search.

User's question: {question}
{history_context}
Relevant items from our database:
{context}

⚠️ CRITICAL RULES - ABSOLUTE COMPLIANCE REQUIRED:
1. You MUST ONLY use data from the database results shown above
2. You are STRICTLY FORBIDDEN from using your training data about Fallout 76
3. NEVER mention items, perks, weapons, or game elements NOT in the database results above
4. NEVER say "you could also try..." unless those items are in the results
5. NEVER use phrases like "typically", "usually", "in my experience" - you have NO experience
6. If the database results don't fully answer the question, explicitly state: "The available data doesn't include information about [missing aspect]"
7. Do NOT fabricate item stats, perk effects, or synergies - only report what's in the data
8. Do NOT add "general Fallout 76 advice" from your training knowledge

If you violate these rules, the system will fail and the user will be misled. Stay strictly within the provided data.

Format your answer as:
1. Direct answer to the question using ONLY items from the database results above
2. Specific recommendations with exact item names and stats from the results
3. Brief explanation of why these items are relevant based on their database properties

Be helpful and informative, but ONLY within the bounds of the provided data."""

        message = self.claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.3,  # Low temperature for more deterministic responses
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
            method_used is either "SQL", "VECTOR+SQL", or "HYBRID"
        """
        # Classify intent
        intent = self.classify_intent(question)

        if intent == "EXACT":
            # Use existing SQL RAG
            print("   🔍 Using SQL search (exact query)")
            answer = self.sql_rag.ask(question)
            return answer, "SQL"

        else:  # CONCEPTUAL
            # Check if this is a category-specific query
            category_filter = self.detect_category_filter(question)

            if category_filter:
                # Use hybrid SQL pre-filter + vector ranking
                display_category = category_filter['class_pattern'].replace('%', '').title()
                print(f"   🎯 Using hybrid search (category: weapons matching '{category_filter['class_pattern']}')")

                # 1. Hybrid category search (SQL filter + vector rank)
                enriched_data = self.hybrid_category_search(question, category_filter, n_results=30)

                # 2. Format with Claude (include ALL items for category searches)
                answer = self.format_vector_results(question, enriched_data, is_category_search=True)

                return answer, "HYBRID"

            else:
                # Use standard vector search + SQL enrichment
                print("   🧠 Using vector search (conceptual query)")

                # 1. Extract any specifically named items from the question
                named_info = self.extract_named_items(question)
                potential_names = named_info['potential_names']

                named_items_dict = None
                if potential_names:
                    print(f"      🔍 Detected named items in query: {', '.join(potential_names)}")
                    named_items_dict = self.fetch_named_items_from_sql(potential_names)

                    # Log what was found
                    total_found = sum(len(items) for items in named_items_dict.values())
                    if total_found > 0:
                        print(f"      ✓ Found {total_found} matching items by name")

                # 2. Vector search
                vector_results = self.vector_search(question, n_results=30)

                # 3. Enrich with SQL + merge named items
                enriched_data = self.enrich_with_sql(vector_results, named_items=named_items_dict)

                # 4. Format with Claude (limit to top results)
                answer = self.format_vector_results(question, enriched_data, is_category_search=False)

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
