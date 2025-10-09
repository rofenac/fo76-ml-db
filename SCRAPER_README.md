# Fallout 76 Wiki Scraper

A robust Python scraper for extracting weapon data from Fallout Wiki pages.

## Features

- ✅ Extracts complete weapon information (name, type, class, level, damage, projectile, Form ID, Editor ID)
- ✅ Intelligent perk extraction from infobox categories
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

### Scrape a single weapon:
```bash
python scraper.py -u "https://fallout.fandom.com/wiki/Laser_gun_(Fallout_76)" -o laser_gun.csv
```

### Scrape multiple weapons from a file:
```bash
python scraper.py -f urls.txt -o weapons_output.csv
```

### Use Playwright for JavaScript-heavy pages:
```bash
python scraper.py -f urls.txt -o weapons_output.csv --playwright
```

### Command-line options:
```
-u, --url         Single URL to scrape
-f, --file        File with URLs (one per line) - default: urls.txt
-o, --output      Output CSV file - default: weapons_scraped.csv
-p, --playwright  Use Playwright instead of requests
--perks           Path to canonical perks CSV - default: Perks.csv
```

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

## Future Enhancements

Potential improvements:
- [ ] Scrape weapon modifications
- [ ] Extract legendary effects
- [ ] Scrape armor data
- [ ] Add retry logic for failed requests
- [ ] Parallel scraping with rate limiting
- [ ] Export to JSON format option
- [ ] Database import script

## License

MIT License - See LICENSE file
