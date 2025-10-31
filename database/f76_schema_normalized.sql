USE f76;

-- ============================================================================
-- FULLY NORMALIZED SCHEMA - F76 DATABASE V2
-- ============================================================================
-- This schema eliminates all redundancies and denormalization:
-- - All VARCHAR fields that should be numeric are now numeric
-- - All comma-separated text fields are now junction tables
-- - All string references to other entities are now foreign keys
-- - Proper lookup tables for enums and categories
-- ============================================================================

-- ============================================================================
-- DROP ALL TABLES (CLEAN SLATE)
-- ============================================================================

DROP TABLE IF EXISTS weapon_mechanics;
DROP TABLE IF EXISTS weapon_mechanic_types;
DROP TABLE IF EXISTS weapon_damage_components;
DROP TABLE IF EXISTS armor_resistance_values;
DROP TABLE IF EXISTS consumable_special_modifiers;
DROP TABLE IF EXISTS consumable_effects;
DROP TABLE IF EXISTS mutation_effects;
DROP TABLE IF EXISTS mutation_perk_interactions;
DROP TABLE IF EXISTS legendary_perk_rank_effects;
DROP TABLE IF EXISTS weapon_perk_rules;
DROP TABLE IF EXISTS weapon_legendary_perk_effects;
DROP TABLE IF EXISTS weapon_perks;
DROP TABLE IF EXISTS legendary_perk_ranks;
DROP TABLE IF EXISTS perk_ranks;
DROP TABLE IF EXISTS perk_races;
DROP TABLE IF EXISTS legendary_perk_races;
DROP TABLE IF EXISTS legendary_perks;
DROP TABLE IF EXISTS perks;
DROP TABLE IF EXISTS consumables;
DROP TABLE IF EXISTS mutations;
DROP TABLE IF EXISTS armor;
DROP TABLE IF EXISTS weapons;
DROP TABLE IF EXISTS races;
DROP TABLE IF EXISTS special_attributes;
DROP TABLE IF EXISTS effect_types;
DROP TABLE IF EXISTS damage_types;
DROP TABLE IF EXISTS weapon_types;
DROP TABLE IF EXISTS weapon_classes;
DROP TABLE IF EXISTS armor_types;
DROP TABLE IF EXISTS armor_classes;
DROP TABLE IF EXISTS armor_slots;

-- ============================================================================
-- LOOKUP TABLES
-- ============================================================================

