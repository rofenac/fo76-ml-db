# Fallout 76 Build Database & RAG System

A Python-based system that scrapes Fallout 76 game data from Fallout Wiki, stores it in a normalized MySQL database, and provides an intelligent natural language interface powered by RAG (Retrieval Augmented Generation) for build optimization queries.

## Quick Stats

- **Database**: 1,037 unique items (262 weapons, 477 armor, 240 perks, 28 legendary perks, 19 mutations, 11 consumables)
- **RAG System**: Hybrid SQL + Vector search with 1,330 OpenAI embeddings (1536 dimensions, includes all perk ranks)
- **Last Updated**: 2025-10-30

## Tech Stack

- **Backend**: Python 3.9+, MySQL 8.0+, ChromaDB
- **AI/ML**: Anthropic Claude (query generation), OpenAI (embeddings), LangChain (orchestration)
- **Scraping**: Playwright, BeautifulSoup4
- **Data**: Pandas, NumPy, scikit-learn

## Prerequisites

- Python 3.9+, MySQL 8.0+, Git
- [Anthropic API Key](https://console.anthropic.com/) (required - for SQL generation & responses)
- [OpenAI API Key](https://platform.openai.com/api-keys) (required - for vector embeddings & semantic search)

## Installation

```bash
# Clone and setup
git clone https://github.com/rofenac/fo76-ml-db.git
cd fo76-ml-db
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac | .venv\Scripts\activate (Windows)
pip install -r requirements.txt
playwright install chromium

# Setup MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"
mysql -u root -p f76 < database/f76_schema.sql

# Configure environment
cp .env.example .env
# Edit .env with your DB credentials and API keys:
#   - ANTHROPIC_API_KEY (for Claude - SQL generation & responses)
#   - OPENAI_API_KEY (for embeddings - vector search)
#   - DB_PASSWORD (MySQL password)

# Import data
bash database/import_all.sh

# Generate embeddings (required for vector search)
python rag/populate_vector_db.py  # Cost: ~$0.001 (generates 1,330 embeddings)
```

## Usage

```bash
# Interactive Hybrid RAG CLI (recommended)
./python-start.sh
# OR
python rag/cli.py

# Example queries:
# - "What perks affect shotguns?" (SQL search - exact)
# - "Best bloodied heavy gunner build" (Vector search - semantic)
# - "Weapons similar to The Fixer" (Vector search - similarity)
```

**Other Commands:**
```bash
python tests/diagnostics.py           # System health check
python rag/inspect_vector_db.py       # View vector database
python scrapers/scraper.py -f urls.txt -o output.csv  # Scrape new data
```

## Project Structure

```
fo76-ml-db/
├── data/
│   ├── input/          # Source CSV data (weapons, armor, perks, mutations, consumables)
│   └── urls/           # URL lists for scrapers
├── database/
│   ├── f76_schema.sql  # Complete database schema
│   └── import_*.py     # Import scripts
├── scrapers/           # Web scraping tools (weapon, armor, mutation, consumable scrapers)
├── rag/
│   ├── cli.py          # Main interactive CLI (hybrid SQL+Vector)
│   ├── hybrid_query_engine.py  # SQL + Vector routing engine
│   └── chroma_db/      # Vector database storage
├── tests/              # Validation and diagnostic scripts
└── docs/
    └── TODO.md         # Project roadmap and status
```

## Database Schema

### Core Tables
- `weapons` (262) - Damage, type, class
- `armor` (477) - Resistances, type, slot (unified regular + power armor)
- `perks` (240), `perk_ranks` (449) - SPECIAL perks with multi-rank support
- `legendary_perks` (28), `legendary_perk_ranks` (112) - 4-rank legendary perks
- `mutations` (19) - Positive/negative effects, exclusivity rules
- `consumables` (11) - Build-relevant food, chems, drinks with stat buffs

### RAG-Optimized Views
- `v_weapons_with_perks` - Weapons with affecting perks
- `v_armor_complete` - Complete armor with all resistances
- `v_perks_all_ranks` - Perks with rank progressions
- `v_legendary_perks_all_ranks` - Legendary perks with effects
- `v_mutations_complete` - Mutations with full effect details
- `v_consumables_complete` - Consumables with buffs

## RAG System

**Hybrid Architecture**: Combines SQL (exact queries) + Vector search (semantic/conceptual)

**Auto-routing Examples:**
- SQL: "What's the damage of the Gauss Shotgun?"
- Vector: "Best bloodied heavy gunner build"
- Vector: "Mutations for stealth commando"

**Features:**
- Natural language queries
- Conversational context (last 3 exchanges)
- Hallucination prevention (database-grounded only)
- Game mechanics knowledge (build archetypes, synergies)

**Performance:**
- Response time: 2-3 seconds
- Cost: ~$0.01-0.03/query (Claude Sonnet 4)

## Key Features

- **Race Support**: Human vs Ghoul-specific perks/mutations
- **Multi-Rank System**: 1-5 ranks (regular perks), 4 ranks (legendary)
- **Mutation Mechanics**: Carnivore/Herbivore exclusivity, Class Freak/Strange in Numbers interactions
- **Build Archetypes**: Understands bloodied, stealth commando, heavy gunner, VATS builds

## Roadmap

See [`docs/TODO.md`](docs/TODO.md) for:
- ✅ **Completed**: Weapons, armor, perks, mutations, consumables, RAG system with vector search
- 📋 **Planned**: Collectibles (bobbleheads/magazines), legendary effects, SPECIAL tracking, damage calculator
- 🎯 **Stretch Goals**: Full-stack web GUI

## Contributing

Personal project, but suggestions welcome via issues.

## License

MIT License

## Acknowledgments

- Data from [Fallout Wiki](https://fallout.fandom.com/)
- Powered by Anthropic Claude & OpenAI
- Built for the Fallout 76 community

---

**Status**: ✅ Fully Operational | **Database**: 1,037 unique items | **Embeddings**: 1,330 | **RAG**: Hybrid SQL+Vector | **Health**: 100%
