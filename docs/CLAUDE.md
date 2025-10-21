# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Great Fallout 76 DB Project is a Python-based data collection and database management system for Fallout 76 game data. The project scrapes comprehensive game data (weapons, armor, power armor, perks, legendary perks) from Fallout Wiki pages and stores it in a normalized MySQL database designed to power a RAG (Retrieval Augmented Generation) system for build optimization.

**Project Goal:** Build a RAG-powered LLM system to help players optimize character builds, query game data, and answer complex questions like "What's the best bloodied heavy gunner build for solo play?"

## Current Status (Last Updated: 2025-10-20)

### ✅ Phase 1-4 Complete: Hybrid RAG System Operational

**Database:** 1,037 items across 6 data types (weapons, armor, perks, legendary perks, mutations, consumables)
**Vector Database:** ChromaDB with OpenAI embeddings (see README.md for details)
**System Health:** 96.7% (29/30 diagnostic tests passing)

For detailed statistics, see README.md.

### ✅ Hybrid RAG System

The project features a dual-mode RAG system:
- **SQL mode** - Exact queries via natural language → SQL generation
- **Vector mode** - Conceptual/semantic queries via ChromaDB embeddings
- **Hybrid routing** - Automatic intent classification chooses best method

**Key RAG Files:**
- `rag/hybrid_query_engine.py` - Main hybrid engine (recommended)
- `rag/query_engine.py` - SQL-only engine
- `rag/hybrid_cli.py` - Interactive CLI
- `rag/populate_vector_db.py` - Vector DB population script
- `rag/chroma_db/` - ChromaDB persistent storage

**See `docs/RAG_IMPLEMENTATION_GUIDE.md` for complete RAG documentation, usage examples, and implementation details.**

### 🔄 Next Phase

See `docs/TODO.md` for the full project roadmap and next steps.

## Environment Setup

This project uses Python with a virtual environment:

```bash
# Create and activate virtual environment (if needed)
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JavaScript-heavy pages)
playwright install chromium
```

Key dependencies:
- `beautifulsoup4` and `lxml` - HTML parsing from wiki pages
- `playwright` - Browser automation for dynamic content
- `pandas` - Data manipulation and CSV processing
- `mysql-connector-python` - MySQL database connectivity
- `requests` - HTTP requests for web scraping

## Database Architecture

The project uses a MySQL database (`f76`) with a normalized schema defined in `f76_schema.sql`.

### Core Tables

1. **weapons** - Weapon data table (262 rows)
   - Contains: name, type, class, level, damage, perks_raw, source_url
   - Unique constraint on weapon name
   - Indexed on: type, class
   - Weapon types: Ranged (127), Melee (94), Grenade (26), Mine (8), Thrown (4), Camera (3)
   - Classes include: Non-automatic pistol, Heavy gun, Rifle, Shotgun, One-Handed, Two-Handed, Unarmed, etc.

2. **armor** - UNIFIED armor data table (477 rows - regular + power armor merged)
   - Contains: name, class, slot, damage_resistance, energy_resistance, radiation_resistance, cryo_resistance, fire_resistance, poison_resistance, set_name, armor_type, level, source_url
   - **armor_type**: ENUM('regular', 'power') - distinguishes regular armor from power armor
   - **No unique constraint on name** - same piece exists at multiple levels
   - **One row per piece per level** - normalized for accurate stat tracking
   - Indexed on: name, set_name, slot, class, armor_type, level
   - **Note:** Power armor no longer has separate table - merged for schema consistency

3. **perks** - Regular SPECIAL perks base table (240 rows)
   - Contains: name, special, level, race
   - Unique constraint on perk name
   - Indexed on: special, race

4. **perk_ranks** - Regular perk ranks (449 rows)
   - Contains: perk_id, `rank`, description, form_id
   - Foreign key to perks(id) with CASCADE delete
   - **Important:** `rank` is a MySQL reserved keyword - must use backticks in queries

5. **legendary_perks** - Legendary perks base table (28 rows)
   - Contains: name, description, race
   - Unique constraint on perk name
   - Indexed on: race

