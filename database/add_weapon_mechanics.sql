-- ============================================================================
-- WEAPON MECHANICS EXTENSION
-- ============================================================================
-- This migration adds support for special weapon mechanics like charge-up,
-- chain lightning, spin-up, explosive AOE, and other unique features.
-- ============================================================================

USE f76;

-- ============================================================================
-- CREATE WEAPON MECHANICS TABLES
-- ============================================================================

-- Lookup table for mechanic types
CREATE TABLE IF NOT EXISTS weapon_mechanic_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  description TEXT,
  INDEX idx_mechanic_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon mechanics (many-to-many with attributes)
CREATE TABLE IF NOT EXISTS weapon_mechanics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  weapon_id INT NOT NULL,
  mechanic_type_id INT NOT NULL,
  -- Generic attribute fields for flexibility
  numeric_value DECIMAL(10,2),      -- For charge multiplier (0.50), AoE radius, damage reduction %, etc.
  numeric_value_2 DECIMAL(10,2),    -- For secondary values (e.g., chain damage reduction per hop)
  string_value VARCHAR(255),         -- For descriptions or specific conditions
  unit VARCHAR(32),                  -- 'multiplier', 'percent', 'meters', 'seconds', etc.
  notes TEXT,
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (mechanic_type_id) REFERENCES weapon_mechanic_types(id),
  INDEX idx_wm_weapon (weapon_id),
  INDEX idx_wm_mechanic (mechanic_type_id),
  UNIQUE KEY uq_weapon_mechanic (weapon_id, mechanic_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- POPULATE MECHANIC TYPES
-- ============================================================================

INSERT INTO weapon_mechanic_types (name, description) VALUES
  ('charge', 'Weapon can be charged to increase damage. Uncharged shots deal reduced damage.'),
  ('charge_self_damage', 'Weapon charges by reloading repeatedly and irradiates the user.'),
  ('chain_lightning', 'Weapon damage chains to nearby enemies with reduced damage per hop.'),
  ('spin_up', 'Weapon requires time to spin up before firing at full rate.'),
  ('explosive_aoe', 'Weapon deals area-of-effect explosive damage.'),
  ('trap_creation', 'Weapon creates damage traps on impact.'),
  ('beam_weapon', 'Weapon fires a continuous beam rather than projectiles.')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- ============================================================================
-- POPULATE MECHANICS FOR KNOWN WEAPONS
-- ============================================================================

-- Gauss weapons: charge mechanic (50% damage uncharged)
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, numeric_value, unit, notes)
SELECT w.id, wmt.id, 0.50, 'multiplier', 'Uncharged damage is 50% of listed damage. Fully charged is 100%.'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'charge'
WHERE w.name IN ('Gauss rifle', 'Gauss shotgun', 'Gauss pistol', 'Gauss minigun')
ON DUPLICATE KEY UPDATE
  numeric_value = VALUES(numeric_value),
  unit = VALUES(unit),
  notes = VALUES(notes);

-- Gauss rifle: explosive AOE mechanic
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, string_value, notes)
SELECT w.id, wmt.id, 'explosive', 'Fires explosive projectile that deals AOE damage to clustered enemies'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'explosive_aoe'
WHERE w.name = 'Gauss rifle'
ON DUPLICATE KEY UPDATE
  string_value = VALUES(string_value),
  notes = VALUES(notes);

-- Tesla rifle: chain lightning mechanic
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, numeric_value, numeric_value_2, unit, notes)
SELECT w.id, wmt.id, 0.65, 0.35, 'multiplier', 'First chain target takes 65% damage, each successive target takes 35% less (second chain: 42.25%)'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'chain_lightning'
WHERE w.name = 'Tesla rifle'
ON DUPLICATE KEY UPDATE
  numeric_value = VALUES(numeric_value),
  numeric_value_2 = VALUES(numeric_value_2),
  unit = VALUES(unit),
  notes = VALUES(notes);

-- Minigun: spin-up mechanic
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, notes)
SELECT w.id, wmt.id, 'Requires a moment to spin up before firing'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'spin_up'
WHERE w.name = 'Minigun'
ON DUPLICATE KEY UPDATE notes = VALUES(notes);

-- Gatling weapons: spin-up mechanic
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, notes)
SELECT w.id, wmt.id, 'Requires a moment to spin up before firing'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'spin_up'
WHERE w.name IN ('Gatling gun', 'Gatling laser', 'Gatling plasma', 'Ultracite Gatling laser')
ON DUPLICATE KEY UPDATE notes = VALUES(notes);

-- Salvaged Assaultron head: charge with self-damage
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, notes)
SELECT w.id, wmt.id, 'Charged by reloading repeatedly. Higher charges deal more damage but irradiate the user.'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'charge_self_damage'
WHERE w.name = 'Salvaged Assaultron head'
ON DUPLICATE KEY UPDATE notes = VALUES(notes);

-- Explosive heavy guns: explosive AOE
INSERT INTO weapon_mechanics (weapon_id, mechanic_type_id, string_value, notes)
SELECT w.id, wmt.id, 'explosive', 'Fires explosive projectiles with area-of-effect damage'
FROM weapons w
JOIN weapon_mechanic_types wmt ON wmt.name = 'explosive_aoe'
WHERE w.name IN (
  'Fat Man', 'Missile launcher', 'Auto grenade launcher',
  'M79 grenade launcher', 'Hellstorm missile launcher'
)
ON DUPLICATE KEY UPDATE
  string_value = VALUES(string_value),
  notes = VALUES(notes);

-- ============================================================================
-- CREATE VIEW FOR EASY QUERYING
-- ============================================================================

CREATE OR REPLACE VIEW v_weapons_with_mechanics AS
SELECT
  w.id,
  w.name AS weapon_name,
  wt.name AS weapon_type,
  wc.name AS weapon_class,
  wmt.name AS mechanic_type,
  wmt.description AS mechanic_description,
  wm.numeric_value,
  wm.numeric_value_2,
  wm.string_value,
  wm.unit,
  wm.notes AS mechanic_notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
ORDER BY w.name, wmt.name;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show all weapons with charge mechanic
-- SELECT * FROM v_weapons_with_mechanics WHERE mechanic_type = 'charge';

-- Show all mechanics for Gauss weapons
-- SELECT * FROM v_weapons_with_mechanics WHERE weapon_name LIKE '%Gauss%';

-- Show all weapon mechanics
-- SELECT mechanic_type, COUNT(*) as weapon_count
-- FROM v_weapons_with_mechanics
-- GROUP BY mechanic_type;

-- ============================================================================
-- NOTES
-- ============================================================================
-- After running this migration:
-- 1. Update import scripts to detect and populate mechanics from wiki data
-- 2. Update RAG system to include weapon mechanics in embeddings
-- 3. Test with queries like "Which weapons can be charged?"
-- ============================================================================
