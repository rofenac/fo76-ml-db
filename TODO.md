# Project TODO List

## Current Tasks

### ✅ Completed
- [x] Create weapon scraper for regular weapons
- [x] Create database schema with weapon, perk, and legendary perk tables
- [x] Create import script for CSV → MySQL
- [x] Create legendary perk scraper
- [x] **Handle multi-rank legendary perks** - scraper now extracts all 4 ranks per perk
- [x] **Re-scrape legendary perks** - LegendaryPerks.csv now has 112 rows (28 perks × 4 ranks)
- [x] **Update import script for legendary perk ranks** - now populates `legendary_perk_ranks` table
- [x] **Add race column to perk tables** - Schema includes race for both perks and legendary_perks

### 🔄 In Progress

### 📋 Pending

#### ✅ RESOLVED: Ghoul vs Human Perk Tree Differences

**Solution Implemented:** Option A - Added race column to perk tables

**Final State:**
- ✅ `perks` table has `race` column (Human, Ghoul, Human, Ghoul)
- ✅ `legendary_perks` table has `race` column
- ✅ `LegendaryPerks.csv` includes race classification for all 28 perks
  - 26 universal perks: "Human, Ghoul"
  - 2 ghoul-specific: "Action Diet" and "Feral Rage" (race: "Ghoul")
- ✅ Import script handles race column for both regular and legendary perks
- ✅ Database schema fully supports race filtering

---

## Project Goal

**Build a RAG-powered LLM system** to help players:
1. **Optimize character builds** based on playstyle preferences
2. **Query game data** (weapon damage, perk effects, stat buffs, etc.)
3. **Answer questions** like "What's the best pistol build for stealth?"

## Future Enhancements

### Priority: Core Asset Tables & Perk Junctions

#### ✅ COMPLETED: Armor & Power Armor Schema
- [x] Create `armor` table (similar structure to `weapons`)
- [x] Create `power_armor` table
- [x] Create `armor_perks` junction table
- [x] Create `armor_legendary_perk_effects` junction table
- [x] Create `power_armor_perks` junction table
- [x] Create `power_armor_legendary_perk_effects` junction table
- [x] Create `perk_ranks` table for regular perks
- [x] Create `legendary_perk_ranks` table for legendary perks
- [x] Add race column to both perk tables
- [ ] Build armor scraper
- [ ] Build power armor scraper

#### ✅ COMPLETED: Perk Ranks Implementation
- [x] **Handle multi-rank regular perks** - Perks.csv has rank column, import script groups by perk name
- [x] **Handle multi-rank legendary perks** - Scraper extracts all 4 ranks with scaling values
  - Fixed scraper to parse repeating data groups from Wiki infoboxes
  - Added deduplication logic to handle duplicate sections
  - Extracts: rank number, description, effect_value, effect_type, form_id
  - Example: "Follow Through" has 10%/20%/30%/40% at ranks 1-4
- [x] **Update import script to populate perk_ranks table** - Regular perks populate `perk_ranks`
- [x] **Update import script for legendary perk ranks** - Legendary perks populate `legendary_perk_ranks`
- [x] **Re-scrape legendary perks** - LegendaryPerks.csv now has complete data (112 rows = 28 perks × 4 ranks)

### Later: Additional Asset Types
- [ ] Evaluate consumables/chems schema
- [ ] Evaluate mutations schema
- [ ] Evaluate player builds schema (save/load build configurations)

### Data Collection
- [ ] Scrape remaining 6 weapons (Laser gun, Pipe variants, Plasma gun, Ultracite laser)
- [x] **Re-scrape legendary perks to capture ALL ranks** - COMPLETED (28 perks, 112 total ranks)
- [ ] Scrape armor data
- [ ] Scrape power armor data
- [ ] Validate scraped data against game files
- [ ] Test database import with actual MySQL connection

### Database Features
- [ ] Implement `weapon_perk_rules` table for conditional perk application
  - Store conditions like "scoped only", "pistol configuration", "ADS only"
  - Link to specific weapon + perk combinations
- [ ] Add race column to perks (see issue #1 above)
- [ ] Create views for common RAG queries

### RAG System Preparation
- [ ] Create optimized views for LLM queries:
  - Best weapons by damage type
  - Perk synergies (perks that work well together)
  - Build archetypes (stealth sniper, heavy gunner, melee tank, etc.)
- [ ] Add full-text indexes for description searches
- [ ] Document query patterns for RAG retrieval
- [ ] Create example prompts for LLM

### Stretch Goals
- [ ] **Damage calculator** - Calculate effective DPS given build + weapon + perks
- [ ] Build simulator - Test builds before committing in-game
- [ ] Perk conflict detection (mutually exclusive perks)

### Data Quality
- [ ] Create validation script to check data integrity
- [ ] Add unit tests for scrapers
- [ ] Add unit tests for import logic
- [ ] Cross-reference with game data files

---

## Notes

### Current Data Status (Last Updated: 2025-10-09)

**Weapons:**
- 7 weapons scraped (only 1 with complete perk data: Enclave plasma gun)
- 6 weapons need perk data scraped

**Regular Perks:**
- 240 unique perk names
- 450 total rows in Perks.csv (with rank variants)
- Import script ready to populate `perks` and `perk_ranks` tables

**Legendary Perks:**
- ✅ **28 legendary perks fully scraped** (all data complete)
- ✅ **112 total ranks** in LegendaryPerks.csv (28 perks × 4 ranks each)
- ✅ **CSV format:** name, rank, description, effect_value, effect_type, form_id, race
- ✅ **Race breakdown:** 26 universal ("Human, Ghoul"), 2 ghoul-only ("Action Diet", "Feral Rage")
- ✅ Import script ready to populate `legendary_perks` and `legendary_perk_ranks` tables

**Database Schema:**
- Fully up to date and ready for import
- Includes: weapons, armor, power_armor tables
- Includes: perks, perk_ranks, legendary_perks, legendary_perk_ranks tables
- Includes: Junction tables for all asset-perk relationships
- Includes: RAG-optimized views for LLM queries

**Scripts:**
- `scraper.py` - Weapon scraper (working)
- `legendary_perk_scraper.py` - Legendary perk scraper (working, extracts all ranks)
- `import_to_db.py` - Database import script (ready, handles all rank data)
- `f76_schema.sql` - Database schema (complete)
