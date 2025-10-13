# RAG/LLM Implementation Guide

## What is RAG (Retrieval Augmented Generation)?

RAG combines:
1. **Retrieval** - Finding relevant information from your database
2. **Generation** - Using an LLM to create human-like responses based on that information

Instead of the LLM relying solely on its training data, RAG lets it access your specific Fallout 76 database to give accurate, up-to-date answers.

## Implementation Status

✅ **MVP Complete** - Basic SQL + LLM RAG system is operational with the following features:
- Natural language to SQL query generation
- Database query execution with error handling
- Conversational context memory (last 3 exchanges)
- Strict grounding to database results (prevents hallucination)
- Reserved keyword handling (MySQL compatibility)
- Empty result detection and reporting
- Command-line interface for testing

---

## Architecture Options for Your MVP

### Option 1: Simple SQL + LLM (Recommended for MVP)
**Complexity:** ⭐ Easy
**Cost:** $ Low
**Setup Time:** 1-2 hours

**How it works:**
```
User Question → LLM generates SQL query → Execute on MySQL → LLM formats results
```

**Pros:**
- No vector database needed
- Uses existing views you already built
- Simple to understand and debug
- Leverages structured data directly

**Cons:**
- LLM must be good at SQL generation
- Less flexible for open-ended questions

**Best for:** Specific lookups ("What perks affect X?", "Show me Y stats")

---

### Option 2: Vector Database + Embeddings (Full RAG)
**Complexity:** ⭐⭐⭐ Moderate
**Cost:** $$ Medium
**Setup Time:** 1-2 days

**How it works:**
```
User Question → Convert to embedding → Find similar data in vector DB → LLM generates answer
```

**Pros:**
- Handles semantic/fuzzy queries better
- Can find related concepts automatically
- Better for conversational flow

**Cons:**
- Requires embedding generation
- Need vector database setup
- More complex architecture

**Best for:** Open-ended questions ("Recommend a stealth build", "What synergizes with X?")

---

### Option 3: Hybrid (SQL + Vector)
**Complexity:** ⭐⭐⭐⭐ Complex
**Cost:** $$$ Higher
**Setup Time:** 3-5 days

**How it works:**
```
User Question → Classify intent → Use SQL OR vector search → LLM generates answer
```

**Pros:**
- Best of both worlds
- Structured queries use SQL, semantic queries use vectors
- Most accurate results

**Cons:**
- Most complex to build and maintain
- Higher costs (embeddings + LLM calls)

**Best for:** Production system after MVP proves value

---

## Recommended MVP Stack

### Simple SQL + LLM Approach

**Tech Stack:**
- **LLM:** Anthropic Claude (Sonnet 3.5) or OpenAI GPT-4
- **Framework:** LangChain (optional) or direct API calls
- **Database:** Your existing MySQL f76 database
- **Interface:** Simple Python CLI (can add Streamlit web UI later)

**Why this approach:**
1. You already have RAG-optimized views (v_weapons_with_perks, etc.)
2. Structured data is perfect for SQL queries
3. Faster to build and test
4. Lower cost initially
5. Can upgrade to vector DB later if needed

---

## Step-by-Step Implementation (MVP)

### Step 1: Install Dependencies

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install LLM libraries
pip install anthropic openai langchain langchain-community

# Update requirements.txt
pip freeze > requirements.txt
```

### Step 2: Create RAG Query System

The implemented system is in `rag/query_engine.py` with the following key features:

**Core Architecture:**
```python
import anthropic
import mysql.connector
import os
import re
from typing import Dict, List

class FalloutRAG:
    def __init__(self):
        # Initialize Claude
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

        # Database connection
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'secret',
            'database': 'f76'
        }

        # Conversation history for context (stores last 3 exchanges)
        self.conversation_history = []
```

**Key Features Implemented:**

1. **Markdown Code Fence Removal** - Strips ````sql` and ` ``` from generated queries
2. **MySQL Reserved Keyword Handling** - Properly handles `rank`, `order`, etc. with backticks
3. **Empty Result Detection** - Returns clear message when queries return no data
4. **Strict Result Grounding** - System prompt prevents LLM from using training data
5. **Conversational Context** - Maintains last 3 Q&A exchanges for follow-up questions
6. **Schema Documentation** - Accurate field descriptions (e.g., armor_type: 'regular' or 'power')

**SQL Generation Prompt:**
- Enforces MySQL ONLY_FULL_GROUP_BY compatibility
- Includes proper schema with actual enum values
- Provides context hints (weapon_type vs weapon_class distinction)
- Requires backticks for reserved keywords

**Answer Formatting:**
- Uses system prompt to strictly limit responses to database results only
- Prevents hallucination by forbidding use of training data
- Returns empty result warnings instead of fabricating data

### Step 3: Create Simple CLI Interface

Create `rag/cli.py`:

```python
#!/usr/bin/env python3
"""Simple CLI for querying Fallout 76 build data"""

from query_engine import FalloutRAG

def main():
    print("=== Fallout 76 Build Assistant ===")
    print("Ask questions about weapons, perks, and armor!")
    print("Type 'exit' to quit\n")

    rag = FalloutRAG()

    while True:
        question = input("You: ").strip()

        if question.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        if not question:
            continue

        print("\nAssistant: ", end="")
        answer = rag.ask(question)
        print(answer)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
```

### Step 4: Set Up API Keys

