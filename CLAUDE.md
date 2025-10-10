# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Great Fallout 76 DB Project is a Python-based data collection and database management system for Fallout 76 game data. The project scrapes comprehensive game data (weapons, armor, power armor, perks, legendary perks) from Fallout Wiki pages and stores it in a normalized MySQL database designed to power a RAG (Retrieval Augmented Generation) system for build optimization.

**Project Goal:** Build a RAG-powered LLM system to help players optimize character builds, query game data, and answer complex questions like "What's the best bloodied heavy gunner build for solo play?"

## Current Status (Last Updated: 2025-10-09)

### ✅ Phase 1 Complete: Core Data Collection

**Database Population:**
- 249 weapons fully scraped and imported
- 18 armor sets fully scraped and imported
- 72 power armor pieces fully scraped and imported (12 sets × 6 pieces each)
- 240 regular perks with 449 total ranks imported
- 28 legendary perks with 112 total ranks imported (all 4 ranks per perk)
- 1,689 weapon-perk relationship links established

**Scrapers Complete:**
- `scraper.py` - Weapon scraper ✅
- `armor_scraper.py` - Armor scraper ✅
- `power_armor_scraper.py` - Power armor scraper ✅
- `legendary_perk_scraper.py` - Legendary perk scraper ✅

### 🔄 Next Phase: Additional Build Components

Research and evaluate adding:
- **Mutations** (e.g., Marsupial, Speed Demon, Bird Bones)
- **Consumables** (food, chems, drinks with stat buffs)
- **Legendary Effects/Mods** (weapon and armor legendary modifications)
- **SPECIAL Stats Tracking** (how stats are calculated and modified)
- **Status Effects/Buffs** (temporary effects from consumables, mutations, environment)

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

1. **weapons** - Weapon data table (249 rows)
   - Contains: name, type, class, level, damage, projectile, form_id, editor_id, perks_raw, source_url
   - Unique constraint on weapon name
   - Indexed on: form_id, type, class

2. **armor** - Armor data table (18 rows)
   - Contains: name, type, slot, armor_rating, energy_resistance, radiation_resistance, set_name, level, weight, value, form_id, editor_id, perks_raw, source_url
   - Unique constraint on armor name
   - Indexed on: set_name, slot, type

3. **power_armor** - Power armor data table (72 rows)
   - Contains: name, type, set_name, armor_rating, energy_resistance, radiation_resistance, level, weight, value, durability, fusion_core_drain, form_id, editor_id, perks_raw, source_url
   - Unique constraint on power armor name
   - Indexed on: set_name, type

4. **perks** - Regular SPECIAL perks base table (240 rows)
   - Contains: name, special, level, race
   - Unique constraint on perk name
   - Indexed on: special, race

5. **perk_ranks** - Regular perk ranks (449 rows)
   - Contains: perk_id, `rank`, description, form_id
   - Foreign key to perks(id) with CASCADE delete
   - **Important:** `rank` is a MySQL reserved keyword - must use backticks in queries

6. **legendary_perks** - Legendary perks base table (28 rows)
   - Contains: name, description, race
   - Unique constraint on perk name
   - Indexed on: race

7. **legendary_perk_ranks** - Legendary perk ranks (112 rows = 28 perks × 4 ranks)
   - Contains: legendary_perk_id, `rank`, description, effect_value, effect_type
   - Foreign key to legendary_perks(id) with CASCADE delete
   - **Important:** `rank` is a MySQL reserved keyword - must use backticks

### Junction Tables (Many-to-Many Relationships)

8. **weapon_perks** - Links weapons to regular perks (1,689 rows)
   - Primary key: (weapon_id, perk_id)
   - Foreign keys with CASCADE delete

9. **weapon_legendary_perk_effects** - Links weapons to legendary perks
   - Primary key: (weapon_id, legendary_perk_id)
   - Foreign keys with CASCADE delete

10. **armor_perks** - Links armor to regular perks (ready, unpopulated)
    - Primary key: (armor_id, perk_id)
    - Foreign keys with CASCADE delete

11. **armor_legendary_perk_effects** - Links armor to legendary perks (ready, unpopulated)
    - Primary key: (armor_id, legendary_perk_id)
    - Foreign keys with CASCADE delete

12. **power_armor_perks** - Links power armor to regular perks (ready, unpopulated)
    - Primary key: (power_armor_id, perk_id)
    - Foreign keys with CASCADE delete

13. **power_armor_legendary_perk_effects** - Links power armor to legendary perks (ready, unpopulated)
    - Primary key: (power_armor_id, legendary_perk_id)
    - Foreign keys with CASCADE delete

