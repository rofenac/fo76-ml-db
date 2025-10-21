# Fallout 76 Build Database & RAG System

A comprehensive Python-based data collection, database management, and **RAG-powered query system** for Fallout 76 game data. This project scrapes game information from Fallout Wiki, stores it in a normalized MySQL database, and provides an intelligent natural language interface for build optimization queries.

## Project Overview

**Goal:** Build a comprehensive database of Fallout 76 game data with an LLM-powered RAG (Retrieval Augmented Generation) system that helps players:
- Optimize character builds based on playstyle preferences
- Query game data using natural language ("What perks affect shotguns?")
- Get build recommendations ("Best mutations for a bloodied rifle build")
- Answer complex questions like "What consumables stack with Psychobuff?"

## Current Status (2025-10-20)

### ✅ **PHASE 1-4: COMPLETE** - Hybrid RAG System Operational

**Database:** 1,037 items (262 weapons, 477 armor, 240 perks, 28 legendary perks, 19 mutations, 11 consumables)
**Vector Database:** ChromaDB with 1,037+ OpenAI embeddings (1536 dimensions)
**RAG System:** Dual-mode (SQL + Vector) with intelligent routing
**System Health:** 96.7% (29/30 diagnostic tests passing)

**See `docs/TODO.md` for detailed roadmap and next steps.**

## Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repository_url>
cd fo76-ml-db

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web scraping)
playwright install chromium
```

### 2. Setup Database

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"

# Import schema
mysql -u root -p f76 < database/f76_schema.sql

# Set environment variables (create .env file)
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=f76
ANTHROPIC_API_KEY=your_api_key_here
EOF
```

### 3. Import All Data

```bash
# Import everything in one command
bash database/import_all.sh

# Or import individually:
python database/import_to_db.py -u root -p your_password -d f76  # Weapons & perks
python database/import_armor.py                                    # Armor
python database/import_mutations.py                                # Mutations
python database/import_consumables.py                              # Consumables
```

### 4. Populate Vector Database (For Semantic Search)

```bash
# Generate embeddings for all 1,037 items
# Requires OPENAI_API_KEY environment variable
# Cost: ~$0.001 (less than a penny!)
python rag/populate_vector_db.py
```

### 5. Run Hybrid RAG System

```bash
# Start interactive hybrid CLI (recommended - uses both SQL and vector search)
python rag/hybrid_cli.py

# Or use SQL-only CLI (original system)
python rag/cli.py

# Inspect vector database contents
python rag/inspect_vector_db.py

# View specific item embeddings
python rag/show_embeddings.py weapon_42
```

## Hybrid RAG System Usage

The system automatically routes queries to SQL (exact lookups) or Vector search (semantic/conceptual queries).

**Example Queries:**
- *Exact:* "What's the damage of the Gauss Shotgun?"
- *Conceptual:* "Best bloodied heavy gunner build"
- *Similarity:* "Weapons similar to The Fixer"

**See `docs/RAG_IMPLEMENTATION_GUIDE.md` for complete usage guide, examples, and architecture details.**

## Project Structure

```
fo76-ml-db/
├── docs/                             # All documentation
│   ├── README.md                     # This file
│   ├── CLAUDE.md                     # AI assistant guidance
│   ├── TODO.md                       # Project roadmap
│   ├── SCHEMA_DESIGN.md              # Database design
│   ├── RAG_IMPLEMENTATION_GUIDE.md   # RAG system guide
│   ├── SCRAPER_README.md             # Scraper documentation
│   └── IMPORT_GUIDE.md               # Database import guide
├── data/                             # All data files
│   ├── input/                        # Source CSV data
│   │   ├── Perks.csv                 # 240 perks, 449 ranks
│   │   ├── LegendaryPerks.csv        # 28 legendary perks
│   │   ├── human_corrected_weapons_clean.csv  # 262 weapons
│   │   ├── armor_unified.csv         # 477 armor pieces
│   │   ├── Mutations.csv             # 19 mutations
│   │   └── Consumables.csv           # 11 consumables
│   └── urls/                         # URL lists for scrapers
│       ├── urls.txt                  # Weapon URLs
│       ├── armor_urls.txt            # Armor URLs
│       ├── mutation_urls.txt         # Mutation URLs
│       └── consumable_urls.txt       # Consumable URLs
├── database/                         # Database schema and imports
│   ├── f76_schema.sql                # Complete schema
│   ├── import_to_db.py               # Weapons & perks import
│   ├── import_armor.py               # Armor import
│   ├── import_mutations.py           # Mutations import
│   ├── import_consumables.py         # Consumables import
│   └── import_all.sh                 # Master import script
├── scrapers/                         # Web scraping scripts
│   ├── scraper.py                    # Weapon scraper
│   ├── armor_scraper.py              # Armor scraper
│   ├── mutation_scraper.py           # Mutation scraper
│   ├── consumable_scraper.py         # Consumable scraper
│   └── legendary_perk_scraper.py     # Legendary perk scraper
├── rag/                              # Hybrid RAG system
│   ├── query_engine.py               # SQL-based RAG engine
│   ├── hybrid_query_engine.py        # Hybrid SQL + Vector engine
│   ├── cli.py                        # SQL-only interactive CLI
│   ├── hybrid_cli.py                 # Hybrid interactive CLI (recommended)
│   ├── populate_vector_db.py         # Generate vector embeddings
│   ├── inspect_vector_db.py          # View vector DB contents
│   ├── show_embeddings.py            # View embedding vectors
│   └── chroma_db/                    # ChromaDB storage (1,037+ embeddings)
├── tests/                            # Tests and validation
│   ├── validate_scraped_data.py      # Data validation
│   ├── test_mutations.py             # Mutation tests
│   └── diagnostics.py                # Full system diagnostic
├── react/                            # Frontend (skeleton)
└── requirements.txt                  # Python dependencies
```

