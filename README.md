# Fallout 76 RAG Database Project

A Python-based data collection and database management system for Fallout 76 game data, designed to power a RAG (Retrieval Augmented Generation) system for build optimization.

## Project Structure

```
fo76-ml-db/
├── docs/                  # All documentation
│   ├── README.md         # Detailed project documentation
│   ├── CLAUDE.md         # Claude Code guidance
│   ├── TODO.md           # Roadmap and task tracking
│   ├── SCHEMA_DESIGN.md  # Database architecture
│   ├── SCRAPER_README.md # Scraper documentation
│   └── IMPORT_GUIDE.md   # Database import guide
├── data/                  # All data files
│   ├── input/            # Source CSV data
│   │   ├── Perks.csv
│   │   ├── LegendaryPerks.csv
│   │   ├── human_corrected_weapons_clean.csv
│   │   └── armor_unified.csv
│   └── urls/             # URL lists for scrapers
│       ├── urls.txt
│       ├── armor_urls.txt
│       ├── power_armor_urls.txt
│       └── legendary_perk_urls.txt
├── database/              # Database schema and import scripts
│   ├── f76_schema.sql
│   ├── import_to_db.py
│   └── import_armor.py
├── scrapers/              # Web scraping scripts
│   ├── scraper.py
│   ├── armor_scraper.py
│   ├── power_armor_scraper.py
│   └── legendary_perk_scraper.py
├── tests/                 # Test and validation scripts
│   ├── validate_scraped_data.py
│   └── test_perk_parsing.py
└── requirements.txt       # Python dependencies
```

## Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for JavaScript-heavy pages)
playwright install chromium
```

### 2. Database Setup

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS f76;"

# Import schema
mysql -u root -p f76 < database/f76_schema.sql
```

### 3. Import Data

```bash
# From project root directory
python database/import_to_db.py -u root -p <password>
python database/import_armor.py
```

## Current Status

**Phase 1 Complete:** Core data collection finished

- ✅ 249 weapons fully scraped and imported
- ✅ 477 armor pieces fully imported (291 regular + 186 power armor)
- ✅ 240 regular perks with 449 total ranks imported
- ✅ 28 legendary perks with 112 total ranks imported
- ✅ 1,689 weapon-perk relationship links established

## Usage Examples

### Running Scrapers

```bash
# Weapon scraper
python scrapers/scraper.py -f data/urls/urls.txt -o weapons_output.csv

# Armor scraper
python scrapers/armor_scraper.py -f data/urls/armor_urls.txt -o armor_output.csv

# Power armor scraper
python scrapers/power_armor_scraper.py -f data/urls/power_armor_urls.txt -o pa_output.csv

# Legendary perk scraper
python scrapers/legendary_perk_scraper.py -f data/urls/legendary_perk_urls.txt -o legendary_output.csv
```

### Validating Data

```bash
# Validate scraped weapon data
python tests/validate_scraped_data.py weapons_output.csv
```

## Documentation

For detailed information, see the `docs/` directory:

- **docs/README.md** - Full project overview and documentation
- **docs/CLAUDE.md** - AI assistant guidance (for Claude Code)
- **docs/TODO.md** - Roadmap and future enhancements
- **docs/SCHEMA_DESIGN.md** - Database architecture details
- **docs/SCRAPER_README.md** - Comprehensive scraper documentation
- **docs/IMPORT_GUIDE.md** - Step-by-step database import guide

## Database Credentials (Local Dev)

- **Host:** localhost
- **User:** root
- **Password:** secret
- **Database:** f76

## License

This project is for educational and personal use. Game data is sourced from the [Fallout Wiki](https://fallout.fandom.com/).