### Future Tables

14. **weapon_perk_rules** - Conditional perk application rules (schema ready, unpopulated)
    - Stores conditions: weapon_class, fire_mode, scope_state, aim_state, vats_state
    - For tracking context-specific perk applications (e.g., "only when scoped", "only in ADS")

### RAG-Optimized Views

The schema includes views for efficient LLM queries:

- **v_weapons_with_perks** - Weapons with all affecting perks (regular + legendary)
- **v_armor_with_perks** - Armor with all affecting perks
- **v_power_armor_with_perks** - Power armor with all affecting perks
- **v_perks_all_ranks** - Regular perks with rank breakdowns
- **v_legendary_perks_all_ranks** - Legendary perks with rank breakdowns

### Database Setup

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"

# Import schema (drops all tables first, then recreates)
mysql -u root -p f76 < f76_schema.sql

# Import data
python import_to_db.py -u root -p <password>
python import_armor.py
```

**Important MySQL 8.0 Note:** The `rank` column is a reserved keyword. All queries must use backticks: `` `rank` ``

## Data Files

### Input Data

- **urls.txt** - 257 Fallout Wiki weapon URLs (all scraped) ✅
- **armor_urls.txt** - 18 armor set URLs (all scraped) ✅
- **power_armor_urls.txt** - 12 power armor set URLs (all scraped) ✅
- **legendary_perk_urls.txt** - 28 legendary perk URLs (all scraped) ✅
- **Perks.csv** - 240 regular SPECIAL perks with 449 ranks
  - Columns: name, special, level, race, rank, description, form_id
- **LegendaryPerks.csv** - 28 legendary perks with 112 total ranks (28 × 4)
  - Columns: name, rank, description, effect_value, effect_type, form_id, race

### Scraped/Processed Data

- **human_corrected_weapons_clean.csv** - 249 weapons (all imported) ✅
  - Columns: Name, Type, Class, Level, Damage, Projectile, Perks, Form ID, Editor ID, Source URL
- **armor_scraped.csv** - 18 armor sets (all imported) ✅
  - Columns: Name, Type, Slot, Armor Rating, Energy Resistance, Radiation Resistance, Set Name, Level, Weight, Value, Form ID, Editor ID, Perks, Source URL
- **power_armor_scraped.csv** - 72 power armor pieces (all imported) ✅
  - Columns: Name, Type, Set Name, Armor Rating, Energy Resistance, Radiation Resistance, Level, Weight, Value, Durability, Fusion Core Drain, Form ID, Editor ID, Perks, Source URL

## Data Processing Workflow

The typical workflow for this project:

1. **Scraping** - Extract data from Fallout Wiki URLs
   - Use `scraper.py`, `armor_scraper.py`, `power_armor_scraper.py`, `legendary_perk_scraper.py`
   - Playwright/BeautifulSoup4 to parse wiki pages
   - Handle dynamic content and infobox tables

2. **Validation** (Optional)
   - Validate against canonical perk list (Perks.csv)
   - Check form IDs, editor IDs, required fields

3. **Import** - Load data into MySQL database
   - `import_to_db.py` - Imports weapons, perks, legendary perks, and populates weapon_perks junction table
   - `import_armor.py` - Imports armor and power armor

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
- **Type** - "Ranged", "Melee", "Thrown", etc.
- **Class** - "Pistol/Rifle", "Heavy", "Shotgun", etc. (some weapons can be multiple classes)
- **Projectile** - Game engine projectile type (e.g., "ProjectilePlasmaLarge", "ProjectileBallisticRifle")

### Armor Classification

Armor has the following classification:
- **Type** - "Light", "Sturdy", "Heavy", "Outfit", etc.
- **Slot** - "Chest", "Helmet", "Left Arm", "Right Arm", "Left Leg", "Right Leg"
- **Set Name** - For matching set bonuses

### Power Armor Classification

Power armor has the following classification:
- **Type** - "Helmet", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg"
- **Set Name** - "T-45", "T-51b", "T-60", "X-01", "Ultracite", "T-65", "Hellcat", "Strangler heart", "Union", "Vulcan", "Excavator", "Raider"

### Race Support

The database tracks race-specific perks:
- **Regular perks:** Most are universal ("Human, Ghoul")
- **Legendary perks:** 26 universal, 2 ghoul-only ("Action Diet", "Feral Rage")

## Web Scraping

### Running the Scrapers

All scrapers follow the same command-line pattern:

```bash
# Weapon scraper (COMPLETE - 249 weapons)
python scraper.py -f urls.txt -o weapons_scraped.csv
python scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser.csv

