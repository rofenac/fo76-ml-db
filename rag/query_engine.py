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

    def ask(self, question: str) -> str:
        """Main RAG query function"""

        # Step 1: Use LLM to generate SQL query
        sql_prompt = f"""You are a SQL expert for a Fallout 76 game database using MySQL with ONLY_FULL_GROUP_BY mode enabled.

Database schema:
- v_weapons_with_perks: weapon_name, weapon_type (Ranged/Melee/etc), weapon_class (Shotgun/Rifle/etc), damage, regular_perks, legendary_perks
- v_armor_complete: name, armor_type ('regular' or 'power'), class, slot, set_name, damage_resistance, energy_resistance
- v_perks_all_ranks: perk_name, special, min_level, race, `rank`, rank_description
- v_legendary_perks_all_ranks: perk_name, race, `rank`, rank_description, effect_value, effect_type

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
            return f"Error executing query: {e}"

        # Check for empty results
        if not results:
            return f"No data found in the database for this query.\n\nSQL executed:\n{sql_query}\n\nThe query returned 0 rows. The data you're looking for may not exist in the database, or the query may need adjustment."

        # Step 3: Format results with LLM
        answer_prompt = f"""User asked: {question}

SQL query executed: {sql_query}

Database results: {results}

Format these results in a clear, helpful answer."""

        answer_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system="You are a database results formatter. You MUST ONLY use the data provided in the user's message. NEVER use external knowledge, training data, or make assumptions. If the data doesn't fully answer the question, explicitly state that. Your job is to present the database results clearly, not to add information from other sources.",
            messages=[{"role": "user", "content": answer_prompt}]
        )

        final_answer = answer_response.content[0].text

        # Store in conversation history
        self.conversation_history.append({
            'question': question,
            'sql': sql_query,
            'summary': final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
        })

        return final_answer

# Example usage
if __name__ == "__main__":
    rag = FalloutRAG()

    question = "What perks affect the Enclave plasma gun?"
    answer = rag.ask(question)
    print(answer)