6. **legendary_perk_ranks** - Legendary perk ranks (112 rows = 28 perks × 4 ranks)
   - Contains: legendary_perk_id, `rank`, description, effect_value, effect_type
   - Foreign key to legendary_perks(id) with CASCADE delete
   - **Important:** `rank` is a MySQL reserved keyword - must use backticks

### Junction Tables (Many-to-Many Relationships)

7. **weapon_perks** - Links weapons to regular perks (1,685 rows)
   - Primary key: (weapon_id, perk_id)
   - Foreign keys with CASCADE delete

8. **weapon_legendary_perk_effects** - Links weapons to legendary perks
   - Primary key: (weapon_id, legendary_perk_id)
   - Foreign keys with CASCADE delete

**Note:** Armor perk junction tables were removed because all armor perks (Armorer, Fix It Good, White Knight, Lucky Break, Funky Duds, Sizzling Style) affect ALL armor equally - no item-specific tracking needed.

### Future Tables

9. **weapon_perk_rules** - Conditional perk application rules (schema ready, unpopulated)
    - Stores conditions: weapon_class, fire_mode, scope_state, aim_state, vats_state
    - For tracking context-specific perk applications (e.g., "only when scoped", "only in ADS")

### RAG-Optimized Views

The schema includes pre-built views (prefixed with `v_`) for efficient LLM queries. Views are **virtual tables** that combine data from multiple tables using optimized JOINs.

**Purpose:** Simplify RAG system queries - the LLM can query a view instead of writing complex multi-table joins.

**The 4 Views:**

1. **v_weapons_with_perks** - Complete weapon info with all affecting perks
   - Returns: weapon details + semicolon-separated perk lists (regular + legendary)
   - Example: `SELECT * FROM v_weapons_with_perks WHERE weapon_name = 'Enclave plasma gun'`
   - Use: "What perks affect this weapon?" or "Show all pistols with their perks"

2. **v_armor_complete** - Unified armor view (regular + power armor)
   - Returns: armor piece with all resistances (DR, ER, RR, Cryo, Fire, Poison)
   - Example: `SELECT * FROM v_armor_complete WHERE armor_type = 'power'`
   - Use: "Show power armor pieces" or "Compare armor sets"

3. **v_perks_all_ranks** - Regular SPECIAL perks with all rank details
   - Returns: perk info + rank descriptions (1-5 ranks per perk)
   - Example: `SELECT * FROM v_perks_all_ranks WHERE perk_name = 'Gunslinger'`
   - Use: "What does Gunslinger do at each rank?"

4. **v_legendary_perks_all_ranks** - Legendary perks with rank progression
   - Returns: legendary perk + rank effects (1-4 ranks per perk)
   - Example: `SELECT * FROM v_legendary_perks_all_ranks WHERE perk_name = 'Follow Through'`
   - Use: "How does Follow Through scale from rank 1 to 4?"

**Key Benefit:** Views auto-update when data changes - no maintenance required. See SCHEMA_DESIGN.md for detailed documentation.

### Database Setup

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"

# Import schema (drops all tables first, then recreates)
mysql -u root -p f76 < database/f76_schema.sql