# Armor scraper (COMPLETE - 18 armor sets)
python armor_scraper.py -f armor_urls.txt -o armor_scraped.csv
python armor_scraper.py -u "https://fallout.fandom.com/wiki/Combat_armor_(Fallout_76)" -o output.csv

# Power armor scraper (COMPLETE - 72 power armor pieces)
python power_armor_scraper.py -f power_armor_urls.txt -o power_armor_scraped.csv
python power_armor_scraper.py -u "https://fallout.fandom.com/wiki/T-45_power_armor_(Fallout_76)" -o output.csv

# Legendary perk scraper (COMPLETE - 28 legendary perks, 112 ranks)
python legendary_perk_scraper.py -f legendary_perk_urls.txt -o LegendaryPerks.csv
python legendary_perk_scraper.py -u "https://fallout.fandom.com/wiki/Follow_Through" -o output.csv

# Use Playwright for JavaScript-heavy pages (add --playwright flag)
python scraper.py -f urls.txt -o weapons.csv --playwright
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
python validate_scraped_data.py weapons_scraped.csv
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
# Using command-line arguments
python import_to_db.py -u root -p secret

# Using environment variables
export MYSQL_USER=root
export MYSQL_PASS=secret
python import_to_db.py

# Custom files/settings
python import_to_db.py \
  -u root -p secret \
  -H localhost -d f76 \
  --perks-csv Perks.csv \
  --legendary-perks-csv LegendaryPerks.csv \
  --weapons-csv human_corrected_weapons_clean.csv
```

**What it does:**
1. Imports 240 regular perks → `perks` table
2. Imports 449 perk ranks → `perk_ranks` table
3. Imports 28 legendary perks → `legendary_perks` table
4. Imports 112 legendary perk ranks → `legendary_perk_ranks` table
5. Imports 249 weapons → `weapons` table
6. Parses perks from weapon data and populates `weapon_perks` junction table (1,689 links)
7. Parses legendary perks and populates `weapon_legendary_perk_effects` junction table

**Smart Perk Parsing:**
- Handles "Gunslinger (Expert, Master)" → Creates 3 links
- Strips conditions like "(scoped only)" for perk matching
- Validates all perks against canonical list
- Logs warnings for unmatched perks

### Armor Import Script (`import_armor.py`)

Imports armor and power armor data.

```bash
python import_armor.py
```

**What it does:**
1. Imports 18 armor pieces → `armor` table
2. Imports 72 power armor pieces → `power_armor` table
3. Uses INSERT...ON DUPLICATE KEY UPDATE for safe re-imports

**Note:** Armor and power armor perk junction tables are currently unpopulated. Future enhancement will parse perks from CSV and populate `armor_perks`, `armor_legendary_perk_effects`, `power_armor_perks`, and `power_armor_legendary_perk_effects`.

## Development Notes

### Completed Features
- ✅ Complete database schema with all core tables
- ✅ All 4 scrapers built and tested
- ✅ All data scraped and imported (weapons, armor, power armor, perks, legendary perks)
- ✅ Weapon-perk relationships fully populated (1,689 links)
- ✅ RAG-optimized database views created
- ✅ Race support for Human/Ghoul perk differences
- ✅ Multi-rank support for both regular and legendary perks

### Technical Considerations
- All tables use InnoDB engine with proper foreign key constraints and cascading deletes
- The `rank` column in perk_ranks and legendary_perk_ranks requires backticks in MySQL 8.0
- Power armor creates 6 pieces per set (Helmet, Torso, Left/Right Arms, Left/Right Legs)
- The scraper successfully extracts complete data including perks with conditional modifiers
- Database credentials: username=root, password=secret (local dev environment)

### Known Gaps
- Armor/power armor perk junction tables are unpopulated
- `weapon_perk_rules` table schema exists but is unpopulated (conditional perk tracking)
- No mutations, consumables, legendary effects, or SPECIAL stat tracking yet

### Future Enhancements
See TODO.md for detailed future plans including:
- Phase 2: Additional build components (mutations, consumables, legendary effects, SPECIAL stats, status effects)
- Phase 3: Data enhancement (populate junction tables, conditional perk rules, damage formulas)
- Phase 4: RAG system & LLM integration (build optimizer, damage calculator, build comparison)

## Documentation

For more details, see:
- **README.md** - Project overview and quick start
- **TODO.md** - Detailed roadmap and task tracking
- **SCRAPER_README.md** - Comprehensive scraper documentation
- **IMPORT_GUIDE.md** - Database import walkthrough
- **SCHEMA_DESIGN.md** - Database architecture and RAG design
