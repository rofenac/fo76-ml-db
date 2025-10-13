# Database Schema Design for Fallout 76 RAG System

## Design Philosophy

This schema is optimized for **RAG (Retrieval Augmented Generation)** queries where an LLM needs to:
1. Find relevant game data based on natural language queries
2. Reason about perk synergies and build optimization
3. Calculate effective stats (damage, resistances, etc.)
4. Answer specific questions about game mechanics

## Core Principles

### 1. **Parallel Structure Across Asset Types**
Weapons, armor, and power armor use similar table structures:
- Common fields: name, type, form_id, editor_id, source_url, perks_raw
- Asset-specific fields as needed
- Consistent junction table patterns for perk relationships

**Why:** Makes LLM queries predictable and allows pattern reuse

### 2. **Junction Tables for Many-to-Many**
Every asset type has TWO junction tables:
- `{asset}_perks` - Links to regular SPECIAL perks
- `{asset}_legendary_perk_effects` - Links to legendary perks

**Why:**
- Perks can affect multiple assets (e.g., "Arms Keeper" affects all weapons)
- Assets can be affected by multiple perks
- Separates legendary from regular for clearer querying

### 3. **Raw + Normalized Dual Storage**
- `perks_raw` TEXT field stores scraped perk text
- Junction tables normalize relationships
- Both are preserved for different use cases

**Why:**
- Raw text helps LLM understand context and conditions
- Normalized junctions enable SQL aggregations and filtering
- Can validate normalization against raw data

### 4. **RAG-Optimized Views**
Pre-built views aggregate common query patterns:
- `v_weapons_with_perks` - Weapons with all affecting perks
- `v_armor_with_perks` - Armor with all affecting perks
- `v_legendary_perks_all_ranks` - Legendary perks with rank breakdowns

**Why:**
- Faster retrieval for RAG system
- Reduces complexity of LLM-generated queries
- Single source of truth for common questions

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                        CHARACTER PERKS                          │
│  ┌──────────────┐              ┌──────────────────────┐         │
│  │    perks     │              │  legendary_perks     │         │
│  │  (240 base)  │              │      (28 base)       │         │
│  └──────┬───────┘              └──────────┬───────────┘         │
│         │                                  │                     │
│         │                      ┌───────────┴──────────┐          │
│         │                      │ legendary_perk_ranks │          │
│         │                      │  (rank-specific)     │          │
│         │                      └──────────────────────┘          │
└─────────┼──────────────────────────────┼──────────────────────┘
          │                               │
          │    ┌──────────────────────────┼─────────────┐
          │    │                          │             │
          ▼    ▼                          ▼             ▼
    ┌─────────────┐              ┌─────────────┐ ┌─────────────┐
    │   weapons   │              │    armor    │ │power_armor  │
    └─────┬───────┘              └──────┬──────┘ └──────┬──────┘
          │                             │               │
          ├─weapon_perks                ├─armor_perks   ├─power_armor_perks
          │                             │               │
          └─weapon_legendary_           └─armor_        └─power_armor_
            perk_effects                  legendary_      legendary_
                                         perk_effects    perk_effects