# Import data (run from project root)
python database/import_to_db.py -u root -p <password>
python database/import_armor.py
```

**Important MySQL 8.0 Note:** The `rank` column is a reserved keyword. All queries must use backticks: `` `rank` ``

## Data Files

### Input Data

- **data/urls/urls.txt** - 257 Fallout Wiki weapon URLs (all scraped) ✅
- **data/urls/armor_urls.txt** - 18 armor set URLs (all scraped) ✅
- **data/urls/power_armor_urls.txt** - 12 power armor set URLs (all scraped) ✅
- **data/urls/legendary_perk_urls.txt** - 28 legendary perk URLs (all scraped) ✅
- **data/input/Perks.csv** - 240 regular SPECIAL perks with 449 ranks
  - Columns: name, special, level, race, rank, description, form_id
- **data/input/LegendaryPerks.csv** - 28 legendary perks with 112 total ranks (28 × 4)
  - Columns: name, rank, description, effect_value, effect_type, form_id, race

### Scraped/Processed Data

- **data/input/human_corrected_weapons_clean.csv** - 262 weapons (all imported) ✅
  - Columns: Name, Type, Class, Level, Damage, Perks, Source URL
  - Authoritative source: Exported from database after manual corrections
- **data/input/armor_unified.csv** - 477 armor pieces (all imported) ✅
  - Contains: 291 regular armor + 186 power armor
  - Columns: Name, Class, Slot, Armor Type, Damage Resistance, Energy Resistance, Radiation Resistance, Cryo Resistance, Fire Resistance, Poison Resistance, Set Name, Level, Source URL
  - **Format:** One row per piece per level (normalized level data)
  - **Armor Type:** "regular" or "power" - distinguishes armor categories
  - Manually collected data covering 18 regular armor sets + 12 power armor sets across all levels

## Data Processing Workflow

The typical workflow for this project:

1. **Scraping** - Extract data from Fallout Wiki URLs
   - Use `scrapers/scraper.py`, `scrapers/armor_scraper.py`, `scrapers/power_armor_scraper.py`, `scrapers/legendary_perk_scraper.py`
   - Playwright/BeautifulSoup4 to parse wiki pages
   - Handle dynamic content and infobox tables

2. **Validation** (Optional)
   - Validate against canonical perk list (data/input/Perks.csv)
   - Check form IDs, editor IDs, required fields

3. **Import** - Load data into MySQL database
   - `database/import_to_db.py` - Imports weapons, perks, legendary perks, and populates weapon_perks junction table
   - `database/import_armor.py` - Imports unified armor data (regular + power armor)

## Key Data Patterns

### Perk Parsing

Perks in the raw data use complex notation:
- "Bloody Mess" - Simple perk
- "Gunslinger (Expert, Master)" - Multiple ranks (expands to Gunslinger, Gunslinger Expert, Gunslinger Master)
- "Sniper (scoped) only" - Conditional application
- "Pistol: Gun Runner, Modern Renegade, Crack Shot (sighted only)" - Class-specific with conditions

When processing perks:
- Split on semicolons and commas
- Handle parenthetical qualifiers separately
- Map variations to canonical perk names from Perks.csv
- The import script automatically handles Expert/Master variants
- Conditions like "scoped only" are stripped for perk matching
- Store conditions in `weapon_perk_rules` if detailed tracking is needed (future enhancement)

### Weapon Classification

Weapons have multiple classification attributes:
- **Type** - "Ranged" (127), "Melee" (94), "Grenade" (26), "Mine" (8), "Thrown" (4), "Camera" (3)
- **Class** - Detailed weapon subtype:
  - Ranged: "Non-automatic pistol", "Heavy gun", "Rifle", "Shotgun", "Automatic Rifle", "Bow", etc.
  - Melee: "One-Handed", "Two-Handed", "Unarmed"
  - Grenades/Mines: Typically no class specified
- **Damage** - Weapon damage values, often level-scaled (e.g., "24 / 28 / 32")

### Armor Classification (Unified Regular + Power Armor)

All armor (regular and power armor) uses the unified armor table with the following classification:
- **armor_type** - ENUM: "regular" or "power"
- **class** - For regular armor only: "Light", "Sturdy", "Heavy" (NULL for power armor)
- **slot** - Piece location: "Chest", "Helmet", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Torso"
- **set_name** - Armor set identifier (e.g., "Combat armor", "T-45 power armor", "X-01 power armor")
- **level** - Level requirement (one row per piece per level for accurate stat tracking)

**Regular Armor Sets (18):** Combat armor, Scout armor, Marine armor, Leather armor, Metal armor, Raider armor, Robot armor, Wood armor, Trapper armor, Secret Service armor, Covert Scout armor, BoS Recon armor, Solar armor, Thorn armor, Strangler heart armor (non-PA), Arctic Marine armor, Enclave armor, Union armor

**Power Armor Sets (12):** T-45, T-51b, T-60, X-01, Ultracite, T-65, Hellcat, Strangler heart, Union, Vulcan, Excavator, Raider

**Note:** Vulcan Power Armor is not yet fully populated - awaiting per-piece stat data from wiki.

### Race Support

The database tracks race-specific perks:
- **Regular perks:** Most are universal ("Human, Ghoul")
- **Legendary perks:** 26 universal, 2 ghoul-only ("Action Diet", "Feral Rage")

## Web Scraping

### Running the Scrapers

All scrapers follow the same command-line pattern:

```bash
# Weapon scraper (COMPLETE - 262 weapons)
python scrapers/scraper.py -f data/urls/urls.txt -o weapons_scraped.csv
python scrapers/scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser.csv

