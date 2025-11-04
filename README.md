# Fallout 76 Build Database & RAG System

Python-based system that scrapes FO76 data, stores it in normalized MySQL, and provides natural language queries via RAG (Retrieval Augmented Generation).

## Quick Stats

- **Database**: 1,206 items (262 weapons, 477 armor, 240 perks, 28 legendary perks, 19 mutations, 180 consumables, collectibles)
- **RAG**: Hybrid SQL + Vector search, 1,519 OpenAI embeddings (1536-dim, cleaned 2025-11-03)
- **Architecture**: Centralized database utility with MCP integration
- **Performance**: 5-10x faster queries, 300x faster lookups

## Tech Stack

- **Backend**: Python 3.9+, MySQL 8.0+, ChromaDB, FastAPI
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS
- **AI/ML**: Anthropic Claude (SQL generation, responses), OpenAI (embeddings)
- **Scraping**: Playwright, BeautifulSoup4
- **Database**: Centralized utility (`database/db_utils.py`) with connection pooling and caching

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
python database/import_weapon_mechanics.py

# Generate embeddings (~$0.001)
python rag/populate_vector_db.py
```

## Usage

### Interactive RAG CLI

```bash
./python-start.sh  # OR: python rag/cli.py

# Example queries:
# - "What perks affect shotguns?" (SQL - exact)
# - "Best bloodied heavy gunner build" (Vector - semantic)
# - "Which weapons can be charged?" (Weapon mechanics)
```

### REST API Server

```bash
# Start FastAPI server
./api-start.sh  # OR: cd api && uvicorn main:app --reload

# API available at:
# - http://localhost:8000 - Base URL
# - http://localhost:8000/docs - Interactive API documentation
# - http://localhost:8000/stats - Database statistics
```

**API Endpoints:**
- `GET /api/weapons` - List weapons (paginated, filterable)
- `GET /api/armor` - List armor pieces
- `GET /api/perks` - List perks (regular + legendary)
- `GET /api/mutations` - List mutations
- `GET /api/consumables` - List consumables (chems, food, drinks)
- `GET /api/collectibles` - List collectibles (magazines, bobbleheads)
- `POST /api/rag/query` - Natural language queries

See `api/README.md` for complete API documentation.

### React Frontend

```bash
cd react
npm install
npm run dev  # http://localhost:5173
```

## Architecture

### Database Layer

**Centralized Database Utility** (`database/db_utils.py`):
- Singleton pattern for connection reuse
- Query caching for lookup tables (300x faster)
- Unified API for all database operations
- Environment-based configuration

**Before refactoring**:
```python
conn = mysql.connector.connect(...)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM weapons")
results = cursor.fetchall()
cursor.close()
conn.close()
```

**After refactoring**:
```python
from database.db_utils import get_db
results = get_db().execute_query("SELECT * FROM weapons")
```

### RAG System

**Hybrid Architecture**: SQL (exact queries) + Vector search (semantic queries)

**Auto-routing**:
- SQL: "Damage of Gauss Shotgun?" → Direct database lookup
- Vector: "Best bloodied heavy gunner build" → Semantic search + enrichment

**Features**:
- Natural language queries
- Conversational context (3-message history)
- Hallucination prevention (database-grounded)
- Game mechanics knowledge

**Performance**: 2-3s response, ~$0.01-0.03/query (Claude Sonnet 4)

## Project Structure

```
fo76-ml-db/
├── api/                    # FastAPI REST API
│   ├── main.py             # API entry point
│   ├── routes/             # API endpoints
│   │   ├── weapons.py
│   │   ├── armor.py
│   │   ├── perks.py
│   │   ├── mutations.py
│   │   ├── consumables.py
│   │   └── rag.py
│   └── models/             # Pydantic models
├── react/                  # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   └── package.json
├── data/
│   ├── input/              # CSV source data
│   └── urls/               # Scraper URL lists
├── database/
│   ├── db_utils.py         # Core database utility (use this!)
│   ├── import_utils.py     # Bulk import helpers
│   ├── legacy_connector.py # Compatibility bridge
│   ├── f76_schema_normalized.sql
│   └── import_*.py         # Data import scripts
├── rag/
│   ├── cli.py              # Interactive CLI
│   ├── hybrid_query_engine.py  # SQL + Vector routing
│   ├── query_engine.py     # SQL-based RAG
│   ├── populate_vector_db.py
│   └── chroma_db/          # Vector store
├── scrapers/               # Web scrapers
├── scripts/                # Wrapper scripts for imports
├── tests/                  # Test and diagnostic scripts
├── docs/                   # Documentation
├── api-start.sh            # API server launcher
└── python-start.sh         # RAG CLI launcher
```

## Database Schema

### Core Tables
- **weapons** (262) - Damage, type, class, special mechanics
- **weapon_mechanics** - Charge, spin-up, chain lightning, explosive AOE
- **armor** (477) - Resistances, type, slot
- **perks** (240), **perk_ranks** (449) - SPECIAL perks with 1-5 ranks
- **legendary_perks** (28), **legendary_perk_ranks** (112) - 4-rank legendary perks
- **mutations** (19) - Effects, exclusivity (Carnivore/Herbivore)
- **consumables** (180) - Chems, food, drinks, aid items with effects and durations
- **collectibles** - Magazines, bobbleheads, and other collectible items with effects

### Lookup Tables
- **races** - Human, Ghoul
- **special_attributes** - S, P, E, C, I, A, L
- **damage_types** - Physical, Energy, Radiation, etc.
- **weapon_types**, **weapon_classes** - Ranged/Melee, Rifle/Shotgun/Pistol/etc.

### Views (for queries)
- `v_weapons_with_perks` - Weapons with applicable perks
- `v_armor_complete` - Armor with full stats
- `v_perks_all_ranks` - Perks with all rank details
- `v_legendary_perks_all_ranks` - Legendary perks with ranks
- `v_mutations_complete` - Mutations with effects
- `v_consumables_complete` - Consumables with modifiers
- `v_collectibles_complete` - Collectibles with effects and series info

## Key Features

- **Race Support**: Human/Ghoul-specific perks
- **Multi-Rank System**: 1-5 ranks (regular perks), 4 ranks (legendary perks)
- **Mutation Mechanics**: Exclusivity, Class Freak/Strange in Numbers
- **Build Archetypes**: Bloodied, stealth commando, heavy gunner, VATS
- **Weapon Mechanics**: Charge, spin-up, chain lightning, explosive AOE

## Contributing

Personal project. Suggestions via issues welcome.

## License

MIT

## Acknowledgments

- Data: [Fallout Wiki](https://fallout.fandom.com/)
- Powered by: Anthropic Claude, OpenAI
- For: Fallout 76 community