-- Races available in game
CREATE TABLE races (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE,  -- 'Human', 'Ghoul'
  INDEX idx_race_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SPECIAL attributes (S, P, E, C, I, A, L)
CREATE TABLE special_attributes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code CHAR(1) NOT NULL UNIQUE,      -- S, P, E, C, I, A, L
  name VARCHAR(32) NOT NULL UNIQUE,  -- Strength, Perception, etc.
  INDEX idx_special_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Effect types for mutations, consumables, perks
CREATE TABLE effect_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  category ENUM('buff', 'debuff', 'healing', 'damage', 'resistance', 'special', 'resource') NOT NULL,
  INDEX idx_effect_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Damage types
CREATE TABLE damage_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE,  -- 'physical', 'energy', 'radiation', 'fire', 'cryo', 'poison'
  INDEX idx_damage_type (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon types (high level)
CREATE TABLE weapon_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,  -- 'Ranged', 'Melee', 'Thrown'
  INDEX idx_weapon_type (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon classes (specific)
CREATE TABLE weapon_classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,  -- 'Pistol', 'Rifle', 'Shotgun', 'Heavy Gun', etc.
  INDEX idx_weapon_class (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Armor types
CREATE TABLE armor_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE,  -- 'regular', 'power'
  INDEX idx_armor_type (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Armor classes
CREATE TABLE armor_classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE,  -- 'Light', 'Sturdy', 'Heavy'
  INDEX idx_armor_class (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Armor slots
CREATE TABLE armor_slots (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,  -- 'Chest', 'Left Arm', 'Right Arm', 'Left Leg', 'Right Leg', 'Helmet', 'Torso'
  INDEX idx_armor_slot (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- WEAPONS TABLE (NORMALIZED)
-- ============================================================================

CREATE TABLE weapons (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  weapon_type_id INT,
  weapon_class_id INT,
  min_level INT,                      -- Changed from VARCHAR to INT
  form_id CHAR(8),
  source_url TEXT,
  UNIQUE KEY uq_weapon_name (name),
  FOREIGN KEY (weapon_type_id) REFERENCES weapon_types(id) ON DELETE SET NULL,
  FOREIGN KEY (weapon_class_id) REFERENCES weapon_classes(id) ON DELETE SET NULL,
  INDEX idx_weapons_type (weapon_type_id),
  INDEX idx_weapons_class (weapon_class_id),
  INDEX idx_weapons_level (min_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon damage components (normalized from VARCHAR damage field)
CREATE TABLE weapon_damage_components (
  id INT AUTO_INCREMENT PRIMARY KEY,
  weapon_id INT NOT NULL,
  damage_type_id INT NOT NULL,
  min_damage DECIMAL(8,2) NOT NULL,
  max_damage DECIMAL(8,2),            -- NULL if single value
  level_tier INT,                     -- For multi-level weapons (1, 2, 3, 4)
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (damage_type_id) REFERENCES damage_types(id),
  INDEX idx_wdc_weapon (weapon_id),
  INDEX idx_wdc_type (damage_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- ARMOR TABLE (NORMALIZED)
-- ============================================================================

CREATE TABLE armor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  armor_class_id INT,                 -- FK to armor_classes
  armor_slot_id INT,                  -- FK to armor_slots
  armor_type_id INT,                  -- FK to armor_types
  set_name VARCHAR(128),
  min_level INT,                      -- Changed from VARCHAR to INT
  form_id CHAR(8),
  source_url TEXT,
  INDEX idx_armor_name (name),
  INDEX idx_armor_set (set_name),
  INDEX idx_armor_slot (armor_slot_id),
  INDEX idx_armor_class (armor_class_id),
  INDEX idx_armor_type (armor_type_id),
  INDEX idx_armor_level (min_level),
  FOREIGN KEY (armor_class_id) REFERENCES armor_classes(id) ON DELETE SET NULL,
  FOREIGN KEY (armor_slot_id) REFERENCES armor_slots(id) ON DELETE SET NULL,
  FOREIGN KEY (armor_type_id) REFERENCES armor_types(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Armor resistance values (normalized from VARCHAR fields)
CREATE TABLE armor_resistance_values (
  id INT AUTO_INCREMENT PRIMARY KEY,
  armor_id INT NOT NULL,
  damage_type_id INT NOT NULL,        -- References damage_types: physical, energy, radiation, cryo, fire, poison
  resistance_value DECIMAL(8,2) NOT NULL,
  level_tier INT,                     -- For multi-level armor variants
  FOREIGN KEY (armor_id) REFERENCES armor(id) ON DELETE CASCADE,
  FOREIGN KEY (damage_type_id) REFERENCES damage_types(id),
  INDEX idx_arv_armor (armor_id),
  INDEX idx_arv_type (damage_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- REGULAR PERK TABLES (NORMALIZED)
-- ============================================================================

-- Base perks table
CREATE TABLE perks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  special_id INT,                     -- FK to special_attributes
  min_level INT,
  form_id CHAR(8),
  UNIQUE KEY uq_perk_name (name),
  FOREIGN KEY (special_id) REFERENCES special_attributes(id) ON DELETE SET NULL,
  INDEX idx_perk_special (special_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Perk race restrictions (many-to-many)
CREATE TABLE perk_races (
  perk_id INT NOT NULL,
  race_id INT NOT NULL,
  PRIMARY KEY (perk_id, race_id),
  FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE CASCADE,
  FOREIGN KEY (race_id) REFERENCES races(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Perk ranks
CREATE TABLE perk_ranks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perk_id INT NOT NULL,
  `rank` INT NOT NULL,
  description TEXT NOT NULL,
  form_id CHAR(8),
  FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE CASCADE,
  UNIQUE KEY uq_perk_rank (perk_id, `rank`),
  INDEX idx_prank_rank (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- LEGENDARY PERK TABLES (NORMALIZED)
-- ============================================================================

-- Base legendary perks table
CREATE TABLE legendary_perks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  description TEXT,
  form_id CHAR(8),
  UNIQUE KEY uq_legendary_perk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legendary perk race restrictions (many-to-many)
CREATE TABLE legendary_perk_races (
  legendary_perk_id INT NOT NULL,
  race_id INT NOT NULL,
  PRIMARY KEY (legendary_perk_id, race_id),
  FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE,
  FOREIGN KEY (race_id) REFERENCES races(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legendary perk ranks
CREATE TABLE legendary_perk_ranks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  legendary_perk_id INT NOT NULL,
  `rank` INT NOT NULL,
  description TEXT,
  FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE,
  UNIQUE KEY uq_legendary_perk_rank (legendary_perk_id, `rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legendary perk rank effects (normalized from single effect_value/effect_type columns)
CREATE TABLE legendary_perk_rank_effects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  legendary_perk_rank_id INT NOT NULL,
  effect_type_id INT NOT NULL,
  value DECIMAL(10,2),
  unit VARCHAR(32),                   -- 'percent', 'flat', 'seconds', etc.
  FOREIGN KEY (legendary_perk_rank_id) REFERENCES legendary_perk_ranks(id) ON DELETE CASCADE,
  FOREIGN KEY (effect_type_id) REFERENCES effect_types(id),
  INDEX idx_lpre_rank (legendary_perk_rank_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- WEAPON PERK JUNCTION TABLES
-- ============================================================================

-- Weapons to regular perks
CREATE TABLE weapon_perks (
  weapon_id INT NOT NULL,
  perk_id INT NOT NULL,
  PRIMARY KEY (weapon_id, perk_id),
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapons to legendary perks
CREATE TABLE weapon_legendary_perk_effects (
  weapon_id INT NOT NULL,
  legendary_perk_id INT NOT NULL,
  PRIMARY KEY (weapon_id, legendary_perk_id),
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon perk conditional rules
CREATE TABLE weapon_perk_rules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  weapon_id INT NOT NULL,
  perk_id INT NOT NULL,
  weapon_class ENUM('pistol','rifle','heavy','melee','explosive','any') DEFAULT 'any',
  fire_mode   ENUM('auto','semi','any') DEFAULT 'any',
  scope_state ENUM('scoped','unscoped','any') DEFAULT 'any',
  aim_state   ENUM('ads','hip_fire','any') DEFAULT 'any',
  vats_state  ENUM('in_vats','out_vats','any') DEFAULT 'any',
  mod_requirements VARCHAR(255),
  note VARCHAR(255),
  FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- WEAPON MECHANICS TABLES
-- ============================================================================

-- Lookup table for weapon mechanic types
CREATE TABLE weapon_mechanic_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  description TEXT,
  INDEX idx_mechanic_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapon mechanics (many-to-many with attributes)
CREATE TABLE weapon_mechanics (
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
-- MUTATIONS TABLE (NORMALIZED)
-- ============================================================================

CREATE TABLE mutations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  form_id CHAR(8),
  exclusive_mutation_id INT,          -- FK to another mutation (Carnivore <-> Herbivore)
  source_url TEXT,
  UNIQUE KEY uq_mutation_name (name),
  FOREIGN KEY (exclusive_mutation_id) REFERENCES mutations(id) ON DELETE SET NULL,
  INDEX idx_mutation_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Mutation effects (normalized from positive_effects/negative_effects TEXT)
CREATE TABLE mutation_effects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mutation_id INT NOT NULL,
  effect_type_id INT NOT NULL,
  value DECIMAL(10,2),
  duration_seconds INT,
  polarity ENUM('positive', 'negative') NOT NULL,
  description TEXT,
  FOREIGN KEY (mutation_id) REFERENCES mutations(id) ON DELETE CASCADE,
  FOREIGN KEY (effect_type_id) REFERENCES effect_types(id),
  INDEX idx_me_mutation (mutation_id),
  INDEX idx_me_polarity (polarity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Mutation-perk interactions (normalized from suppression_perk/enhancement_perk VARCHAR)
CREATE TABLE mutation_perk_interactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mutation_id INT NOT NULL,
  perk_id INT,
  legendary_perk_id INT,
  interaction_type ENUM('suppression', 'enhancement') NOT NULL,
  FOREIGN KEY (mutation_id) REFERENCES mutations(id) ON DELETE CASCADE,
  FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE SET NULL,
  FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE SET NULL,
  CHECK ((perk_id IS NOT NULL AND legendary_perk_id IS NULL) OR
         (perk_id IS NULL AND legendary_perk_id IS NOT NULL)),
  INDEX idx_mpi_mutation (mutation_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CONSUMABLES TABLE (NORMALIZED)
-- ============================================================================

CREATE TABLE consumables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category ENUM('food', 'drink', 'chem', 'aid', 'alcohol', 'beverage') NOT NULL,
  subcategory VARCHAR(64),
  duration_seconds INT,               -- Changed from VARCHAR to INT
  hp_restore DECIMAL(8,2),            -- Changed from VARCHAR to DECIMAL
  rads DECIMAL(8,2),                  -- Changed from VARCHAR to DECIMAL (negative = removal)
  hunger_satisfaction DECIMAL(8,2),   -- Changed from VARCHAR to DECIMAL
  thirst_satisfaction DECIMAL(8,2),   -- Changed from VARCHAR to DECIMAL
  addiction_risk DECIMAL(5,2),        -- Changed from VARCHAR to DECIMAL (percentage)
  disease_risk DECIMAL(5,2),          -- Changed from VARCHAR to DECIMAL (percentage)
  weight DECIMAL(5,2),
  value INT,
  form_id CHAR(8),
  crafting_station VARCHAR(64),
  source_url TEXT,
  UNIQUE KEY uq_consumable_name (name),
  INDEX idx_consumable_category (category),
  INDEX idx_consumable_subcategory (subcategory)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Consumable effects (normalized from effects TEXT)
CREATE TABLE consumable_effects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  consumable_id INT NOT NULL,
  effect_type_id INT NOT NULL,
  value DECIMAL(10,2),
  description TEXT,
  FOREIGN KEY (consumable_id) REFERENCES consumables(id) ON DELETE CASCADE,
  FOREIGN KEY (effect_type_id) REFERENCES effect_types(id),
  INDEX idx_ce_consumable (consumable_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Consumable SPECIAL modifiers (normalized from special_modifiers TEXT)
CREATE TABLE consumable_special_modifiers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  consumable_id INT NOT NULL,
  special_id INT NOT NULL,
  modifier INT NOT NULL,              -- Can be negative
  FOREIGN KEY (consumable_id) REFERENCES consumables(id) ON DELETE CASCADE,
  FOREIGN KEY (special_id) REFERENCES special_attributes(id),
  INDEX idx_csm_consumable (consumable_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- BACKWARD-COMPATIBLE VIEWS (MAINTAIN OLD INTERFACE)
-- ============================================================================

-- View: Complete weapon info with all affecting perks
CREATE OR REPLACE VIEW v_weapons_with_perks AS
SELECT
  w.id,
  w.name AS weapon_name,
  wt.name AS weapon_type,
  wc.name AS weapon_class,
  w.min_level AS level,
  -- Reconstruct damage string (simplified - shows first damage component)
  CONCAT(
    COALESCE(MIN(wdc.min_damage), ''),
    CASE WHEN MIN(wdc.max_damage) IS NOT NULL
      THEN CONCAT('-', MIN(wdc.max_damage))
      ELSE ''
    END
  ) AS damage,
  GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
  GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
  w.source_url
FROM weapons w
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
LEFT JOIN weapon_damage_components wdc ON w.id = wdc.weapon_id
LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
LEFT JOIN perks p ON wp.perk_id = p.id
LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
LEFT JOIN legendary_perks lp ON wlpe.legendary_perk_id = lp.id
GROUP BY w.id, w.name, wt.name, wc.name, w.min_level, w.source_url;

-- View: Complete armor info
CREATE OR REPLACE VIEW v_armor_complete AS
SELECT
  a.id,
  a.name,
  at.name AS armor_type,
  ac.name AS class,
  asl.name AS slot,
  a.set_name,
  a.min_level AS level,
  -- Reconstruct resistance fields
  MAX(CASE WHEN dt.name = 'physical' THEN arv.resistance_value END) AS damage_resistance,
  MAX(CASE WHEN dt.name = 'energy' THEN arv.resistance_value END) AS energy_resistance,
  MAX(CASE WHEN dt.name = 'radiation' THEN arv.resistance_value END) AS radiation_resistance,
  MAX(CASE WHEN dt.name = 'cryo' THEN arv.resistance_value END) AS cryo_resistance,
  MAX(CASE WHEN dt.name = 'fire' THEN arv.resistance_value END) AS fire_resistance,
  MAX(CASE WHEN dt.name = 'poison' THEN arv.resistance_value END) AS poison_resistance,
  a.source_url
FROM armor a
LEFT JOIN armor_types at ON a.armor_type_id = at.id
LEFT JOIN armor_classes ac ON a.armor_class_id = ac.id
LEFT JOIN armor_slots asl ON a.armor_slot_id = asl.id
LEFT JOIN armor_resistance_values arv ON a.id = arv.armor_id
LEFT JOIN damage_types dt ON arv.damage_type_id = dt.id
GROUP BY a.id, a.name, at.name, ac.name, asl.name, a.set_name, a.min_level, a.source_url;

-- View: Regular perks with all ranks
CREATE OR REPLACE VIEW v_perks_all_ranks AS
SELECT
  p.id AS perk_id,
  p.name AS perk_name,
  sa.code AS special,
  p.min_level,
  GROUP_CONCAT(DISTINCT r.name ORDER BY r.name SEPARATOR ', ') AS race,
  pr.`rank`,
  pr.description AS rank_description,
  pr.form_id
FROM perks p
LEFT JOIN special_attributes sa ON p.special_id = sa.id
LEFT JOIN perk_races praces ON p.id = praces.perk_id
LEFT JOIN races r ON praces.race_id = r.id
LEFT JOIN perk_ranks pr ON p.id = pr.perk_id
GROUP BY p.id, p.name, sa.code, p.min_level, pr.`rank`, pr.description, pr.form_id
ORDER BY p.name, pr.`rank`;

-- View: Legendary perks with all ranks
CREATE OR REPLACE VIEW v_legendary_perks_all_ranks AS
SELECT
  lp.id AS legendary_perk_id,
  lp.name AS perk_name,
  lp.description AS base_description,
  GROUP_CONCAT(DISTINCT r.name ORDER BY r.name SEPARATOR ', ') AS race,
  lpr.`rank`,
  lpr.description AS rank_description,
  -- Simplified: show first effect value/type only
  (SELECT value FROM legendary_perk_rank_effects WHERE legendary_perk_rank_id = lpr.id LIMIT 1) AS effect_value,
  (SELECT unit FROM legendary_perk_rank_effects WHERE legendary_perk_rank_id = lpr.id LIMIT 1) AS effect_type
FROM legendary_perks lp
LEFT JOIN legendary_perk_races lpraces ON lp.id = lpraces.legendary_perk_id
LEFT JOIN races r ON lpraces.race_id = r.id
LEFT JOIN legendary_perk_ranks lpr ON lp.id = lpr.legendary_perk_id
GROUP BY lp.id, lp.name, lp.description, lpr.`rank`, lpr.description, lpr.id
ORDER BY lp.name, lpr.`rank`;

-- View: All mutations with effects
CREATE OR REPLACE VIEW v_mutations_complete AS
SELECT
  m.id AS mutation_id,
  m.name AS mutation_name,
  -- Reconstruct positive/negative effects
  GROUP_CONCAT(
    DISTINCT CASE WHEN me.polarity = 'positive' THEN me.description END
    ORDER BY me.id SEPARATOR '; '
  ) AS positive_effects,
  GROUP_CONCAT(
    DISTINCT CASE WHEN me.polarity = 'negative' THEN me.description END
    ORDER BY me.id SEPARATOR '; '
  ) AS negative_effects,
  m.form_id,
  m2.name AS exclusive_with,
  -- Reconstruction of perk interactions (simplified)
  (SELECT p.name FROM mutation_perk_interactions mpi
   JOIN perks p ON mpi.perk_id = p.id
   WHERE mpi.mutation_id = m.id AND mpi.interaction_type = 'suppression' LIMIT 1) AS suppression_perk,
  (SELECT p.name FROM mutation_perk_interactions mpi
   JOIN perks p ON mpi.perk_id = p.id
   WHERE mpi.mutation_id = m.id AND mpi.interaction_type = 'enhancement' LIMIT 1) AS enhancement_perk,
  m.source_url
FROM mutations m
LEFT JOIN mutations m2 ON m.exclusive_mutation_id = m2.id
LEFT JOIN mutation_effects me ON m.id = me.mutation_id
GROUP BY m.id, m.name, m.form_id, m2.name, m.source_url
ORDER BY m.name;

-- View: All consumables with effects
CREATE OR REPLACE VIEW v_consumables_complete AS
SELECT
  c.id AS consumable_id,
  c.name AS consumable_name,
  c.category,
  c.subcategory,
  -- Reconstruct effects field
  GROUP_CONCAT(DISTINCT ce.description ORDER BY ce.id SEPARATOR '; ') AS effects,
  CONCAT(c.duration_seconds, ' seconds') AS duration,
  c.hp_restore,
  c.rads,
  c.hunger_satisfaction,
  c.thirst_satisfaction,
  -- Reconstruct special_modifiers
  GROUP_CONCAT(
    DISTINCT CONCAT(
      CASE WHEN csm.modifier > 0 THEN '+' ELSE '' END,
      csm.modifier, ' ', sa.code
    )
    ORDER BY sa.code SEPARATOR ', '
  ) AS special_modifiers,
  c.addiction_risk,
  c.disease_risk,
  c.weight,
  c.value,
  c.form_id,
  c.crafting_station,
  c.source_url
FROM consumables c
LEFT JOIN consumable_effects ce ON c.id = ce.consumable_id
LEFT JOIN consumable_special_modifiers csm ON c.id = csm.consumable_id
LEFT JOIN special_attributes sa ON csm.special_id = sa.id
GROUP BY c.id, c.name, c.category, c.subcategory, c.duration_seconds, c.hp_restore,
         c.rads, c.hunger_satisfaction, c.thirst_satisfaction, c.addiction_risk,
         c.disease_risk, c.weight, c.value, c.form_id, c.crafting_station, c.source_url
ORDER BY c.category, c.name;

-- View: Weapons with mechanics
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
-- POPULATE LOOKUP TABLES
-- ============================================================================

-- Races
INSERT INTO races (name) VALUES ('Human'), ('Ghoul');

-- SPECIAL attributes
INSERT INTO special_attributes (code, name) VALUES
  ('S', 'Strength'),
  ('P', 'Perception'),
  ('E', 'Endurance'),
  ('C', 'Charisma'),
  ('I', 'Intelligence'),
  ('A', 'Agility'),
  ('L', 'Luck');

-- Damage types
INSERT INTO damage_types (name) VALUES
  ('physical'),
  ('energy'),
  ('radiation'),
  ('fire'),
  ('cryo'),
  ('poison');

-- Common weapon types (will be populated by migration/import)
INSERT INTO weapon_types (name) VALUES ('Ranged'), ('Melee'), ('Thrown');

-- Common armor types
INSERT INTO armor_types (name) VALUES ('regular'), ('power');

-- ============================================================================
-- NOTES ON MIGRATION
-- ============================================================================
-- To migrate from old schema to this one:
-- 1. Run migrate_to_normalized.py to transform existing data
-- 2. All views maintain backward compatibility with old column names
-- 3. Import scripts need updates to write to new normalized structure
-- 4. RAG system should work unchanged since it queries views
-- ============================================================================
