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
- **Key fields:** damage, projectile, class (pistol/rifle/heavy)
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

## RAG Query Examples

### Example 1: Build Optimization
**User:** "Best stealth sniper build for a human?"

**RAG retrieval:**
1. Query `v_weapons_with_perks` WHERE weapon_class = 'Rifle'
2. Query `perks` WHERE name LIKE '%sneak%' OR name LIKE '%sniper%'
3. Query `legendary_perks` WHERE description LIKE '%sneak%'
4. Filter by race = 'Human' or 'Both'

**LLM response:** Synthesize weapon recommendations + perk loadout

### Example 2: Stat Lookup
**User:** "What's the base damage of the Enclave plasma gun?"

**RAG retrieval:**
1. Query `weapons` WHERE name = 'Enclave plasma gun'
2. Return damage field

**LLM response:** Parse multi-level damage "24 / 28 / 32"

### Example 3: Perk Effect
**User:** "What does Follow Through do at rank 3?"

**RAG retrieval:**
1. Query `v_legendary_perks_all_ranks` WHERE name = 'Follow Through' AND rank = 3

**LLM response:** Explain rank 3 effect

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
