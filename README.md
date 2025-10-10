# Fallout 76 Database Project

A Python-based data collection and database management system for Fallout 76 game data. This project scrapes weapon and perk information from Fallout Wiki pages and stores it in a normalized MySQL database, designed to support a future RAG-powered LLM system for build optimization.

## Project Overview

**Goal:** Build a comprehensive database of Fallout 76 game data to power a RAG (Retrieval Augmented Generation) system that helps players:
- Optimize character builds based on playstyle preferences
- Query game data (weapon damage, perk effects, stat buffs, etc.)
- Answer questions like "What's the best pistol build for stealth?"

**Current Status:**
- ✅ Database schema complete (weapons, armor, power armor, perks, legendary perks)
- ✅ 240 regular perks with 449 total ranks imported
- ✅ 28 legendary perks with all ranks imported (112 total rank entries)
- ✅ 249 weapons fully scraped and imported
- ✅ 18 armor sets fully scraped and imported
- ✅ 72 power armor pieces fully scraped and imported (12 sets × 6 pieces each)
- ✅ 1,689 weapon-perk relationship links established
- ⏳ Junction tables for armor/power armor perks ready but unpopulated
- ⏳ Additional build components needed (mutations, consumables, legendary effects, etc.)

## Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repository_url>
cd fo76-ml-db

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JavaScript-heavy pages)
playwright install chromium
```

### 2. Create Database

```bash
# Create database and import schema
mysql -u <username> -p -e "CREATE DATABASE IF NOT EXISTS f76;"
mysql -u <username> -p f76 < f76_schema.sql
```

### 3. Import Data

```bash
# Option A: Using environment variables (recommended)
export MYSQL_USER=your_username
export MYSQL_PASS=your_password
python import_to_db.py

# Option B: Using command-line arguments
python import_to_db.py -u <username> -p <password>

# Option C: Custom database settings
python import_to_db.py \
  -u <username> \
  -p <password> \
  -H localhost \
  -d f76 \
  --perks-csv Perks.csv \
  --legendary-perks-csv LegendaryPerks.csv \
  --weapons-csv human_corrected_weapons_clean.csv
```

## Data Sources

### Input Files

- **`Perks.csv`** - 240 unique regular SPECIAL perks (449 rows with rank variants)
  - Columns: name, special, level, race, rank, description, form_id
- **`LegendaryPerks.csv`** - 28 legendary perks with all 4 ranks (112 rows)
  - Columns: name, rank, description, effect_value, effect_type, form_id, race
- **`human_corrected_weapons_clean.csv`** - 249 weapons fully imported
  - Columns: Name, Type, Class, Level, Damage, Projectile, Perks, Form ID, Editor ID, Source URL
- **`armor_scraped.csv`** - 18 armor sets fully scraped
  - Columns: Name, Type, Slot, Armor Rating, Energy Resistance, Radiation Resistance, Set Name, Level, Weight, Value, Form ID, Editor ID, Perks, Source URL
- **`power_armor_scraped.csv`** - 72 power armor pieces fully scraped
  - Columns: Name, Type, Set Name, Armor Rating, Energy Resistance, Radiation Resistance, Level, Weight, Value, Durability, Fusion Core Drain, Form ID, Editor ID, Perks, Source URL
- **`urls.txt`** - 257 Fallout Wiki weapon URLs (fully scraped)
- **`armor_urls.txt`** - 18 armor set URLs (fully scraped)
- **`power_armor_urls.txt`** - 12 power armor set URLs (fully scraped)

## Web Scraping

### Scrape Weapons ✅ COMPLETE

```bash
# Scrape all URLs in urls.txt
python scraper.py -f urls.txt -o weapons_scraped.csv

# Scrape a single weapon
python scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser.csv

# Use Playwright for JavaScript-heavy pages
python scraper.py -f urls.txt -o weapons.csv --playwright
```

**Status:** All 249 weapons scraped and imported.

### Scrape Armor ✅ COMPLETE

```bash
# Scrape all armor sets
python armor_scraper.py -f armor_urls.txt -o armor_scraped.csv

# Scrape a single armor set
python armor_scraper.py -u "https://fallout.fandom.com/wiki/Combat_armor_(Fallout_76)" -o output.csv

