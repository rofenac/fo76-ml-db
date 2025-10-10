# Project TODO List

## Current Status (Last Updated: 2025-10-09)

### ✅ Phase 1: Core Data Collection - COMPLETE

**Weapons:**
- ✅ 249 weapons fully scraped and imported
- ✅ All weapon-perk relationships established (1,689 links)

**Armor:**
- ✅ 18 armor sets fully scraped and imported
- ⏳ Armor-perk junction tables ready but unpopulated

**Power Armor:**
- ✅ 72 power armor pieces fully scraped and imported (12 sets × 6 pieces each)
- ⏳ Power armor-perk junction tables ready but unpopulated

**Regular Perks:**
- ✅ 240 unique perks imported
- ✅ 449 total perk ranks imported
- ✅ Race classification complete (Human/Ghoul/Both)

**Legendary Perks:**
- ✅ 28 legendary perks fully scraped
- ✅ 112 total legendary perk ranks (28 × 4 ranks)
- ✅ Effect values and types parsed
- ✅ Race breakdown: 26 universal, 2 ghoul-only

**Database:**
- ✅ Full schema implemented with all tables
- ✅ RAG-optimized views created
- ✅ Junction tables for weapon-perk relationships populated
- ✅ Foreign key constraints and indexes in place

**Scrapers:**
- ✅ `scraper.py` - Weapon scraper (complete)
- ✅ `armor_scraper.py` - Armor scraper (complete)
- ✅ `power_armor_scraper.py` - Power armor scraper (complete)
- ✅ `legendary_perk_scraper.py` - Legendary perk scraper (complete)

---

## Phase 2: Additional Build Components

### 🔍 Research & Evaluation Phase

The following build components need to be researched, evaluated, and potentially added to the database schema:

#### 1. Mutations
- [ ] Research mutation mechanics in Fallout 76
- [ ] Identify all available mutations (e.g., Marsupial, Speed Demon, Bird Bones, Carnivore, Herbivore)
- [ ] Determine schema requirements:
  - Positive effects (e.g., +20 carry weight, +20% jump height)
  - Negative effects (e.g., -4 Intelligence)
  - Suppression mechanics (Class Freak perk, Starched Genes)
  - Compatibility with perks
- [ ] Create mutation scraper
- [ ] Create `mutations` table and related junction tables
- [ ] Import mutation data

#### 2. Consumables (Food, Chems, Drinks)
- [ ] Research consumable categories:
  - Food (cooked, raw, preserved)
  - Chems (buffout, psycho, med-x, etc.)
  - Drinks (nuka-cola variants, alcoholic beverages)
  - Aid items (stimpaks, radaway, rad-x)
- [ ] Identify stat buffs and durations
- [ ] Determine stacking rules and conflicts
- [ ] Consider perk interactions (e.g., Chem Fiend, Good With Salt, Party Boy/Girl)
- [ ] Create consumables scraper
- [ ] Create `consumables` table with effect tracking
- [ ] Import consumable data

