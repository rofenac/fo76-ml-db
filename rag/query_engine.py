import anthropic
import mysql.connector
import os
from dotenv import load_dotenv
import re
from typing import Dict, List

# Load environment variables
load_dotenv()

class FalloutRAG:
    def __init__(self):
        # Initialize Claude
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

        # Database connection
        self.db_config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD'),
            'database': os.environ.get('DB_NAME', 'f76')
        }

        # Conversation history for context
        self.conversation_history = []

        # Game mechanics knowledge base
        self.game_mechanics = """
FALLOUT 76 GAME MECHANICS CONTEXT:

1. Weapon Damage Levels:
   - Multiple damage values (e.g., "51 / 57 / 65 / 83") represent different weapon LEVELS
   - Higher level weapons have higher damage output
   - Each value corresponds to a specific level tier

2. Character Races:
   - Human: Standard character
   - Ghoul: Added in recent updates, has radiation-based mechanics
   - Some perks are race-specific (e.g., "Action Diet" and "Feral Rage" are Ghoul-only)

3. Build Archetypes:
   - Bloodied: Low health, high damage
   - Stealth/Sneak: Hidden damage multipliers
   - Heavy Gunner: Tank with heavy weapons
   - Commando: Automatic rifle specialist
   - VATS: Critical hit focused
   - Melee: Close combat specialist

4. Armor Types:
   - Regular Armor: Light/Sturdy/Heavy variants with different DR/ER values
   - Power Armor: Requires fusion cores, provides highest protection
   - DR = Damage Resistance, ER = Energy Resistance, RR = Radiation Resistance

5. Perk System:
   - Regular Perks: 1-5 ranks, equipped in SPECIAL categories
   - Legendary Perks: 1-4 ranks, more powerful endgame perks
   - Perks can have conditional effects (scoped, ADS, VATS, etc.)

6. Mutations:
   - 19 total mutations available, acquired through radiation exposure
   - Each mutation has positive and negative effects
   - Players can have up to 18 mutations simultaneously
   - Carnivore and Herbivore are mutually exclusive (can only have one)
   - Class Freak perk reduces negative effects by 25%/50%/75% at ranks 1/2/3
   - Strange in Numbers perk increases positive effects by 25% when in a team with other mutated players
   - Starched Genes perk prevents gaining/losing mutations
   - Common mutations: Marsupial (+carry weight, +jump/-INT), Speed Demon (+speed/+reload/-hunger increase)
"""

    def escape_reserved_keywords(self, sql: str) -> str:
        """Escape MySQL reserved keywords with backticks"""
        # Pattern to match column names (not in strings, not already escaped)
        for keyword in self.reserved_keywords:
            # Match keyword as column name (word boundary, not in backticks or quotes)
            pattern = r'\b' + keyword + r'\b(?![`\'])'
            # Replace with backticked version
            sql = re.sub(pattern, f'`{keyword}`', sql, flags=re.IGNORECASE)
        return sql

    def query_database(self, sql: str) -> List[Dict]:
        """Execute SQL query and return results"""
        conn = mysql.connector.connect(**self.db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def classify_intent(self, question: str) -> Dict:
        """Classify user intent and detect if clarification is needed"""
        classification_prompt = f"""Analyze this Fallout 76 database question and determine if it needs clarification.

Question: "{question}"

Classify as:
1. SPECIFIC - Question is clear and can be answered directly (e.g., "What perks affect the Gauss shotgun?")
2. VAGUE_CRITERIA - Uses subjective terms without criteria (e.g., "What's the best weapon?", "Show me good armor")
3. VAGUE_BUILD - Asks about builds without specifying playstyle (e.g., "What's a good rifle build?")
4. AMBIGUOUS - Unclear what the user is asking for

For VAGUE questions, suggest 2-3 clarifying questions to ask the user.

Respond in this exact format:
CLASSIFICATION: [SPECIFIC/VAGUE_CRITERIA/VAGUE_BUILD/AMBIGUOUS]
REASON: [Brief explanation]
CLARIFYING_QUESTIONS: [List questions separated by ||| or NONE if specific]"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": classification_prompt}]
        )

        result_text = response.content[0].text.strip()

        # Parse the response
        classification = "SPECIFIC"
        reason = ""
        questions = []

        for line in result_text.split('\n'):
            if line.startswith('CLASSIFICATION:'):
                classification = line.split(':', 1)[1].strip()
            elif line.startswith('REASON:'):
                reason = line.split(':', 1)[1].strip()
            elif line.startswith('CLARIFYING_QUESTIONS:'):
                q_text = line.split(':', 1)[1].strip()
                if q_text != "NONE":
                    questions = [q.strip() for q in q_text.split('|||')]

        return {
            'classification': classification,
            'reason': reason,
            'clarifying_questions': questions
        }

    def ask(self, question: str, skip_classification: bool = False) -> Dict:
        """Main RAG query function

        Args:
            question: User's question
            skip_classification: Skip intent classification (used after clarification)

        Returns:
            Dict with 'type' (answer/clarification) and 'content'
        """

        # Step 1: Classify intent (unless skipped)
        if not skip_classification:
            intent = self.classify_intent(question)

            # If question needs clarification, return clarifying questions
            if intent['classification'] in ['VAGUE_CRITERIA', 'VAGUE_BUILD', 'AMBIGUOUS']:
                return {
                    'type': 'clarification',
                    'classification': intent['classification'],
                    'reason': intent['reason'],
                    'questions': intent['clarifying_questions']
                }

        # Step 2: Use LLM to generate SQL query
        sql_prompt = f"""You are a SQL expert for a Fallout 76 game database using MySQL with ONLY_FULL_GROUP_BY mode enabled.

Database schema:
- v_weapons_with_perks: weapon_name, weapon_type (Ranged/Melee/etc), weapon_class (Shotgun/Rifle/etc), damage, regular_perks, legendary_perks
- v_armor_complete: name, armor_type ('regular' or 'power'), class, slot, set_name, damage_resistance, energy_resistance
- v_perks_all_ranks: perk_name, special, min_level, race, `rank`, rank_description
- v_legendary_perks_all_ranks: perk_name, race, `rank`, rank_description, effect_value, effect_type
- v_mutations_complete: mutation_name, positive_effects, negative_effects, form_id, exclusive_with, suppression_perk, enhancement_perk

User question: {question}

Generate ONLY a valid MySQL query to answer this question. No explanations or markdown.

Requirements:
- Use backticks around reserved keyword columns (like `rank`, `order`, `key`, `index`, `group`)
- If using aggregate functions (GROUP_CONCAT, COUNT, SUM, etc.), you MUST include a GROUP BY clause with all non-aggregated columns
- Ensure the query is compatible with MySQL ONLY_FULL_GROUP_BY mode
- Keep queries simple and efficient
- NOTE: weapon_type is general (Ranged/Melee), weapon_class is specific (Shotgun/Rifle/Pistol/etc)"""

        # Build conversation context if history exists
        context_section = ""
        if self.conversation_history:
            context_section = "\n\nPrevious conversation context:\n"
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                context_section += f"Q: {entry['question']}\nA: {entry['summary']}\n\n"
            sql_prompt = context_section + sql_prompt

        # Get SQL from Claude
        sql_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": sql_prompt}]
        )

        sql_query = sql_response.content[0].text.strip()

        # Remove markdown code fences if present
        sql_query = re.sub(r'^```(?:sql)?\s*\n?', '', sql_query)
        sql_query = re.sub(r'\n?```\s*$', '', sql_query)
        sql_query = sql_query.strip()

        print(f"Generated SQL: ```sql\n{sql_query}\n```\n")

        # Step 2: Execute the query
        try:
            results = self.query_database(sql_query)
        except Exception as e:
            return {
                'type': 'error',
                'content': f"Error executing query: {e}\n\nSQL attempted:\n{sql_query}"
            }

        # Check for empty results
        if not results:
            return {
                'type': 'answer',
                'content': f"No data found in the database for this query.\n\nSQL executed:\n{sql_query}\n\nThe query returned 0 rows. The data you're looking for may not exist in the database, or the query may need adjustment."
            }

        # Step 3: Format results with LLM
        answer_prompt = f"""User asked: {question}

SQL query executed: {sql_query}

Database results: {results}

{self.game_mechanics}

Format these results in a clear, helpful answer.

IMPORTANT INSTRUCTIONS:
- When showing weapon damage with multiple values (e.g., "51 / 57 / 65"), explain that these represent different weapon LEVEL tiers
- If discussing builds, mention the relevant build archetype (bloodied, stealth, etc.)
- Explain armor type differences (regular vs power armor) when relevant
- Clarify race-specific perks if applicable
- Use the game mechanics context above to provide helpful explanations"""

        answer_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system="""You are a database results formatter. You have ZERO knowledge of Fallout 76 beyond what is in the database results and game mechanics context provided to you.

ABSOLUTE RULES - NO EXCEPTIONS:
1. You MUST ONLY use data from the database results provided in the user message
2. You MUST ONLY use the game mechanics context explicitly provided to you
3. You are FORBIDDEN from using ANY training data, external knowledge, or assumptions about Fallout 76
4. NEVER mention game elements (perks, weapons, items) that are not in the database results
5. NEVER speculate about what "might exist" or what "could be available"
6. If information is not in the database results, say "This information is not available in the database"
7. Do NOT suggest perks, weapons, or items that weren't returned in the query results

VIOLATION EXAMPLES (DO NOT DO THIS):
❌ "Other perks like Expert Shotgunner might help" - NO! If not in results, don't mention it
❌ "You should also consider..." and then list items not in the results - FORBIDDEN
❌ "The database doesn't include X, Y, Z" where X, Y, Z are from your training - FORBIDDEN

CORRECT APPROACH:
✅ Only describe what IS in the database results
✅ If asked about something not in results: "The database does not contain information about that"
✅ Use only the game mechanics context provided to explain results

Your ONLY job is to format and explain the database results clearly. Nothing more.""",
            messages=[{"role": "user", "content": answer_prompt}]
        )

        final_answer = answer_response.content[0].text

        # Store in conversation history
        self.conversation_history.append({
            'question': question,
            'sql': sql_query,
            'summary': final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
        })

        return {
            'type': 'answer',
            'content': final_answer
        }

# Example usage
if __name__ == "__main__":
    rag = FalloutRAG()

    question = "What perks affect the Enclave plasma gun?"
    answer = rag.ask(question)
    print(answer)
