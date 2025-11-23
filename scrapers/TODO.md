# Weapon Mod Scraping TODO

## Next Session: Full Weapon Mod Scrape

### 1. Apply Schema Changes
```bash
cd /home/rofenac/github/fo76-ml-db
mysql -u $DB_USER -p f76 < database/f76_master_schema.sql
```

### 2. Run Full Scrape
```bash
cd scrapers
source ../.venv/bin/activate
python weapon_mod_scraper.py --no-playwright -o weapon_mods_scraped.csv
```
- ~70 weapons in `weapon_mod_urls.txt`
- ~1 second per weapon (rate limiting)
- Estimated time: ~2 minutes

### 3. Import to Database
```bash
cd ../database
python import_weapon_mods.py -f ../scrapers/weapon_mods_scraped.csv
```

### 4. Verify Data
```sql
SELECT COUNT(*) FROM weapon_mods;
SELECT * FROM v_weapon_mods_complete LIMIT 20;
```

## Files Created This Session
- `scrapers/weapon_mod_urls.txt` - Curated list of 70+ weapon URLs
- `scrapers/weapon_mod_scraper.py` - Extracts mod tables from wiki pages
- `database/import_weapon_mods.py` - Imports CSV to MySQL
- `database/f76_master_schema.sql` - Updated with:
  - `weapon_mod_slots` table
  - `weapon_mods` table  
  - `weapon_mod_crafting` table
  - `v_weapon_mods_complete` view

## Notes
- Use `--no-playwright` flag for faster scraping (HTTP requests work fine)
- Scraper extracts: damage, fire rate, range, accuracy, AP cost, weight, value, perk requirements
- Boolean flags: converts_to_auto, converts_to_semi, is_suppressed, is_scoped
- Appearance/cosmetic mods are automatically skipped