# Armor scraper (COMPLETE - 18 armor sets)
python scrapers/armor_scraper.py -f data/urls/armor_urls.txt -o armor_scraped.csv
python scrapers/armor_scraper.py -u "https://fallout.fandom.com/wiki/Combat_armor_(Fallout_76)" -o output.csv

# Power armor scraper (COMPLETE - 72 power armor pieces)
python scrapers/power_armor_scraper.py -f data/urls/power_armor_urls.txt -o power_armor_scraped.csv
python scrapers/power_armor_scraper.py -u "https://fallout.fandom.com/wiki/T-45_power_armor_(Fallout_76)" -o output.csv

# Legendary perk scraper (COMPLETE - 28 legendary perks, 112 ranks)
python scrapers/legendary_perk_scraper.py -f data/urls/legendary_perk_urls.txt -o LegendaryPerks.csv
python scrapers/legendary_perk_scraper.py -u "https://fallout.fandom.com/wiki/Follow_Through" -o output.csv

# Use Playwright for JavaScript-heavy pages (add --playwright flag)
python scrapers/scraper.py -f data/urls/urls.txt -o weapons.csv --playwright
```

All scrapers:
- Extract complete data from infobox (Form ID, Editor ID, stats, etc.)
- Intelligently parse perks from categorized sections (Damage, Legendary, Sneak, Weight, etc.)
- Handle conditional perks ("scoped only", "pistol only", "sighted", etc.)
- Validate perks against canonical list in Perks.csv
- Handle Expert/Master perk variants automatically
- Log progress and errors

### Data Validation

Validate scraped data before importing to database:

```bash
python tests/validate_scraped_data.py weapons_scraped.csv
```

This checks:
- Required fields are present (Name, Form ID, Editor ID, Source URL)
- Form IDs are valid 8-digit hex values (if present)
- Perks match canonical list
- Data completeness (flags missing Type, Level, etc.)

## Import Scripts

### Main Import Script (`import_to_db.py`)

Imports weapons, perks, legendary perks, and populates junction tables.

```bash
# Using command-line arguments (run from project root)
python database/import_to_db.py -u root -p secret

# Using environment variables
export MYSQL_USER=root
export MYSQL_PASS=secret
python database/import_to_db.py

# Custom files/settings
python database/import_to_db.py \
  -u root -p secret \
  -H localhost -d f76 \
  --perks-csv data/input/Perks.csv \
  --legendary-perks-csv data/input/LegendaryPerks.csv \
  --weapons-csv data/input/human_corrected_weapons_clean.csv