```bash
# Get API key from: https://console.anthropic.com/
export ANTHROPIC_API_KEY="your-key-here"

# Or for OpenAI:
export OPENAI_API_KEY="your-key-here"
```

### Step 5: Test It!

```bash
python rag/cli.py
```

**Example questions to try:**
- "What perks affect the Enclave plasma gun?"
- "Show me all heavy armor sets"
- "What does Gunslinger do at each rank?"
- "Compare Combat armor vs Scout armor"
- "What's a good rifle build?"

**Testing Conversational Context:**
The system now supports follow-up questions using context from previous exchanges:
```
You: What's the best shotgun in the game?
Assistant: [Returns Combat shotgun info]

You: Compare that to the Gauss Shotgun
Assistant: [Understands "that" refers to Combat shotgun from previous answer]
```

The system maintains the last 3 Q&A exchanges to enable natural conversation flow.

---

## Cost Estimates

### Claude API (Recommended)
- **Model:** Claude Sonnet 3.5
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens
- **Typical query cost:** $0.01-0.03
- **100 queries/day:** ~$2-3/month

### OpenAI API (Alternative)
- **Model:** GPT-4 Turbo
- **Input:** $10 per million tokens
- **Output:** $30 per million tokens
- **Typical query cost:** $0.03-0.10
- **100 queries/day:** ~$9-10/month

---

## Upgrade Path: Adding Vector Database

If you want semantic search later:

### Option A: ChromaDB (Easiest)
```bash
pip install chromadb

# Example embedding script
from chromadb import Client
from chromadb.config import Settings

client = Client(Settings())
collection = client.create_collection("fallout76")

# Add weapon data as embeddings
weapons = query_database("SELECT * FROM v_weapons_with_perks")
for weapon in weapons:
    text = f"{weapon['weapon_name']}: {weapon['regular_perks']}"
    collection.add(
        documents=[text],
        metadatas=[weapon],
        ids=[f"weapon_{weapon['id']}"]
    )
```

### Option B: Pinecone (Cloud-hosted)
```bash
pip install pinecone-client

# Better for production, has free tier
```

---

## Tips for Better Results

### 1. Prompt Engineering
Give the LLM context about Fallout 76 terminology:

```python
system_prompt = """You are an expert Fallout 76 build advisor.
You understand:
- SPECIAL stats (Strength, Perception, Endurance, Charisma, Intelligence, Agility, Luck)
- Perk cards and their ranks
- Weapon types (rifles, pistols, heavy guns, melee)
- Build archetypes (bloodied, stealth commando, heavy gunner, etc.)

Always cite specific weapon/perk names and stats when answering."""
```

### 2. Conversation History (✅ Implemented)
The system now maintains conversation context automatically:
```python
# In __init__
self.conversation_history = []

# Before SQL generation, inject context
if self.conversation_history:
    context_section = "\n\nPrevious conversation context:\n"
    for entry in self.conversation_history[-3:]:  # Last 3 exchanges
        context_section += f"Q: {entry['question']}\nA: {entry['summary']}\n\n"
    sql_prompt = context_section + sql_prompt

# After generating answer, store in history
self.conversation_history.append({
    'question': question,
    'sql': sql_query,
    'summary': final_answer[:200] + "..." if len(final_answer) > 200 else final_answer
})
```

This enables natural follow-up questions like "compare that to X" where "that" refers to a previous result.

### 3. Error Handling
```python
def safe_query(self, sql: str) -> List[Dict]:
    try:
        return self.query_database(sql)
    except Exception as e:
        # Try to fix common SQL errors
        if "syntax error" in str(e):
            return self.regenerate_sql(sql, error=str(e))
        raise
```

---

## Next Steps After MVP

1. **Add Web Interface** - Build a Streamlit or Flask web UI
2. **Implement Caching** - Cache common queries to reduce API costs
3. **Add Authentication** - Protect your API keys
4. **Build Feedback Loop** - Track which queries work well
5. **Fine-tune Prompts** - Improve accuracy based on user questions
6. **Add Build Templates** - Pre-built answers for common builds
7. **Upgrade to Hybrid** - Add vector search for semantic queries

---

## Common Pitfalls to Avoid

❌ **Don't:** Let the LLM hallucinate data - always retrieve from database
✅ **Do:** Use RAG to ground responses in actual game data (✅ Implemented via system prompt)

❌ **Don't:** Send entire database to LLM context window
✅ **Do:** Retrieve only relevant data for each query (✅ Implemented)

❌ **Don't:** Expose raw SQL errors to users
✅ **Do:** Catch errors and retry with better prompts (✅ Basic error handling implemented)

❌ **Don't:** Hardcode API keys in code
✅ **Do:** Use environment variables (✅ Implemented)

❌ **Don't:** Ignore MySQL reserved keywords
✅ **Do:** Use backticks for columns like `rank`, `order`, etc. (✅ Implemented in prompt)

❌ **Don't:** Provide inaccurate schema information
✅ **Do:** Document actual enum values and field types (✅ Implemented - armor_type, weapon_class distinctions)

---

## Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [LangChain SQL Tutorial](https://python.langchain.com/docs/use_cases/sql/)
- [ChromaDB Quick Start](https://docs.trychroma.com/getting-started)
- [RAG Best Practices](https://www.anthropic.com/research/retrieval-augmented-generation)

---

## Questions?

This guide should get you from zero to a working MVP in a few hours. Start simple with SQL + LLM, then add complexity only if needed!