```

## Table Descriptions

### Assets (Items)

#### `weapons`
Ranged and melee weapons (guns, swords, etc.)
- **Key fields:** damage, class (pistol/rifle/heavy), type (ranged/melee/thrown)
- **Use case:** "What's the best stealth pistol?" → Filter by class, join perks

#### `armor`
Regular armor pieces (leather, combat, scout, etc.)
- **Key fields:** slot, set_name, armor_rating, resistances
- **Use case:** "Show me heavy armor with high DR" → Filter by type, rating

#### `power_armor`
Power armor frames and pieces (T-45, T-60, X-01, etc.)
- **Key fields:** set_name, durability, fusion_core_drain
- **Use case:** "What's the best power armor for tanking?" → Join legendary perks

### Character Perks

#### `perks`
Regular SPECIAL perks (240 unique names, 450 with ranks)
- **Key fields:** name
- **TODO:** Add race column (Human/Ghoul/Both)

#### `legendary_perks`
Legendary character perks (28 total)
- **Key fields:** name, description
- **Note:** 2 are ghoul-specific (Action Diet, Feral Rage)

#### `legendary_perk_ranks`
Rank-specific effects for legendary perks
- **Key fields:** rank, description, effect_value, effect_type
- **Use case:** "What's Far-Flung Fireworks at rank 4?" → Filter by perk + rank

### Junction Tables (Relationships)

Pattern: `{asset}_{perk_type}`

All follow this structure:
```sql
PRIMARY KEY (asset_id, perk_id)
FOREIGN KEY asset_id → {asset}(id)
FOREIGN KEY perk_id → {perk_table}(id)
```

## Future Expansions

### Planned Tables

#### `consumables`
Chems, food, drinks, magazines, bobbleheads
- Aid items that provide temporary buffs
- Important for build calculations

#### `mutations`
Genetic mutations (Marsupial, Speed Demon, etc.)
- Permanent effects with trade-offs
- Interact with Starched Genes perk

#### `player_builds`
Saved build configurations
- SPECIAL allocation
- Equipped perks (regular + legendary)
- Equipped gear (weapon + armor)
- Active mutations
- Use case: Save/load builds, simulate effectiveness

### Conditional Perk Rules

#### `weapon_perk_rules` (partially implemented)
Stores conditions for when perks apply:
- "Sniper perk: scoped only"
- "Guerrilla: pistol configuration only"
- "Ground Pounder: hip fire only"

**Fields:**
- weapon_class ENUM
- fire_mode ENUM
- scope_state ENUM
- aim_state ENUM (ADS vs hip)
- vats_state ENUM

## Database Views (RAG-Optimized Queries)

### What Are Views?

Database views are **pre-built, reusable SELECT statements** that combine data from multiple tables. They appear as tables but don't store data - they execute the underlying query when accessed.

**Naming Convention:** All views use the `v_` prefix to distinguish them from actual data tables.

### The 4 RAG-Optimized Views

#### 1. `v_weapons_with_perks`
**Purpose:** Complete weapon information with all affecting perks in a single query

**Data Provided:**
- Weapon details: id, name, type, class, level, damage, source_url
- All regular perks (semicolon-separated): "Arms Keeper; Bloody Mess; Gunslinger..."
- All legendary perks (semicolon-separated): "Follow Through; Far-Flung Fireworks"

**Query:**
```sql
SELECT * FROM v_weapons_with_perks WHERE weapon_name = 'Enclave plasma gun';
```

**Use Cases:**
- "What perks affect the Enclave plasma gun?"
- "Show me all heavy guns and their perks"
- "Which weapons benefit from Gunslinger?"

#### 2. `v_armor_complete`
**Purpose:** Unified view of all armor (regular + power armor) with resistances

**Data Provided:**
- Armor details: id, name, armor_type, class, slot, set_name, level
- All resistances: DR, ER, RR, Cryo, Fire, Poison
- Source URL

**Query:**
```sql
SELECT * FROM v_armor_complete
WHERE armor_type = 'regular' AND class = 'Heavy';
```

**Use Cases:**
- "Show me all heavy armor sets"
- "What's the DR of T-65 power armor chest?"
- "Compare Scout armor vs Combat armor resistances"

#### 3. `v_perks_all_ranks`
**Purpose:** Regular SPECIAL perks with all rank details

**Data Provided:**
- Perk base info: perk_id, name, SPECIAL, min_level, race
- Rank details: rank number (1-5), description, form_id
- All ranks for each perk in separate rows

**Query:**
```sql
SELECT * FROM v_perks_all_ranks
WHERE perk_name = 'Gunslinger' AND rank = 3;
```

**Use Cases:**
- "What does Gunslinger Master do?"
- "Show me all Strength perks at rank 1"
- "What's the difference between rank 1 and rank 3 of Bloody Mess?"

#### 4. `v_legendary_perks_all_ranks`
**Purpose:** Legendary perks with rank progression (1-4)

**Data Provided:**
- Legendary perk info: legendary_perk_id, name, base_description, race
- Rank details: rank (1-4), rank_description, effect_value, effect_type
- Scaling values parsed: "10%", "20%", "30%", "40%"

**Query:**
```sql
SELECT * FROM v_legendary_perks_all_ranks
WHERE perk_name = 'Follow Through'
ORDER BY rank;
```

**Use Cases:**
- "How does Follow Through scale from rank 1 to 4?"
- "Which legendary perks are ghoul-only?"
- "Show me all rank 4 legendary perk effects"

### Why Views Are Essential for RAG

**❌ Without Views:**
```sql
-- Complex 5-table join the LLM would need to generate
SELECT w.name, w.damage,
       GROUP_CONCAT(DISTINCT p.name) as regular_perks,
       GROUP_CONCAT(DISTINCT lp.name) as legendary_perks
