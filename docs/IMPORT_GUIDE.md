# Fallout 76 Database Import Guide

## Understanding the Data Model

### Character Perks (follow the character, affect weapons)

1. **Regular SPECIAL Perks** (`perks` table)
   - From `Perks.csv` (450 perks, 240 unique names with ranks)
   - Examples: Gunslinger, Tank Killer, Bloody Mess, Covert Operative
   - Stored in: `perks` table

2. **Legendary Perks** (`legendary_perks` table)
   - From `LegendaryPerks.csv`
   - Examples: Follow Through, Far-Flung Fireworks
   - Stored in: `legendary_perks` table

### Weapon-Perk Relationships

- **`weapon_perks`** junction table: Links weapons → regular perks that can affect them
- **`weapon_legendary_perk_effects`** junction table: Links weapons → legendary perks that can affect them

### NOT Tracked Here

- **Weapon Mods** (scopes, barrels, stocks) - these are physical modifications that follow the weapon itself, not character perks

---

## Step-by-Step Import Process

### 1. Create Database & Schema

```bash
# Create the database
mysql -u <username> -p -e "CREATE DATABASE IF NOT EXISTS f76;"

# Import schema (includes legendary_perks table)
mysql -u <username> -p f76 < f76_schema.sql
```

### 2. Verify Legendary Perks Data

The `LegendaryPerks.csv` file is already populated with complete rank data:

```csv
name,rank,description,effect_value,effect_type,form_id,race
Follow Through,1,Ranged sneak damage increases damage to target by 10% for 10 seconds.,10,percentage,005A5D69,"Human, Ghoul"
Follow Through,2,Ranged sneak damage increases damage to target by 20% for 10 seconds.,20,percentage,005A5D6A,"Human, Ghoul"
...
```

**CSV Structure:**
- Each perk has 4 ranks (1 row per rank)
- Total: 28 perks = 112 CSV rows
- Includes parsed effect values and types for damage calculations

### 3. Run the Import Script

```bash
# Using environment variables (recommended)
export MYSQL_USER=your_username
export MYSQL_PASS=your_password
python import_to_db.py
```

Or with command-line arguments:

```bash
python import_to_db.py -u <username> -p <password>
```

---

## What the Import Does

1. **Imports regular perks** from `Perks.csv`:
   - 240 unique perks → `perks` table
   - 450 perk ranks → `perk_ranks` table (grouped by perk name)
   - Includes: special, level, race, rank-specific descriptions

2. **Imports legendary perks** from `LegendaryPerks.csv`:
   - 28 unique legendary perks → `legendary_perks` table
   - 112 legendary perk ranks → `legendary_perk_ranks` table (grouped by perk name)
   - Includes: race, rank-specific descriptions, effect_value, effect_type
   - Handles ghoul-specific perks: "Action Diet", "Feral Rage"

3. **Imports weapons** from `human_corrected_weapons_clean.csv` → `weapons` table

4. **Parses perk references** from weapon data:
   - Handles complex formats: `"Gunslinger (Expert, Master)"` → creates 3 links
   - Auto-corrects typos: `"Guerilla"` → `"Guerrilla"`
   - Strips conditions: `"Sniper (scoped) only"` → extracts `"Sniper"`
   - Handles class-specific: `"Pistol: Gun Runner, Modern Renegade"`

5. **Links weapons to perks**:
   - Regular perks → `weapon_perks` table
   - Legendary perks → `weapon_legendary_perk_effects` table

6. **Warns about missing perks** not found in either table

---

## Expected Output

```
============================================================
FALLOUT 76 DATABASE IMPORT
============================================================

=== Importing Perks from Perks.csv ===
Found 240 unique perks with 450 total ranks
✓ Inserted 240 perks
✓ Inserted 450 perk ranks
✓ Cached 240 regular perk IDs

=== Importing Legendary Perks from LegendaryPerks.csv ===
Found 28 unique legendary perks with 112 total ranks
✓ Inserted 28 legendary perks
✓ Inserted 112 legendary perk ranks
✓ Cached 28 legendary perk IDs

=== Importing Weapons from human_corrected_weapons_clean.csv ===
✓ Inserted 7 new weapons
✓ Created 22 weapon-perk links

============================================================
IMPORT COMPLETE
============================================================
Total regular perks imported: 240
Total legendary perks imported: 28
Total weapons imported: 7

=== Database Summary ===
Weapons in database: 7
Regular perks in database: 240 (450 total ranks)
Legendary perks in database: 28 (112 total ranks)
Weapon → regular perk links: 20
Weapon → legendary perk effects: 2

Weapons with no perks (regular or legendary): 6
  - Laser gun
  - Pipe bolt-action
  - Pipe gun
  - Pipe revolver
  - Plasma gun
  - Ultracite laser gun
```

---

## Current Data Status

**Regular Perks:**
- ✅ 240 unique perks fully loaded (Perks.csv)
- ✅ 450 total perk ranks ready for import
- ✅ Import script handles race column and rank grouping

**Legendary Perks:**
- ✅ 28 legendary perks fully scraped with all rank data
- ✅ 112 total legendary perk ranks (28 perks × 4 ranks)
- ✅ Includes effect parsing (effect_value, effect_type)
- ✅ Race classification: 26 universal, 2 ghoul-specific

**Weapons:**
- Enclave plasma gun: Complete perk data (20 regular perks, 2 legendary perks)
- 6 weapons need perk data scraped: Laser gun, Pipe variants, Plasma gun, Ultracite laser

**Next Steps:**
1. Test import with MySQL database connection
2. Scrape remaining 6 weapons' perk data
3. Consider scraping armor and power armor data

---

## Database Schema Overview

```
weapons
├── weapon_perks ────→ perks (regular SPECIAL perks)
└── weapon_legendary_perk_effects ────→ legendary_perks (legendary character perks)
```

**Future expansion:** `weapon_perk_rules` table for conditional logic (e.g., "only when scoped", "pistol configuration only")