# Use Playwright (if needed)
python armor_scraper.py -f armor_urls.txt -o armor_scraped.csv --playwright
```

**Status:** All 18 armor sets scraped and imported.

### Scrape Power Armor ✅ COMPLETE

```bash
# Scrape all power armor sets
python power_armor_scraper.py -f power_armor_urls.txt -o power_armor_scraped.csv

# Scrape a single power armor set
python power_armor_scraper.py -u "https://fallout.fandom.com/wiki/T-45_power_armor_(Fallout_76)" -o output.csv

# Use Playwright (if needed)
python power_armor_scraper.py -f power_armor_urls.txt -o power_armor_scraped.csv --playwright
```

**Status:** All 72 power armor pieces scraped and imported (12 sets × 6 pieces each).

### Scrape Legendary Perks ✅ COMPLETE

```bash
# Scrape all legendary perks
python legendary_perk_scraper.py -f legendary_perk_urls.txt -o LegendaryPerks.csv

# Scrape a single legendary perk
python legendary_perk_scraper.py -u "https://fallout.fandom.com/wiki/Follow_Through" -o output.csv

# Use Playwright (if needed)
python legendary_perk_scraper.py -f legendary_perk_urls.txt -o output.csv --playwright
```

**Legendary Perk Scraper Features:**
- ✅ Extracts all 4 ranks per perk (not just one)
- ✅ Parses effect values and types (percentage, flat, value)
- ✅ Handles race classification (Human, Ghoul, or Both)
- ✅ Extracts Form IDs for each rank
- ✅ Deduplicates data from Wiki page sections
- ✅ Validates rank completeness (all perks should have 4 ranks)

**Status:** All 28 legendary perks scraped and imported with all ranks.

## Database Architecture

### Core Tables

- **`weapons`** - Weapon data (damage, projectile, form_id, etc.)
- **`armor`** - Regular armor pieces
- **`power_armor`** - Power armor frames and pieces
- **`perks`** - Regular SPECIAL perks (240 unique)
- **`perk_ranks`** - Rank-specific effects for regular perks (450 rows)
- **`legendary_perks`** - Legendary character perks (28 unique)
- **`legendary_perk_ranks`** - Rank-specific effects for legendary perks (112 rows)

### Junction Tables

- **`weapon_perks`** - Links weapons to regular perks that affect them
- **`weapon_legendary_perk_effects`** - Links weapons to legendary perks
- **`armor_perks`** / **`armor_legendary_perk_effects`** - Similar for armor
- **`power_armor_perks`** / **`power_armor_legendary_perk_effects`** - Similar for power armor

### RAG-Optimized Views

- **`v_weapons_with_perks`** - Weapons with all affecting perks (regular + legendary)
- **`v_armor_with_perks`** - Armor with all affecting perks
- **`v_power_armor_with_perks`** - Power armor with all affecting perks
- **`v_perks_all_ranks`** - Regular perks with rank breakdowns
- **`v_legendary_perks_all_ranks`** - Legendary perks with rank breakdowns

## Import Script Features

### What the Import Does

1. **Imports regular perks** from `Perks.csv`:
   - 240 unique perks → `perks` table
   - 450 perk ranks → `perk_ranks` table (grouped by perk name)
   - Handles race column (Human/Ghoul/Both)

2. **Imports legendary perks** from `LegendaryPerks.csv`:
   - 28 unique legendary perks → `legendary_perks` table
   - 112 legendary perk ranks → `legendary_perk_ranks` table
   - Parses effect values (10%, 20%, 30%, 40%) and types
   - Handles ghoul-specific perks: "Action Diet", "Feral Rage"

3. **Imports weapons** and links them to perks

### Smart Perk Parsing

The import script handles complex perk formats:
- ✓ `"Bloody Mess"` → Creates 1 link
- ✓ `"Gunslinger (Expert, Master)"` → Creates 3 links: Gunslinger, Gunslinger Expert, Gunslinger Master
- ✓ `"Sniper (scoped) only"` → Extracts "Sniper" (strips conditions)
- ✓ `"Pistol: Gun Runner, Modern Renegade"` → Parses class-specific perks
- ✓ Validates all perks against canonical perk lists

## Example Output

```
============================================================
DATABASE IMPORT COMPLETE
============================================================
Armor imported this session:        18
Power armor imported this session:  72
------------------------------------------------------------
TOTAL DATABASE RECORDS:
  Weapons:         249
  Armor:           18
  Power Armor:     72
  Perks:           240
  Legendary Perks: 28