FROM weapons w
LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
LEFT JOIN perks p ON wp.perk_id = p.id
LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
LEFT JOIN legendary_perks lp ON wlpe.legendary_perk_id = lp.id
WHERE w.name = 'Enclave plasma gun'
GROUP BY w.id;
```

**✅ With Views:**
```sql
-- Simple, readable query
SELECT * FROM v_weapons_with_perks
WHERE weapon_name = 'Enclave plasma gun';
```

### Benefits

1. **Simpler Queries** - LLM doesn't need to know table relationships or JOIN syntax
2. **Faster Retrieval** - Pre-optimized joins, MySQL caches execution plans
3. **Consistent Format** - Always returns data in the same structure
4. **Single Source of Truth** - One canonical way to query common patterns
5. **Reduced Errors** - No risk of incorrect joins or missing foreign keys
6. **Better Performance** - Database can optimize view queries better than dynamic SQL

### View Maintenance

Views are automatically updated when underlying tables change:
- Add weapon → Immediately appears in `v_weapons_with_perks`
- Link new perk → View reflects change instantly
- No manual refresh needed

**Schema Updates:** If table structure changes, views must be recreated:
```sql
DROP VIEW v_weapons_with_perks;
CREATE VIEW v_weapons_with_perks AS ...
```

This is handled automatically when importing `f76_schema.sql`.

## RAG Query Examples

### Example 1: Build Optimization
**User:** "Best stealth sniper build for a human?"

**RAG retrieval:**
1. Query `v_weapons_with_perks` WHERE weapon_class LIKE '%Rifle%'
2. Query `v_perks_all_ranks` WHERE perk_name LIKE '%sneak%' OR perk_name LIKE '%sniper%'
3. Query `v_legendary_perks_all_ranks` WHERE base_description LIKE '%sneak%'
4. Filter by race = 'Human' or 'Human, Ghoul'

**LLM response:** Synthesize weapon recommendations + perk loadout

### Example 2: Stat Lookup
**User:** "What's the base damage of the Enclave plasma gun?"

**RAG retrieval:**
1. Query `v_weapons_with_perks` WHERE weapon_name = 'Enclave plasma gun'
2. Return damage field

**LLM response:** Parse multi-level damage "24 / 28 / 32"

### Example 3: Perk Effect
**User:** "What does Follow Through do at rank 3?"

**RAG retrieval:**
1. Query `v_legendary_perks_all_ranks` WHERE perk_name = 'Follow Through' AND rank = 3

**LLM response:** Explain rank 3 effect

### Example 4: Weapon-Perk Relationships
**User:** "Which weapons are affected by Gunslinger?"

**RAG retrieval:**
1. Query `v_weapons_with_perks` WHERE regular_perks LIKE '%Gunslinger%'
2. Return list of weapons

**LLM response:** List weapons with their classes (Non-automatic pistol, Pistol/Rifle, etc.)

## Performance Considerations

### Indexes
- Primary keys on all tables (auto)
- Unique constraints on names
- Indexes on commonly filtered fields:
  - weapon.class, armor.slot, power_armor.set_name
  - armor.set_name (for matching set queries)
  - Form IDs (for game file cross-reference)

### Views
- Pre-aggregated for common joins
- Avoid computing on every query
- Trade storage for query speed (RAG prioritizes retrieval speed)

## Schema Evolution Notes

**Current status (2025-10-09):**
- ✅ Weapons table fully implemented
- ✅ Armor and Power Armor tables in schema (not yet populated)
- ✅ Regular perks fully implemented (240 perks, 450 ranks)
- ✅ Legendary perks fully implemented (28 perks, 112 ranks)
- ✅ Perk rank tables for both regular and legendary perks
- ✅ Race column for ghoul/human differentiation
- ✅ All junction tables for asset-perk relationships
- ✅ RAG-optimized views

**Next:**
- Populate weapons table (257 URLs ready to scrape)
- Build armor and power armor scrapers
- Test full database import

**Later:**
- Consumables, Mutations, Builds tables
- Implement weapon_perk_rules for conditional logic

**Migration strategy:** Additive only (no breaking changes to existing tables)
