# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Great Fallout 76 DB Project is a Python-based data collection and database management system for Fallout 76 game data. The project scrapes weapon and perk information from Fallout Wiki pages and stores it in a normalized MySQL database.

## Environment Setup

This project uses Python with a virtual environment:

```bash
# Create and activate virtual environment (if needed)
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

Key dependencies:
- `beautifulsoup4` and `lxml` - HTML parsing from wiki pages
- `playwright` - Browser automation for dynamic content
- `pandas` - Data manipulation and CSV processing
- `mysql-connector-python` - MySQL database connectivity
- `requests` - HTTP requests for web scraping

## Database Architecture

The project uses a MySQL database (`f76`) with a normalized schema defined in `f76_schema.sql`:

### Core Tables

1. **weapons** - Primary table storing weapon data
   - Contains: name, type, projectile, form_id, editor_id, perks_raw, source_url
   - Unique constraint on weapon name

2. **perks** - Canonical perk names table
   - Simple lookup table for all available perks
   - Unique constraint on perk name

3. **weapon_perks** - Many-to-many relationship
   - Links weapons to perks they can use
   - Composite primary key (weapon_id, perk_id)

4. **weapon_perk_rules** - Detailed perk application rules (optional)
   - Stores conditions: weapon_class, fire_mode, scope_state, aim_state, vats_state
   - For tracking context-specific perk applications (e.g., "only when scoped", "only in ADS")

### Database Setup

```bash
# Create database and tables
mysql -u <username> -p < f76_schema.sql

# Or connect and run manually:
mysql -u <username> -p
source f76_schema.sql;
```

## Data Files

### Input Data

- **urls.txt** - List of Fallout Wiki URLs to scrape for weapon data
- **Perks.csv** - Complete perk catalog with columns:
  - name, special, level, race, rank, description, form_id

### Processed Data

- **human_corrected_weapons_clean.csv** - Cleaned weapon data ready for import
  - Columns: Name, Type, Class, Level, Damage, Projectile, Perks, Form ID, Editor ID, Source URL
  - Contains parsed perk information from wiki pages

## Data Processing Workflow

The typical workflow for this project:

1. **Scraping** - Extract weapon data from Fallout Wiki URLs
   - Use playwright/beautifulsoup4 to parse wiki pages
   - Handle dynamic content and tables

2. **Cleaning** - Process and normalize scraped data
   - Parse comma-separated perks from wiki format
   - Validate against canonical perk list (Perks.csv)
   - Handle special cases (e.g., "Expert", "Master" variants)

3. **Import** - Load data into MySQL database
   - Insert weapons into `weapons` table
   - Parse `perks_raw` field to populate `weapon_perks` junction table
   - Cross-reference with `perks` table

## Key Data Patterns

### Perk Parsing

Perks in the raw data use complex notation:
- "Bloody Mess" - Simple perk
- "Gunslinger (Expert, Master)" - Multiple ranks
- "Sniper (scoped) only" - Conditional application
- "Pistol: Gun Runner, Modern Renegade, Crack Shot (sighted only)" - Class-specific with conditions

When processing perks:
- Split on semicolons and commas
- Handle parenthetical qualifiers separately
- Map variations to canonical perk names from Perks.csv
- Store conditions in `weapon_perk_rules` if detailed tracking is needed

### Weapon Classification

Weapons have multiple classification attributes:
- **Type** - "Ranged", "Melee", etc.
- **Class** - "Pistol/Rifle", "Heavy", etc. (note: some weapons can be multiple classes)
- **Projectile** - Game engine projectile type (e.g., "ProjectilePlasmaLarge")

## Web Scraping

### Running the Scraper

The `scraper.py` script extracts weapon data from Fallout Wiki pages:

```bash
# Scrape all URLs in urls.txt
python scraper.py -f urls.txt -o weapons_scraped.csv

# Scrape a single weapon
python scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser.csv

# Use Playwright for JavaScript-heavy pages
python scraper.py -f urls.txt -o weapons.csv --playwright
```

The scraper:
- Extracts weapon stats from infobox (Form ID, Editor ID, levels, damage, etc.)
- Intelligently parses perks from categorized sections (Damage, Legendary, Sneak, etc.)
- Handles conditional perks ("scoped only", "pistol only", "sighted", etc.)
- Validates perks against canonical list in Perks.csv
- Handles Expert/Master perk variants automatically

### Data Validation

Validate scraped data before importing to database:

```bash
python validate_scraped_data.py weapons_scraped.csv
```

This checks:
- Required fields are present (Name, Form ID, Editor ID, Source URL)
- Form IDs are valid 8-digit hex values
- Perks match canonical list
- Data completeness (flags missing Type, Level, etc.)

## Development Notes

- The project currently contains sample data for 7 weapons (mostly energy weapons: Enclave plasma gun, Laser gun, Pipe variants)
- The scraper successfully extracts complete data including perks with conditional modifiers
- The database schema supports future expansion with the `weapon_perk_rules` table for complex conditional logic
- All tables use InnoDB engine with proper foreign key constraints and cascading deletes
- See `SCRAPER_README.md` for detailed scraper documentation
