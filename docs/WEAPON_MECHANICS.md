# Weapon Mechanics System

## Overview

The weapon mechanics system provides a flexible way to model special weapon features in Fallout 76, such as:

- **Charge mechanics** (Gauss weapons)
- **Chain lightning** (Tesla rifle)
- **Spin-up delay** (Minigun, Gatling weapons)
- **Explosive AOE** (explosive heavy weapons)
- **Self-damage charging** (Salvaged Assaultron head)
- And more...

## Database Schema

### Tables

#### `weapon_mechanic_types`
Lookup table for mechanic types:
```sql
CREATE TABLE weapon_mechanic_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  description TEXT,
  INDEX idx_mechanic_name (name)
);
```

#### `weapon_mechanics`
Many-to-many relationship with flexible attributes:
```sql
CREATE TABLE weapon_mechanics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  weapon_id INT NOT NULL,
  mechanic_type_id INT NOT NULL,
  numeric_value DECIMAL(10,2),      -- e.g., 0.50 for charge multiplier
  numeric_value_2 DECIMAL(10,2),    -- e.g., 0.35 for chain damage reduction
  string_value VARCHAR(255),         -- e.g., 'explosive'
  unit VARCHAR(32),                  -- e.g., 'multiplier', 'percent', 'meters'
  notes TEXT,
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (mechanic_type_id) REFERENCES weapon_mechanic_types(id),
  UNIQUE KEY uq_weapon_mechanic (weapon_id, mechanic_type_id)
);
```

### View

#### `v_weapons_with_mechanics`
Convenient view for querying weapons with their mechanics:
```sql
SELECT * FROM v_weapons_with_mechanics WHERE weapon_name LIKE 'Gauss%';
```

## Installation

### Step 1: Apply Migration to Existing Database

If you already have the normalized schema running:

```bash
mysql -u your_user -p f76 < database/add_weapon_mechanics.sql
```

### Step 2: Populate Mechanics

Run the import script to populate weapon mechanics:

```bash
python database/import_weapon_mechanics.py -u your_user -p your_password
```

Or use environment variables:

```bash
export MYSQL_USER=your_user
export MYSQL_PASS=your_password
python database/import_weapon_mechanics.py
```

### Step 3: Verify

Check that mechanics were imported correctly:

```sql
-- Count mechanics by type
SELECT wmt.name, COUNT(*) as weapon_count
FROM weapon_mechanics wm
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
GROUP BY wmt.name;

-- View all Gauss weapons with charge mechanic
SELECT * FROM v_weapons_with_mechanics
WHERE weapon_name LIKE 'Gauss%';
```

## Supported Mechanics

### 1. Charge Mechanic

**Weapons**: Gauss rifle, Gauss shotgun, Gauss pistol

**Note**: Gauss minigun does NOT have charge mechanic - it only has spin-up like other miniguns

**Behavior**:
- Uncharged shots deal **50% of listed damage**
- Fully charged shots deal **100% of listed damage**
- Charging affects actual fire rate

**Data**:
```sql
mechanic_type: 'charge'
numeric_value: 0.50
unit: 'multiplier'
```

### 2. Chain Lightning

**Weapons**: Tesla rifle

**Behavior**:
- Damage chains to nearby enemies
- First chain target: **65% damage** (numeric_value)
- Each successive hop: **35% reduction** (numeric_value_2)
- Second chain: 42.25% (65% × 0.65)

**Data**:
```sql
mechanic_type: 'chain_lightning'
numeric_value: 0.65
numeric_value_2: 0.35
unit: 'multiplier'
```

### 3. Spin-Up Delay

**Weapons**: Minigun, Gauss minigun, Gatling gun, Gatling laser, Gatling plasma, Ultracite Gatling laser, Pepper Shaker

**Behavior**:
- Requires time to spin up before firing
- Actual fire rate lower than listed

**Data**:
```sql
mechanic_type: 'spin_up'
notes: 'Requires a moment to spin up before firing'
```

### 4. Explosive AOE

**Weapons**: Gauss rifle, Fat Man, Missile launcher, Auto grenade launcher, M79 grenade launcher, Hellstorm missile launcher, Tesla cannon

**Behavior**:
- Fires explosive projectiles
- Deals area-of-effect damage
- Can hit multiple clustered enemies

**Data**:
```sql
mechanic_type: 'explosive_aoe'
string_value: 'explosive'
```

### 5. Charge with Self-Damage

**Weapons**: Salvaged Assaultron head

**Behavior**:
- Charges by reloading repeatedly
- Higher charges = more damage
- **Irradiates the user** while charging

**Data**:
```sql
mechanic_type: 'charge_self_damage'
notes: 'Charged by reloading repeatedly. Higher charges deal more damage but irradiate the user.'
```

## Query Examples

### Find all weapons with charge mechanics

```sql
SELECT weapon_name, mechanic_notes, numeric_value, unit
FROM v_weapons_with_mechanics
WHERE mechanic_type = 'charge';
```

