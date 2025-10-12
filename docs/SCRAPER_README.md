# Fallout 76 Wiki Scrapers

A comprehensive set of Python scrapers for extracting game data from Fallout Wiki pages.

## Overview

This project includes scrapers for:
- **Weapons** (`scraper.py`) - 249 weapons scraped ✅
- **Armor** (`armor_scraper.py`) - 18 armor sets scraped ✅
- **Power Armor** (`power_armor_scraper.py`) - 72 power armor pieces scraped ✅
- **Legendary Perks** (`legendary_perk_scraper.py`) - 28 legendary perks with all ranks scraped ✅

## Common Features

All scrapers share these features:
- ✅ Extracts complete data from Wiki infoboxes
- ✅ Intelligent perk extraction from categorized sections
- ✅ Handles conditional perks (e.g., "scoped only", "pistol only", "sighted")
- ✅ Validates perks against canonical list (Perks.csv)
- ✅ Handles Expert/Master perk variants
- ✅ Error handling and logging
- ✅ Supports both requests (fast) and Playwright (JavaScript-heavy pages)

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

For Playwright support (optional):
```bash
playwright install
```

## Usage

### Weapon Scraper (`scraper.py`) ✅ COMPLETE

**Scrape a single weapon:**
```bash
python scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser_gun.csv
```

**Scrape all weapons from file:**
```bash
python scraper.py -f urls.txt -o weapons_scraped.csv
```

**Command-line options:**
```
-u, --url         Single URL to scrape
-f, --file        File with URLs (one per line) - default: urls.txt
-o, --output      Output CSV file - default: weapons_scraped.csv
-p, --playwright  Use Playwright instead of requests
--perks           Path to canonical perks CSV - default: Perks.csv
```

**Status:** All 249 weapons scraped and imported to database.

---

### Armor Scraper (`armor_scraper.py`) ✅ COMPLETE

**Scrape a single armor set:**
```bash
python armor_scraper.py -u "https://fallout.fandom.com/wiki/Combat_armor_(Fallout_76)" -o output.csv
```

**Scrape all armor sets from file:**
```bash
python armor_scraper.py -f armor_urls.txt -o armor_scraped.csv
```

**Command-line options:**
```
-u, --url         Single URL to scrape
-f, --file        File with URLs - default: armor_urls.txt
-o, --output      Output CSV file - default: armor_scraped.csv
-p, --playwright  Use Playwright instead of requests
--perks           Path to canonical perks CSV - default: Perks.csv
```

**Status:** All 18 armor sets scraped and imported to database.

---

### Power Armor Scraper (`power_armor_scraper.py`) ✅ COMPLETE

**Scrape a single power armor set:**
```bash
python power_armor_scraper.py -u "https://fallout.fandom.com/wiki/T-45_power_armor_(Fallout_76)" -o output.csv
```

**Scrape all power armor sets from file:**
```bash
python power_armor_scraper.py -f power_armor_urls.txt -o power_armor_scraped.csv
```

**Command-line options:**
```
-u, --url         Single URL to scrape
-f, --file        File with URLs - default: power_armor_urls.txt
-o, --output      Output CSV file - default: power_armor_scraped.csv
-p, --playwright  Use Playwright instead of requests
--perks           Path to canonical perks CSV - default: Perks.csv
```

**Status:** All 72 power armor pieces scraped and imported (12 sets × 6 pieces each).

---

### Legendary Perk Scraper (`legendary_perk_scraper.py`) ✅ COMPLETE

**Scrape a single legendary perk:**
```bash
python legendary_perk_scraper.py -u "https://fallout.fandom.com/wiki/Follow_Through" -o output.csv
```

**Scrape all legendary perks from file:**
```bash
python legendary_perk_scraper.py -f legendary_perk_urls.txt -o LegendaryPerks.csv
```

**Command-line options:**
```
-u, --url         Single URL to scrape
-f, --file        File with URLs - default: legendary_perk_urls.txt
-o, --output      Output CSV file - default: LegendaryPerks.csv
-p, --playwright  Use Playwright instead of requests
```

