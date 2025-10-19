# Fallout 76 Build Database & RAG System

A comprehensive Python-based data collection, database management, and **RAG-powered query system** for Fallout 76 game data. This project scrapes game information from Fallout Wiki, stores it in a normalized MySQL database, and provides an intelligent natural language interface for build optimization queries.

## Project Overview

**Goal:** Build a comprehensive database of Fallout 76 game data with an LLM-powered RAG (Retrieval Augmented Generation) system that helps players:
- Optimize character builds based on playstyle preferences
- Query game data using natural language ("What perks affect shotguns?")
- Get build recommendations ("Best mutations for a bloodied rifle build")
- Answer complex questions like "What consumables stack with Psychobuff?"

## Current Status (2025-10-19)

### ✅ **PHASE 1-3: COMPLETE** - Full Data Collection & RAG System

**Database:** 1,037 game items fully imported
- ✅ **262 Weapons** (Ranged: 127, Melee: 94, Grenade: 26, Mine: 8, Thrown: 4, Camera: 3)
- ✅ **477 Armor Pieces** (Regular: 291, Power Armor: 186)
- ✅ **240 Regular Perks** (449 total ranks)
- ✅ **28 Legendary Perks** (112 total ranks)
- ✅ **19 Mutations** (with positive/negative effects, exclusivity rules)
- ✅ **11 Consumables** (build-essential chems, food, aid items)

**RAG System:** MVP Operational
- ✅ Natural language SQL query generation
- ✅ Conversational context memory (last 3 exchanges)
- ✅ Intent classification (detects vague questions, asks for clarification)
- ✅ Strict database grounding (prevents hallucination)
- ✅ Game mechanics knowledge integration
- ✅ CLI interface functional
- ✅ Supports queries across all data types (weapons, armor, perks, mutations, consumables)

**System Health:** 96.7% (29/30 diagnostic tests passing)

### ⏳ **PHASE 4: IN PROGRESS** - Enhancements

- ⏳ Awaiting user's curated consumables list for expansion
- ⏳ React frontend (skeleton exists in `/react` folder)
- ⏳ Vector database integration (for semantic search)

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

### 4. Run RAG System

```bash
# Start interactive CLI
python rag/cli.py

# Or test specific queries
python test_mutations.py
```

## RAG System Usage

### Example Queries

**Weapons:**
```
You: What shotguns do the most damage?
You: List all heavy weapons
You: Compare Combat shotgun vs Gauss shotgun
```

**Perks:**
```
You: What perks affect shotguns?
You: Show me all Strength perks
You: What does Gunslinger do at each rank?
```

**Mutations:**
```
You: List all mutations
You: What does Marsupial do?
You: Which mutations are mutually exclusive?
You: What mutations help with carry weight?
```

**Consumables:**
```
You: What chems boost damage?
You: Best food for XP farming?
You: What heals me besides Stimpaks?
```

**Complex Build Questions:**
```
You: Best perks for a bloodied rifle build
You: How do I min/max my shotgun build?
You: What mutations work with heavy gunner?
```

### Intent Classification

The RAG system intelligently handles vague questions:

```
You: What's the best weapon?
Assistant: I need more information. What do you mean by "best"?
  1. Highest damage output?
  2. Best for a specific build type?
  3. Most versatile overall?

You: Highest damage output for rifles
Assistant: [Returns top damage rifles with stats]
```

## Project Structure

```
fo76-ml-db/
├── docs/                             # All documentation
│   ├── README.md                     # This file
│   ├── CLAUDE.md                     # AI assistant guidance
│   ├── TODO.md                       # Project roadmap
│   ├── SCHEMA_DESIGN.md              # Database design
│   ├── RAG_IMPLEMENTATION_GUIDE.md   # RAG system guide
│   └── RAG_ENHANCEMENTS.md           # Recent enhancements
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
├── rag/                              # RAG system
│   ├── query_engine.py               # Core RAG engine
│   └── cli.py                        # Interactive CLI
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

### 1. Intent Classification
- Detects vague/ambiguous questions
- Asks clarifying questions before querying
- Categories: SPECIFIC, VAGUE_CRITERIA, VAGUE_BUILD, AMBIGUOUS

### 2. Conversational Context
- Maintains last 3 Q&A exchanges
- Supports follow-up questions ("Compare that to X")
- Natural conversation flow

### 3. Hallucination Prevention
- Strict grounding to database results ONLY
- Forbidden from using training data
- Empty result detection with clear messaging

### 4. Game Mechanics Knowledge
- Weapon damage level tiers
- Character races (Human vs Ghoul)
- Build archetypes (Bloodied, Stealth, etc.)
- Armor types and resistances
- Mutation mechanics (Class Freak, Strange in Numbers)
- Consumable categories and effects

### 5. Error Handling
- MySQL reserved keyword handling (backticks)
- ONLY_FULL_GROUP_BY compatibility
- Query validation and retry logic

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

- **[RAG_IMPLEMENTATION_GUIDE.md](docs/RAG_IMPLEMENTATION_GUIDE.md)** - RAG system architecture and implementation
- **[RAG_ENHANCEMENTS.md](docs/RAG_ENHANCEMENTS.md)** - Recent enhancements and features
- **[SCHEMA_DESIGN.md](docs/SCHEMA_DESIGN.md)** - Database architecture
- **[TODO.md](docs/TODO.md)** - Project roadmap and status
- **[CLAUDE.md](docs/CLAUDE.md)** - AI assistant guidance

## API Costs

### Anthropic Claude (Recommended)
- **Model:** Claude Sonnet 4
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens
- **Typical query cost:** $0.01-0.03
- **100 queries/day:** ~$2-3/month

## Development Timeline

**Week 5** (Current) - RAG MVP complete! Mutations and consumables systems added.
**Week 4** - Discovered Claude Code. Made huge progress on database.
**Week 3** - Rebuilt from scratch with better architecture.
**Week 2** - Initial attempts, started over.
**Week 1** - Project planning and research.

## Future Plans

### Phase 4: Data Expansion
- [ ] Expand consumables (user-curated list pending)
- [ ] Add legendary weapon/armor effects
- [ ] SPECIAL stat tracking
- [ ] Status effects/buffs

### Phase 5: Advanced RAG
- [ ] Vector database integration (ChromaDB/Pinecone)
- [ ] Hybrid SQL + semantic search
- [ ] Build recommendation engine
- [ ] Damage calculator

### Phase 6: Frontend
- [ ] React web interface (skeleton exists)
- [ ] Interactive build planner
- [ ] Character sheet integration
- [ ] Build sharing/export

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