#### 3. Legendary Effects/Mods
- [ ] Research legendary weapon effects (Bloodied, Anti-Armor, Two-Shot, Explosive, etc.)
- [ ] Research legendary armor effects (Unyielding, Vanguard's, Bolstering, etc.)
- [ ] Determine effect values and how they stack
- [ ] Research weapon mods (receivers, barrels, stocks, sights)
- [ ] Research armor mods (lining, padding, etc.)
- [ ] Create schema for legendary effects
- [ ] Create schema for mods
- [ ] Create scrapers for legendary effects and mods
- [ ] Import legendary effect and mod data

#### 4. SPECIAL Stats Tracking
- [ ] Research how SPECIAL stats are calculated:
  - Base stats (minimum 1, maximum 15 without legendary perks)
  - Perk card point allocation
  - Legendary perk bonuses (SPECIAL stat cards give +5 when maxed)
  - Gear/armor bonuses (Unyielding gives +3 to all SPECIAL except END when low health)
  - Mutation effects
  - Consumable buffs
- [ ] Determine schema for tracking stat modifiers
- [ ] Create tables for SPECIAL calculations
- [ ] Build stat calculation logic

#### 5. Status Effects/Buffs
- [ ] Research temporary status effects:
  - Environmental effects (well rested, well tuned)
  - Team buffs (Strange in Numbers for mutations)
  - Bobbleheads and magazines
  - Disease effects
  - Addiction effects
- [ ] Determine duration tracking
- [ ] Create schema for status effects
- [ ] Build effect application logic

#### 6. Additional Build Elements to Consider
- [ ] Evaluate adding **Legendary Perk loadouts** (players can swap between builds)
- [ ] Evaluate adding **Weapon/Armor legendary rolls** (specific combinations)
- [ ] Evaluate adding **Food/Chem crafting recipes** (for self-sufficiency builds)
- [ ] Evaluate adding **Bobbleheads and Magazines** (temporary buffs)
- [ ] Evaluate adding **Team synergies** (perks that benefit teams)
- [ ] Evaluate adding **Workshop and CAMP bonuses** (crafting benches, rest bonuses)

---

## Phase 3: Data Enhancement

### Junction Table Population
- [ ] Parse armor perks from `armor_scraped.csv` `Perks` column
- [ ] Populate `armor_perks` junction table
- [ ] Parse power armor perks from `power_armor_scraped.csv` `Perks` column
- [ ] Populate `power_armor_perks` junction table

### Conditional Perk Rules
- [ ] Implement `weapon_perk_rules` table population:
  - Parse conditional modifiers from weapon perk data
  - Store rules like "scoped only", "pistol configuration", "ADS only", "in VATS"
  - Link specific weapon-perk combinations with conditions
- [ ] Create similar tables for armor and power armor if needed

### Damage Formulas
- [ ] Research Fallout 76 damage calculation formulas
- [ ] Document how perks stack (additive vs multiplicative)
- [ ] Add damage formula metadata to database
- [ ] Create damage calculation functions/views

---

## Phase 4: RAG System & LLM Integration

### RAG-Optimized Views
- [ ] Enhance existing views with computed fields
- [ ] Create build archetype views:
  - Stealth commando builds
  - Heavy gunner builds
  - Bloodied builds
  - Shotgunner builds
  - Melee builds
  - VATS builds
  - Tank/support builds
- [ ] Create perk synergy views (perks that complement each other)

### Query Patterns
- [ ] Document common query patterns for RAG retrieval
- [ ] Add full-text indexes for description searches
- [ ] Create example prompts for LLM queries
- [ ] Build query optimization for fast retrieval

### Build Optimizer
- [ ] Create LLM-powered build recommendation system
- [ ] Input: Playstyle preferences, weapon choice, role (solo/team)
- [ ] Output: Recommended perks, mutations, gear, consumables
- [ ] Explain trade-offs and synergies

### Advanced Features
- [ ] **Damage calculator** - Calculate effective DPS given build + weapon + perks + buffs
- [ ] **Build simulator** - Test builds before committing in-game
- [ ] **Build comparison** - Compare two builds side-by-side
- [ ] **Perk conflict detection** - Identify mutually exclusive perks or inefficient combinations
- [ ] **Gear recommendation** - Suggest legendary effects based on build

---

## Data Quality & Testing

### Validation
- [ ] Create validation script to check data integrity
- [ ] Cross-reference with game data files (if accessible)
- [ ] Verify perk descriptions match in-game text
- [ ] Validate form IDs and editor IDs

### Testing
- [ ] Add unit tests for scrapers
- [ ] Add unit tests for import logic
- [ ] Add integration tests for database queries
- [ ] Test RAG retrieval accuracy

### Documentation
- [ ] Complete SCRAPER_README.md with armor/PA scraper docs
- [ ] Update CLAUDE.md with current architecture
- [ ] Document all database views and their use cases
- [ ] Create user guide for querying the database

---

## Completed Tasks Archive

### ✅ Core Schema & Import Scripts
- [x] Create weapon scraper for regular weapons
- [x] Create database schema with weapon, perk, and legendary perk tables
- [x] Create import script for CSV → MySQL
- [x] Create legendary perk scraper
- [x] Handle multi-rank legendary perks - scraper extracts all 4 ranks
- [x] Re-scrape legendary perks - LegendaryPerks.csv has 112 rows (28 × 4)
- [x] Update import script for legendary perk ranks
- [x] Add race column to perk tables (Human/Ghoul)
- [x] Create armor and power armor tables
- [x] Create all junction tables for perk relationships
- [x] Create RAG-optimized database views

### ✅ Armor & Power Armor
- [x] Build armor scraper
- [x] Build power armor scraper
- [x] Scrape all 18 armor sets
- [x] Scrape all 12 power armor sets (72 pieces total)
- [x] Import armor data to database
- [x] Import power armor data to database

### ✅ Weapon Data Collection
- [x] Gather 257 weapon URLs from Fallout Wiki
- [x] Scrape all 249 weapons
- [x] Import all weapons to database
- [x] Populate weapon_perks junction table (1,689 links)

---

## Project Goal

**Build a RAG-powered LLM system** to help Fallout 76 players:
1. **Optimize character builds** based on playstyle preferences
2. **Query game data** (weapon damage, perk effects, legendary effects, mutations, consumables, etc.)
3. **Answer complex questions** like:
   - "What's the best bloodied heavy gunner build for solo play?"
   - "Which mutations synergize with a VATS critical build?"
   - "What food should I use for a melee tank build?"
   - "How much damage does this weapon do with my current build?"

---

## Notes

### Current Database Summary
- **Weapons:** 249
- **Armor:** 18
- **Power Armor:** 72 (12 sets × 6 pieces)
- **Regular Perks:** 240 (449 total ranks)
- **Legendary Perks:** 28 (112 total ranks)
- **Weapon-Perk Links:** 1,689

### MySQL Reserved Keyword Fix
- Fixed `rank` column in `perk_ranks` and `legendary_perk_ranks` tables
- Used backticks: `` `rank` `` in both schema and import scripts
- Applied to CREATE TABLE statements and INSERT queries

### Next Immediate Steps
1. Evaluate and research mutation system
2. Evaluate and research consumable system
3. Evaluate legendary effects and mods
4. Consider SPECIAL stat tracking implementation
5. Plan status effects schema