## Database Architecture

### Core Tables

- **`weapons`** - 262 weapons with damage, type, class
- **`armor`** - 477 armor pieces (unified regular + power armor)
- **`perks`** - 240 regular SPECIAL perks
- **`perk_ranks`** - 449 rank-specific effects
- **`legendary_perks`** - 28 legendary perks
- **`legendary_perk_ranks`** - 112 legendary perk ranks
- **`mutations`** - 19 mutations with positive/negative effects
- **`consumables`** - 11 build-essential consumables (expandable)

### RAG-Optimized Views

Pre-built views simplify LLM queries:

- **`v_weapons_with_perks`** - Weapons with all affecting perks
- **`v_armor_complete`** - Complete armor data with resistances
- **`v_perks_all_ranks`** - Regular perks with all ranks
- **`v_legendary_perks_all_ranks`** - Legendary perks with ranks
- **`v_mutations_complete`** - Mutations with full details
- **`v_consumables_complete`** - Consumables with effects

**Example:**
```sql
-- Instead of complex JOINs, the LLM generates:
SELECT * FROM v_weapons_with_perks WHERE weapon_name = 'Enclave plasma gun';
```

## RAG System Features

- **Intent Classification** - Detects vague questions and asks for clarification
- **Conversational Context** - Maintains last 3 Q&A exchanges for follow-ups
- **Hallucination Prevention** - Strictly grounded to database results only
- **Game Mechanics Knowledge** - Understands build archetypes, mutations, perks
- **Error Handling** - MySQL compatibility, query validation, retry logic

**See `docs/RAG_IMPLEMENTATION_GUIDE.md` for detailed feature descriptions.**

## System Diagnostics

Run full system health check:

```bash
python diagnostics.py
```

**Output:**
```
╔═══════════════════════════════════════════════════════════════════╗
║  SUCCESS RATE: 96.7% (29/30 tests passing)                        ║
║  STATUS: ✓ ALL SYSTEMS OPERATIONAL                                ║
╚═══════════════════════════════════════════════════════════════════╝

DATABASE STATISTICS:
  Weapons:          262
  Armor Pieces:     477
  Regular Perks:    240
  Legendary Perks:  28
  Mutations:        19
  Consumables:      11
  Total Items:      1,037
```

## Web Scraping

### Scrape New Data

```bash
# Weapons
python scrapers/scraper.py -f data/urls/urls.txt -o output.csv

# Armor
python scrapers/armor_scraper.py -f data/urls/armor_urls.txt -o output.csv

# Mutations
python scrapers/mutation_scraper.py -f data/urls/mutation_urls.txt -o output.csv

# Consumables
python scrapers/consumable_scraper.py -f data/urls/consumable_urls.txt -o output.csv

# Use Playwright for JavaScript-heavy pages
python scrapers/scraper.py -f urls.txt -o output.csv --playwright
```

## Key Features

### Race Support (Human vs Ghoul)
- Tracks race-specific perks/mutations
- Ghoul-exclusive legendary perks: "Action Diet", "Feral Rage"
- Most content is universal (both races)

### Multi-Rank System
- Regular perks: 1-5 ranks (varies by perk)
- Legendary perks: Always 4 ranks with scaling effects
- Example: Follow Through - 10%/20%/30%/40% damage increase

### Mutation Mechanics
- 19 total mutations available
- Carnivore/Herbivore mutual exclusivity enforced
- Class Freak perk integration (-25%/-50%/-75% negative effects)
- Strange in Numbers perk integration (+25% positive effects when teamed)

### Consumable System
- Categories: chem, food, aid, alcohol, beverage
- Tracks: effects, duration, addiction risk, SPECIAL modifiers
- Build-focused curated dataset

## Documentation

- **[RAG_IMPLEMENTATION_GUIDE.md](docs/RAG_IMPLEMENTATION_GUIDE.md)** - Complete RAG system documentation
- **[TODO.md](docs/TODO.md)** - Project roadmap and task tracking
- **[SCHEMA_DESIGN.md](docs/SCHEMA_DESIGN.md)** - Database architecture
- **[CLAUDE.md](docs/CLAUDE.md)** - AI assistant guidance (for Claude Code)
- **[SCRAPER_README.md](docs/SCRAPER_README.md)** - Web scraping documentation
- **[IMPORT_GUIDE.md](docs/IMPORT_GUIDE.md)** - Database import guide

## API Costs

Typical usage: ~$0.01-0.03 per query (Claude Sonnet 4). For detailed cost breakdown, see `docs/RAG_IMPLEMENTATION_GUIDE.md`.

## Contributing

Personal project, but suggestions welcome!

## License

MIT License

## Acknowledgments

- Data sourced from [Fallout Wiki](https://fallout.fandom.com/)
- Built with Anthropic Claude API
- Powered by MySQL and Python
- Built for the Fallout 76 community

---

**System Status:** ✅ Fully Operational | **Database:** 1,037 items | **RAG:** Active | **Health:** 96.7%
