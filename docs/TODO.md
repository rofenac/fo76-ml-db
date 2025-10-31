# Project TODO List

## Current Status (2025-10-30)

### Database
- **Weapons:** 262 (with special mechanics: charge, spin-up, chain lightning, explosive AOE)
- **Armor:** 477 unified (291 regular + 186 power armor, one row per piece per level)
- **Perks:** 240 regular (449 ranks), 28 legendary (112 ranks)
- **Mutations:** 19
- **Consumables:** 11 (build-relevant buffs)
- **Weapon-Perk Links:** 1,711
- **Total Items:** 1,037
- **Vector Embeddings:** 1,517 (OpenAI text-embedding-3-small, 1536-dim)

### Completed Phases
- ✅ **Phase 1:** Core data collection (weapons, armor, perks, legendary perks)
- ✅ **Phase 2:** RAG system with hybrid SQL + Vector search
- ✅ **Phase 3:** Mutations and consumables
- ✅ **Phase 4:** ChromaDB vector database with 1,517 embeddings
- ✅ **Weapon Mechanics:** Charge, spin-up, chain lightning, explosive AOE system

### Notable Features
- Normalized MySQL schema with views optimized for RAG
- Hybrid query engine with intelligent SQL/Vector routing
- Interactive CLI (`./python-start.sh` or `python rag/cli.py`)
- Conversation history (3-message context)
- Hallucination prevention via strict database grounding
- Race support (Human/Ghoul-specific perks)
- Multi-rank system (1-5 regular, 4 legendary)

---

## Active Development

### Phase 5: Data Enhancement

#### Weapon Mechanics System ✅ COMPLETE
- ✅ Flexible mechanic types table (charge, spin-up, chain lightning, explosive AOE, etc.)
- ✅ Many-to-many relationship with attributes (numeric_value, numeric_value_2, string_value, unit, notes)
- ✅ Gauss weapons: 50% uncharged → 100% charged (rifle, shotgun, pistol)
- ✅ Spin-up weapons: Minigun, Gauss minigun, Gatling guns, Pepper Shaker (7 total)
- ✅ Tesla rifle: Chain lightning (65% → 42.25% per hop)
- ✅ View: `v_weapons_with_mechanics`
- ✅ Documentation: `docs/WEAPON_MECHANICS.md`
- ✅ Test queries: `database/test_weapon_mechanics.sql`

#### Conditional Perk Rules ⏳ PLANNED
- [ ] Populate `weapon_perk_rules` table with conditions
- [ ] Parse conditional modifiers (scoped only, ADS only, in VATS, etc.)
- [ ] Link weapon-perk combinations with rules

#### Damage Formulas ⏳ PLANNED
- [ ] Research FO76 damage calculation formulas
- [ ] Document perk stacking (additive vs multiplicative)
- [ ] Create damage calculation views/functions

---

## Future Phases

### Phase 6: Additional Build Components

**Collectibles (Bobbleheads & Magazines):**
- [ ] Schema: collectible_types, collectible_series, collectibles tables
- [ ] Scraper + import scripts
- [ ] Temporary buff tracking

**Legendary Effects/Mods:**
- [ ] Weapon legendary effects (Bloodied, Anti-Armor, Two-Shot, Explosive)
- [ ] Armor legendary effects (Unyielding, Vanguard's, Bolstering)
- [ ] Weapon/armor mods (receivers, barrels, stocks, linings)
- [ ] Effect stacking research

**SPECIAL Stats Tracking:**
- [ ] Base stats + perk allocations
- [ ] Legendary perk bonuses (+5 when maxed)
- [ ] Gear bonuses (Unyielding +3 SPECIAL)
- [ ] Mutation/consumable modifiers

---

## Phase 7: Advanced RAG Features

**Build Archetypes:**
- [ ] Views for common builds (bloodied, stealth commando, heavy gunner, VATS, tank)
- [ ] Perk synergy analysis

**Build Tools:**
- [ ] Damage calculator (weapon + perks + buffs → DPS)
- [ ] Build simulator
- [ ] Build comparison (side-by-side)
- [ ] Perk conflict detection
- [ ] Gear recommendation engine

---

## Phase 8: Web GUI (Stretch Goal)

**Tech Stack:** React + Vite + TypeScript + TailwindCSS + FastAPI + MySQL

**Core Features:**
- Weapon/Armor/Perk browsers with filters
- Natural language chat interface (RAG integration)
- Build optimizer and damage calculator
- User authentication + saved builds (optional)

**Status:** 🎯 Not started. See `react/` directory for frontend scaffolding.

---

## Data Quality & Testing

**Validation:**
- [ ] Data integrity checks
- [ ] Cross-reference with game files
- [ ] Form ID verification

**Testing:**
- [ ] Unit tests for scrapers
- [ ] Integration tests for queries
- [ ] RAG accuracy tests (`rag/test_no_hallucination.py`)

---

## Next Immediate Steps

1. **Conditional Perk Rules** - Populate weapon_perk_rules with parsed conditions
2. **Damage Formulas** - Research and implement damage calculations
3. **Collectibles** - Add bobbleheads and magazines
4. **Legendary Effects** - Research and implement legendary item effects
5. **Web GUI** - Begin FastAPI backend development (stretch goal)

---

## Notes

**Vulcan Power Armor:** Awaiting per-piece stat data from wiki before import.

**MySQL Reserved Keywords:** Fixed `rank` column with backticks in schema and import scripts.

**Cost:** Vector DB population ~$0.001 (OpenAI embeddings). RAG queries ~$0.01-0.03 each (Claude Sonnet 4).