**Status:** All 28 legendary perks scraped with all ranks (112 total rank entries).

## Input Format

### URLs File (`urls.txt`)
One URL per line. Lines starting with `#` are ignored (comments).

Example:
```
https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)
https://fallout.fandom.com/wiki/Plasma_gun_(Fallout_76)
# https://fallout.fandom.com/wiki/Disabled_weapon
```

## Output Format

### Weapon Scraper Output
CSV with the following columns:
- **Name**: Weapon name
- **Type**: Weapon type (e.g., "Ranged")
- **Class**: Weapon class (e.g., "Pistol/Rifle")
- **Level**: Level requirements (e.g., "25 / 35 / 45")
- **Damage**: Damage values
- **Projectile**: Projectile type from game engine
- **Perks**: Semicolon-separated list of perks with conditions
- **Form ID**: Game Form ID (8-digit hex)
- **Editor ID**: Game Editor ID
- **Source URL**: Wiki page URL

### Armor Scraper Output
CSV with the following columns:
- **Name**: Armor piece name
- **Type**: Armor type (e.g., "Light", "Sturdy", "Heavy", "Outfit")
- **Slot**: Armor slot (e.g., "Chest", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Helmet")
- **Armor Rating**: Physical damage resistance
- **Energy Resistance**: Energy damage resistance
- **Radiation Resistance**: Radiation resistance
- **Set Name**: Armor set name (for matching set bonuses)
- **Level**: Level requirements
- **Weight**: Item weight
- **Value**: Item value (caps)
- **Form ID**: Game Form ID (8-digit hex)
- **Editor ID**: Game Editor ID
- **Perks**: Semicolon-separated list of affecting perks
- **Source URL**: Wiki page URL

### Power Armor Scraper Output
CSV with the following columns:
- **Name**: Power armor piece name
- **Type**: Piece type (e.g., "Frame", "Torso", "Helmet", "Left Arm", "Right Arm", "Left Leg", "Right Leg")
- **Set Name**: Power armor set (e.g., "T-45", "T-51b", "T-60", "X-01", "Ultracite")
- **Armor Rating**: Physical damage resistance
- **Energy Resistance**: Energy damage resistance
- **Radiation Resistance**: Radiation resistance
- **Level**: Level requirements
- **Weight**: Item weight
- **Value**: Item value (caps)
- **Durability**: Item durability/HP
- **Fusion Core Drain**: AP drain rate (for frames)
- **Form ID**: Game Form ID (8-digit hex)
- **Editor ID**: Game Editor ID
- **Perks**: Semicolon-separated list of affecting perks
- **Source URL**: Wiki page URL

### Legendary Perk Scraper Output
CSV with the following columns:
- **name**: Legendary perk name
- **rank**: Perk rank (1-4)
- **description**: Rank-specific description
- **effect_value**: Parsed numeric value (e.g., "10" from "10% damage")
- **effect_type**: Effect type (percentage, flat, value)
- **form_id**: Game Form ID (8-digit hex)
- **race**: Race classification (Human, Ghoul, or "Human, Ghoul")

## Perk Extraction

The scraper extracts perks from the weapon infobox, organized by category:

### Perk Categories
- **Damage**: Perks that increase damage (e.g., Bloody Mess, Gunslinger, Guerrilla)
- **Legendary**: Legendary perks (e.g., Follow Through, Far-Flung Fireworks)
- **Sneak**: Stealth perks (e.g., Covert Operative)
- **Penetration**: Armor penetration perks (e.g., Tank Killer)
- **Weight**: Weight reduction perks (e.g., Packin' Light, Arms Keeper)
- **Other**: Miscellaneous perks (e.g., Gunsmith, Quick Hands, Sniper)

### Conditional Perks
The scraper captures conditions for perks:

- `"scoped only"` - Perk only applies when using a scope
- `"sighted only"` - Perk only applies when aiming down sights
- `"pistol only"` - Perk only applies in pistol configuration
- `"rifle only"` - Perk only applies in rifle configuration
- `"suppressor only"` - Perk only applies with suppressor equipped

### Example Output Format
```
Bloody Mess; Covert Operative; Tank Killer; Gunsmith; Quick Hands; Pistol: Gun Runner; pistol only: Packin' Light; rifle only: Arms Keeper; scoped only: Sniper
```

## Validation

The scraper validates extracted perks against `Perks.csv` (240 canonical perks). Invalid perks are automatically filtered out.

## Error Handling

- Failed page fetches are logged and skipped
- Invalid HTML structure is handled gracefully
- Missing infobox data results in empty fields (not errors)
- All errors are logged with timestamps for debugging

## Logging

The scraper logs to stdout with the following levels:
- **INFO**: Progress updates (scraping, successful extractions)
- **WARNING**: Missing data (no infobox, no perks found)
- **ERROR**: Failures (fetch errors, parsing errors)

## Architecture

### Key Components

1. **`WeaponData` dataclass**: Structured data container matching CSV format
2. **`FalloutWikiScraper` class**: Main scraper with:
   - `scrape_weapon()`: Scrape single URL
   - `scrape_urls_from_file()`: Batch scraping
   - `_extract_infobox()`: Extract weapon stats from infobox
   - `_extract_perks_from_infobox()`: Extract perks by category
   - `_extract_perk_condition()`: Parse conditional perk modifiers
   - `_is_valid_perk()`: Validate against canonical list

### Workflow

```
URL → Fetch HTML → Parse with BeautifulSoup → Extract Infobox →
→ Extract Stats → Extract Perks by Category → Parse Conditions →
→ Validate Perks → Format Output → Save to CSV
```

## Tips

### For best results:
1. **Start small**: Test on 1-2 URLs before running large batches
2. **Check logs**: Watch for warnings about missing data
3. **Validate output**: Compare scraped data with wiki pages for accuracy
4. **Use Playwright sparingly**: Only needed for JavaScript-heavy pages (slower)
5. **Update Perks.csv**: Keep canonical perk list updated as game updates

### Common Issues:

**No perks found**: Page structure may differ - check logs for warnings

**Missing data**: Some weapons have incomplete wiki pages

**Slow scraping**: Use requests (default) instead of Playwright when possible

## Scraper Architecture

### Common Components

All scrapers share similar architecture:

1. **Data Classes**: Structured data containers (`WeaponData`, `ArmorData`, `PowerArmorData`, `LegendaryPerkData`)
2. **Scraper Classes**: Main scraping logic with modular methods
3. **HTML Fetching**: Support for both requests (fast) and Playwright (JavaScript-heavy pages)
4. **Infobox Parsing**: Extract structured data from Wiki infoboxes
5. **Perk Extraction**: Intelligent perk parsing with validation
6. **CSV Export**: Write to CSV with proper formatting

### Workflow
```
URL → Fetch HTML → Parse with BeautifulSoup → Extract Infobox →
→ Extract Stats → Extract Perks → Parse Conditions →
→ Validate Against Canonical List → Format Output → Save to CSV
```

## Future Enhancements

### Potential Improvements
- [ ] Scrape weapon modifications (receivers, barrels, stocks, sights)
- [ ] Extract legendary weapon/armor effects
- [ ] Scrape mutations
- [ ] Scrape consumables (food, chems, drinks)
- [ ] Add retry logic for failed requests
- [ ] Parallel scraping with rate limiting
- [ ] Export to JSON format option
- [ ] Real-time progress bars

### Completed Enhancements
- [x] Weapon scraper - 249 weapons scraped
- [x] Armor scraper - 18 armor sets scraped
- [x] Power armor scraper - 72 power armor pieces scraped
- [x] Legendary perk scraper - 28 legendary perks with all ranks scraped
- [x] Database import scripts for all data types

## License

MIT License - See LICENSE file