============================================================

Full Database Summary:
- Regular perks: 240 (449 total ranks)
- Legendary perks: 28 (112 total ranks)
- Weapons: 249
- Armor: 18
- Power Armor: 72 (12 sets × 6 pieces)
- Weapon-perk links: 1,689
```

## Project Structure

```
fo76-ml-db/
├── f76_schema.sql                    # Database schema (complete)
├── import_to_db.py                   # Main import script (weapons + perks)
├── import_armor.py                   # Armor/power armor import script
├── scraper.py                        # Weapon scraper
├── armor_scraper.py                  # Armor scraper
├── power_armor_scraper.py            # Power armor scraper
├── legendary_perk_scraper.py         # Legendary perk scraper (with rank support)
├── Perks.csv                         # 240 perks, 449 ranks
├── LegendaryPerks.csv                # 28 legendary perks, 112 ranks
├── human_corrected_weapons_clean.csv # 249 weapons (imported)
├── armor_scraped.csv                 # 18 armor sets (imported)
├── power_armor_scraped.csv           # 72 power armor pieces (imported)
├── urls.txt                          # 257 weapon Wiki URLs (complete)
├── armor_urls.txt                    # 18 armor Wiki URLs (complete)
├── power_armor_urls.txt              # 12 power armor Wiki URLs (complete)
├── legendary_perk_urls.txt           # 28 legendary perk Wiki URLs (complete)
├── IMPORT_GUIDE.md                   # Detailed import instructions
├── SCHEMA_DESIGN.md                  # Database design documentation
├── SCRAPER_README.md                 # Web scraper documentation
├── TODO.md                           # Project roadmap and status
└── CLAUDE.md                         # AI assistant guidance
```

## Key Features

### Race Support (Human vs Ghoul)
- Database tracks race-specific perks
- 2 ghoul-exclusive legendary perks: "Action Diet", "Feral Rage"
- Most perks are universal (both races)

### Multi-Rank Perk Support
- Regular perks: Ranks 1-5 (varying by perk)
- Legendary perks: Always 4 ranks with scaling effects
- Example: "Follow Through" - 10%/20%/30%/40% damage increase

### Effect Parsing
- Automatically extracts numeric values from descriptions
- Categorizes effect types: percentage, flat, value
- Enables future damage calculators and build simulators

## Documentation

- **[IMPORT_GUIDE.md](IMPORT_GUIDE.md)** - Complete import process walkthrough
- **[SCHEMA_DESIGN.md](SCHEMA_DESIGN.md)** - Database architecture and RAG design
- **[TODO.md](TODO.md)** - Project status, roadmap, and next steps
- **[CLAUDE.md](CLAUDE.md)** - Project context for AI assistants

## Development

### Dependencies

```
beautifulsoup4  # HTML parsing
lxml            # XML/HTML parser
playwright      # Browser automation
pandas          # Data manipulation
mysql-connector-python  # MySQL connectivity
requests        # HTTP requests
```

### Testing

```bash
# Validate scraped weapon data
python validate_scraped_data.py weapons_scraped.csv

# Test import logic without database
python test_import_legendary_perks.py
```

## Future Plans

### Phase 1: Additional Build Components (Not Yet Started)
- [ ] **Mutations** - Scraped and stored in database (e.g., Marsupial, Speed Demon, Bird Bones)
- [ ] **Consumables** - Food, chems, drinks with stat buffs
- [ ] **Legendary Effects/Mods** - Weapon and armor legendary modifications
- [ ] **SPECIAL Stats** - Base stats and how they're modified by perks/gear
- [ ] **Status Effects/Buffs** - Temporary effects from consumables, mutations, environment

### Phase 2: Data Enhancement
- [ ] Populate armor_perks and power_armor_perks junction tables
- [ ] Implement weapon_perk_rules table (conditional perks: scoped, ADS, VATS, etc.)
- [ ] Add damage formulas and calculation support

### Phase 3: RAG System & Optimization
- [ ] Build RAG-powered LLM query interface
- [ ] Create build optimizer based on playstyle inputs
- [ ] Add damage calculator with full perk/buff stacking
- [ ] Build comparison and recommendation engine

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## License

MIT License

## Acknowledgments

- Data sourced from [Fallout Wiki](https://fallout.fandom.com/)
- Built for the Fallout 76 community
