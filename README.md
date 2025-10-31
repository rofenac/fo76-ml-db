# Fallout 76 Build Database & RAG System

Python-based system that scrapes FO76 data, stores it in normalized MySQL, and provides natural language queries via RAG (Retrieval Augmented Generation).

## Quick Stats

- **Database**: 1,037 items (262 weapons, 477 armor, 240 perks, 28 legendary perks, 19 mutations, 11 consumables)
- **RAG**: Hybrid SQL + Vector search, 1,517 OpenAI embeddings (1536-dim)
- **Last Updated**: 2025-10-30

## Tech Stack

- **Backend**: Python 3.9+, MySQL 8.0+, ChromaDB
- **AI/ML**: Anthropic Claude (SQL gen, responses), OpenAI (embeddings), LangChain
- **Scraping**: Playwright, BeautifulSoup4

## Prerequisites

- Python 3.9+, MySQL 8.0+, Git
- [Anthropic API Key](https://console.anthropic.com/) (SQL generation & responses)
- [OpenAI API Key](https://platform.openai.com/api-keys) (vector embeddings)

## Installation

```bash
# Clone and setup
git clone https://github.com/rofenac/fo76-ml-db.git
cd fo76-ml-db
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Setup MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"
mysql -u root -p f76 < database/f76_schema_normalized.sql

# Configure environment
cp .env.example .env
# Edit .env with DB credentials and API keys

# Import data
python database/import_to_db_normalized.py
python database/import_weapon_mechanics.py  # Special weapon mechanics

# Generate embeddings (~$0.001, required for vector search)
python rag/populate_vector_db.py
```

## Usage

```bash
# Interactive Hybrid RAG CLI
./python-start.sh  # OR: python rag/cli.py

# Example queries:
# - "What perks affect shotguns?" (SQL - exact)
# - "Best bloodied heavy gunner build" (Vector - semantic)
# - "Which weapons can be charged?" (Weapon mechanics)
```

**Other Commands:**
```bash
python tests/diagnostics.py            # Health check
python rag/inspect_vector_db.py        # View vector DB
python database/test_weapon_mechanics.sql  # Test mechanics
```

## Project Structure

```
fo76-ml-db/
├── data/
│   ├── input/     # CSV data
│   └── urls/      # Scraper URLs
├── database/
│   ├── f76_schema_normalized.sql  # Normalized schema
│   ├── import_*.py                # Import scripts
│   └── add_weapon_mechanics.sql   # Weapon mechanics migration
├── scrapers/      # Web scrapers
├── rag/
│   ├── cli.py                      # Interactive CLI
│   ├── hybrid_query_engine.py      # SQL + Vector routing
│   └── chroma_db/                  # Vector store
└── docs/          # Documentation
```

## Database Schema

### Core Tables
- `weapons` (262) - Damage, type, class, **special mechanics**
- `weapon_mechanics` - Charge, spin-up, chain lightning, explosive AOE
- `armor` (477) - Resistances, type, slot
- `perks` (240), `perk_ranks` (449) - SPECIAL perks, multi-rank
- `legendary_perks` (28), `legendary_perk_ranks` (112) - 4-rank legendary perks
- `mutations` (19) - Effects, exclusivity
- `consumables` (11) - Build-relevant buffs

### Weapon Mechanics
Special weapon behaviors:
- **Charge**: Gauss rifle/shotgun/pistol (50% uncharged → 100% charged)
- **Chain Lightning**: Tesla rifle (65% → 42.25% per hop)
- **Spin-Up**: Minigun, Gauss minigun, Gatling guns, Pepper Shaker
- **Explosive AOE**: Fat Man, Missile launcher, grenade launchers
- **Charge + Self-Damage**: Salvaged Assaultron head (irradiates user)

See `docs/WEAPON_MECHANICS.md` for details.

## RAG System

**Hybrid Architecture**: SQL (exact) + Vector (semantic)

**Auto-routing:**
- SQL: "Damage of Gauss Shotgun?"
- Vector: "Best bloodied heavy gunner build"

**Features:**
- Natural language queries
- Conversational context (3-message history)
- Hallucination prevention (database-grounded)
- Game mechanics knowledge

**Performance:** 2-3s response, ~$0.01-0.03/query (Claude Sonnet 4)

## Key Features

- **Race Support**: Human/Ghoul-specific perks
- **Multi-Rank System**: 1-5 ranks (regular), 4 ranks (legendary)
- **Mutation Mechanics**: Exclusivity, Class Freak/Strange in Numbers
- **Build Archetypes**: Bloodied, stealth commando, heavy gunner, VATS

## Documentation

- `docs/WEAPON_MECHANICS.md` - Weapon special mechanics system
- `docs/ANTI_HALLUCINATION.md` - LLM hallucination prevention
- `docs/f76_normalized_erd.mmd` - Database ER diagram

## Contributing

Personal project. Suggestions via issues welcome.

## License

MIT

## Acknowledgments

- Data: [Fallout Wiki](https://fallout.fandom.com/)
- Powered by: Anthropic Claude, OpenAI
- For: Fallout 76 community

---

**Status**: ✅ Operational | **DB**: 1,037 items | **Embeddings**: 1,517 | **RAG**: Hybrid SQL+Vector