**Expected output**:
```
| weapon_name   | mechanic_notes                                        | numeric_value | unit       |
|---------------|-------------------------------------------------------|---------------|------------|
| Gauss rifle   | Uncharged damage is 50% of listed damage. Fully...   | 0.50          | multiplier |
| Gauss shotgun | Uncharged damage is 50% of listed damage. Fully...   | 0.50          | multiplier |
| Gauss pistol  | Uncharged damage is 50% of listed damage. Fully...   | 0.50          | multiplier |
```

**Note**: Only 3 Gauss weapons, not 4 - Gauss minigun has spin-up, not charge

### Find all weapons with explosive AOE

```sql
SELECT weapon_name, string_value, mechanic_notes
FROM v_weapons_with_mechanics
WHERE mechanic_type = 'explosive_aoe';
```

### Get all mechanics for a specific weapon

```sql
SELECT mechanic_type, mechanic_description, numeric_value, numeric_value_2,
       string_value, unit, mechanic_notes
FROM v_weapons_with_mechanics
WHERE weapon_name = 'Gauss rifle';
```

**Expected output** (Gauss rifle has both charge AND explosive_aoe):
```
| mechanic_type | numeric_value | string_value | notes                                      |
|---------------|---------------|--------------|---------------------------------------------|
| charge        | 0.50          | NULL         | Uncharged damage is 50% of listed damage... |
| explosive_aoe | NULL          | explosive    | Fires explosive projectile that deals AOE... |
```

### Count weapons by mechanic type

```sql
SELECT mechanic_type, COUNT(DISTINCT weapon_name) as weapon_count
FROM v_weapons_with_mechanics
GROUP BY mechanic_type
ORDER BY weapon_count DESC;
```

## RAG Integration

The weapon mechanics data enhances RAG (Retrieval Augmented Generation) queries:

### Example RAG Query
**User**: "Which weapons can I charge for more damage?"

**Enhanced Context** (from v_weapons_with_mechanics):
```
Weapons with charge mechanic:
- Gauss rifle: 50% uncharged, 100% charged (also has explosive AOE)
- Gauss shotgun: 50% uncharged, 100% charged
- Gauss pistol: 50% uncharged, 100% charged

Note: Gauss minigun does not have charge - it only has spin-up like other miniguns
```

### Update Vector Database

After importing mechanics, update your vector embeddings:

```bash
python rag/populate_vector_db.py
```

This will ensure ChromaDB includes weapon mechanics in its embeddings for better query results.

## Adding New Mechanics

### Option 1: Via SQL

```sql
-- Add new mechanic type
INSERT INTO weapon_mechanic_types (name, description)
VALUES ('beam_weapon', 'Weapon fires a continuous beam rather than projectiles');

-- Add mechanic to weapon
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, notes)
SELECT w.id, wmt.id, 'Fires continuous beam'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'beam_weapon'
WHERE w.name = 'Plasma cutter';
```

### Option 2: Via Python Script

Edit `database/import_weapon_mechanics.py` and add a new rule to `_initialize_mechanic_rules()`:

```python
{
    'mechanic_type': 'beam_weapon',
    'weapon_names': ['Plasma cutter', 'Gatling laser', 'Gatling plasma'],
    'weapon_name_patterns': [r'Gatling\s+(laser|plasma)'],
    'notes': 'Fires continuous beam rather than projectiles'
}
```

Then re-run the import script.

## Use Cases

### Build Optimization
Users can query: "What weapons benefit from slow, charged shots?" → Gauss weapons

### Damage Calculation
Factor in charge multipliers and chain damage reduction for accurate DPS calculations

### Perk Synergies
Cross-reference mechanics with perks:
- Charge weapons + "Charging" perks
- Explosive AOE + Demolition Expert perk

### Wiki Integration
Automatically detect and populate mechanics from scraped wiki data

## Technical Notes

### Why This Design?

1. **Flexible**: Generic numeric/string fields support various mechanic types
2. **Extensible**: Easy to add new mechanic types without schema changes
3. **Queryable**: Can filter/search by mechanic type efficiently
4. **Normalized**: Maintains database best practices

### Alternative Designs Considered

**Boolean flags** (rejected): Not extensible, would need schema changes for new mechanics

**JSON column** (rejected): Harder to query, less normalized, but could work for MySQL 5.7+

**EAV pattern** (rejected): Over-engineered for this use case

## Future Enhancements

Potential mechanics to add:

- **Beam weapons**: Continuous damage over time
- **Burst fire**: Fires multiple rounds per trigger pull
- **Projectile behavior**: Ballistic arc vs. straight line
- **Reload types**: Magazine vs. single-round
- **Special ammo**: Unique ammunition effects

## Summary

The weapon mechanics system provides:

✓ Accurate modeling of Gauss weapon charge mechanics (50% uncharged)
✓ Gauss rifle, shotgun, and pistol have charge (Gauss minigun only has spin-up)
✓ Support for chain lightning, spin-up, and explosive AOE
✓ Flexible schema for future mechanics
✓ Easy querying via views
✓ Integration with RAG system

The three chargeable Gauss weapons (rifle, shotgun, pistol) now correctly represent that uncharged shots deal 50% damage!