```

**What it does:**
1. Imports 240 regular perks → `perks` table
2. Imports 449 perk ranks → `perk_ranks` table
3. Imports 28 legendary perks → `legendary_perks` table
4. Imports 112 legendary perk ranks → `legendary_perk_ranks` table
5. Imports 262 weapons → `weapons` table
6. Parses perks from weapon data and populates `weapon_perks` junction table (1,685 links)
7. Parses legendary perks and populates `weapon_legendary_perk_effects` junction table

**Smart Perk Parsing:**
- Handles "Gunslinger (Expert, Master)" → Creates 3 links
- Strips conditions like "(scoped only)" for perk matching
- Validates all perks against canonical list
- Logs warnings for unmatched perks

### Armor Import Script (`import_armor.py`)

Imports unified armor data (regular + power armor).

```bash
# Run from project root
python database/import_armor.py
```

**What it does:**
1. Imports 477 armor pieces from `data/input/armor_unified.csv` → `armor` table
   - 291 regular armor pieces (18 sets × multiple levels × pieces)
   - 186 power armor pieces (12 sets × multiple levels × 6 pieces each)
2. Uses INSERT for initial import (no ON DUPLICATE KEY UPDATE needed - no unique name constraint)
3. Tracks and reports import counts by armor type

**Important:** Armor perks (Armorer, Fix It Good, White Knight, Lucky Break, Funky Duds, Sizzling Style) affect ALL armor equally, so no junction tables are needed for item-specific tracking.

## Development Notes

### Completed Features
- ✅ Complete database schema with unified armor architecture
- ✅ All 4 scrapers built and tested (weapon, armor, power armor, legendary perk)
- ✅ All data collected and imported:
  - 262 weapons fully scraped and imported
  - 477 armor pieces imported (291 regular + 186 power armor)
  - 240 regular perks with 449 ranks imported
  - 28 legendary perks with 112 ranks imported
- ✅ Weapon-perk relationships fully populated (1,685 links)
- ✅ RAG-optimized database views created
- ✅ Race support for Human/Ghoul perk differences
- ✅ Multi-rank support for both regular and legendary perks
- ✅ Normalized level tracking (one row per armor piece per level)
- ✅ Unified armor schema (regular + power armor merged)
- ✅ **RAG System MVP** - Functional natural language query interface with:
  - SQL generation from natural language
  - Conversational context memory
  - Strict database grounding (no hallucination)
  - MySQL compatibility layer
  - Error handling and empty result detection

### Technical Considerations
- All tables use InnoDB engine with proper foreign key constraints and cascading deletes
- The `rank` column in perk_ranks and legendary_perk_ranks requires backticks in MySQL 8.0
- Armor table uses ENUM for armor_type ('regular' or 'power')
- No UNIQUE constraint on armor.name - same piece can exist at multiple levels
- One row per armor piece per level for accurate stat tracking
- Armor perks are universal (no junction tables needed)
- Database credentials: username=root, password=secret (local dev environment)

### Known Gaps
- Vulcan Power Armor stats not yet available (awaiting wiki data for per-piece stats)
- `weapon_perk_rules` table schema exists but is unpopulated (conditional perk tracking)
- No mutations, consumables, legendary effects, or SPECIAL stat tracking yet

### Future Enhancements
See TODO.md for detailed future plans including:
- Phase 2: Additional build components (mutations, consumables, legendary effects, SPECIAL stats, status effects)
- Phase 3: Data enhancement (populate junction tables, conditional perk rules, damage formulas)
- Phase 4: RAG system & LLM integration (build optimizer, damage calculator, build comparison)

## Project Structure

```
fo76-ml-db/
├── docs/                  # All documentation
│   ├── README.md         # Detailed project documentation
│   ├── CLAUDE.md         # This file - Claude Code guidance
│   ├── TODO.md           # Roadmap and task tracking
│   ├── SCHEMA_DESIGN.md  # Database architecture
│   ├── SCRAPER_README.md # Scraper documentation
│   └── IMPORT_GUIDE.md   # Database import guide
├── data/                  # All data files
│   ├── input/            # Source CSV data (Perks, weapons, armor)
│   └── urls/             # URL lists for scrapers
├── database/              # Database schema and import scripts
├── scrapers/              # Web scraping scripts
├── tests/                 # Test and validation scripts
└── requirements.txt       # Python dependencies
```

## Documentation

For more details, see:
- **README.md** - Project overview and quick start
- **docs/TODO.md** - Project roadmap and task tracking
- **docs/RAG_IMPLEMENTATION_GUIDE.md** - Complete RAG system documentation
- **docs/SCHEMA_DESIGN.md** - Database architecture
- **docs/SCRAPER_README.md** - Scraper documentation
- **docs/IMPORT_GUIDE.md** - Database import guide
