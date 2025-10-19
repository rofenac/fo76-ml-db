USE f76;

-- ============================================================================
-- DROP ALL TABLES (CLEAN SLATE)
-- ============================================================================

DROP TABLE IF EXISTS weapon_perk_rules;
DROP TABLE IF EXISTS weapon_legendary_perk_effects;
DROP TABLE IF EXISTS weapon_perks;
DROP TABLE IF EXISTS legendary_perk_ranks;
DROP TABLE IF EXISTS perk_ranks;
DROP TABLE IF EXISTS legendary_perks;
DROP TABLE IF EXISTS perks;
DROP TABLE IF EXISTS consumables;
DROP TABLE IF EXISTS mutations;
DROP TABLE IF EXISTS power_armor;  -- Deprecated: merged into armor table
DROP TABLE IF EXISTS armor;
DROP TABLE IF EXISTS weapons;

-- ============================================================================
-- WEAPONS TABLE
-- ============================================================================

CREATE TABLE weapons (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(64),
  class VARCHAR(64),
  level VARCHAR(64),
  damage VARCHAR(255),
  perks_raw TEXT,
  source_url TEXT,
  UNIQUE KEY uq_weapon_name (name),
  INDEX idx_weapons_type (type),
  INDEX idx_weapons_class (class)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- ARMOR TABLES
-- ============================================================================

CREATE TABLE armor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  class VARCHAR(64),                   -- "Light", "Sturdy", "Heavy" (regular armor only)
  slot VARCHAR(64),                    -- "Chest", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Helmet", "Torso"
  damage_resistance VARCHAR(64),       -- Physical damage resistance (DR)
  energy_resistance VARCHAR(64),       -- Energy damage resistance (ER)
  radiation_resistance VARCHAR(64),    -- Radiation resistance (RR)
  cryo_resistance VARCHAR(64),         -- Cryo resistance (for Arctic Marine, etc.)
  fire_resistance VARCHAR(64),         -- Fire resistance (if applicable)
  poison_resistance VARCHAR(64),       -- Poison resistance (if applicable)
  set_name VARCHAR(128),               -- Armor set name (for matching set bonuses)
  armor_type ENUM('regular', 'power') DEFAULT 'regular',  -- Regular armor or power armor
  level VARCHAR(64),                   -- Level requirement (single level per row)
  source_url TEXT,
  INDEX idx_armor_name (name),         -- Index for searching by name (not unique due to level variants)
  INDEX idx_armor_set (set_name),
  INDEX idx_armor_slot (slot),
  INDEX idx_armor_class (class),
  INDEX idx_armor_type (armor_type),
  INDEX idx_armor_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- POWER ARMOR (MERGED INTO ARMOR TABLE)
-- ============================================================================
-- Power armor is now stored in the armor table with armor_type='power'
-- Removed separate power_armor table to unify schema

-- ============================================================================
-- REGULAR PERK TABLES
-- ============================================================================

-- Base perks table (one row per unique perk name)
CREATE TABLE perks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  special CHAR(1),                     -- S, P, E, C, I, A, L
  level INT,                           -- Min level required
  race VARCHAR(32),                    -- "Human", "Ghoul", "Human, Ghoul"
  UNIQUE KEY uq_perk_name (name),
  INDEX idx_perk_special (special),
  INDEX idx_perk_race (race)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Perk ranks (multiple rows for each perk with different ranks)
-- This allows us to store rank-specific effects and do damage calculations
CREATE TABLE perk_ranks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perk_id INT NOT NULL,
  `rank` INT NOT NULL,                   -- 1, 2, 3, 4, etc.
  description TEXT NOT NULL,           -- Rank-specific description with values
  form_id CHAR(8),                     -- Some ranks have form IDs, some don't
  CONSTRAINT fk_pr_perk FOREIGN KEY (perk_id) REFERENCES perks(id) ON DELETE CASCADE,
  UNIQUE KEY uq_perk_rank (perk_id, `rank`),
  INDEX idx_prank_rank (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- LEGENDARY PERK TABLES
-- ============================================================================

-- Base legendary perks table (one row per unique legendary perk name)
CREATE TABLE legendary_perks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  description TEXT,                    -- Base/overview description
  race VARCHAR(32) DEFAULT 'Human, Ghoul', -- Most are universal, 2 are ghoul-only
  UNIQUE KEY uq_legendary_perk_name (name),
  INDEX idx_legendary_race (race)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Legendary perk ranks (many legendary perks have 4+ ranks with scaling effects)
CREATE TABLE legendary_perk_ranks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  legendary_perk_id INT NOT NULL,
  `rank` INT NOT NULL,                   -- 1, 2, 3, 4, etc.
  description TEXT,                    -- Rank-specific description
  effect_value VARCHAR(128),           -- Parsed numeric value (e.g., "10" from "10% damage")
  effect_type VARCHAR(64),             -- "percentage", "flat", "duration", etc.
  CONSTRAINT fk_lpr_perk FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE,
  UNIQUE KEY uq_legendary_perk_rank (legendary_perk_id, `rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- WEAPON PERK JUNCTION TABLES
-- ============================================================================

-- Weapons to regular perks that can affect them
CREATE TABLE weapon_perks (
  weapon_id INT NOT NULL,
  perk_id INT NOT NULL,
  PRIMARY KEY (weapon_id, perk_id),
  CONSTRAINT fk_wp_weapon FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  CONSTRAINT fk_wp_perk   FOREIGN KEY (perk_id)   REFERENCES perks(id)   ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Weapons to legendary perks that can affect them
CREATE TABLE weapon_legendary_perk_effects (
  weapon_id INT NOT NULL,
  legendary_perk_id INT NOT NULL,
  PRIMARY KEY (weapon_id, legendary_perk_id),
  CONSTRAINT fk_wlpe_weapon FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  CONSTRAINT fk_wlpe_perk   FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CONDITIONAL PERK RULES (FUTURE)
-- ============================================================================

-- Optional table for qualifiers and rules
-- Populate later when you extract conditions like pistol, scoped, ADS, etc.
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
  CONSTRAINT fk_wpr_weapon FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  CONSTRAINT fk_wpr_perk   FOREIGN KEY (perk_id)   REFERENCES perks(id)   ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- RAG-OPTIMIZED VIEWS FOR LLM QUERIES
-- ============================================================================

-- View: Complete weapon info with all affecting perks
CREATE OR REPLACE VIEW v_weapons_with_perks AS
SELECT
  w.id,
  w.name AS weapon_name,
  w.type AS weapon_type,
  w.class AS weapon_class,
  w.level,
  w.damage,
  GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
  GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
  w.source_url
FROM weapons w
LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
LEFT JOIN perks p ON wp.perk_id = p.id
LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
LEFT JOIN legendary_perks lp ON wlpe.legendary_perk_id = lp.id
GROUP BY w.id;

-- View: Complete armor info (includes both regular and power armor)
-- Note: Armor perks are universal and not tracked per-item
CREATE OR REPLACE VIEW v_armor_complete AS
SELECT
  a.id,
  a.name,
  a.armor_type,
  a.class,
  a.slot,
  a.set_name,
  a.level,
  a.damage_resistance,
  a.energy_resistance,
  a.radiation_resistance,
  a.cryo_resistance,
  a.fire_resistance,
  a.poison_resistance,
  a.source_url
FROM armor a;

-- View: Regular perks with all ranks
CREATE OR REPLACE VIEW v_perks_all_ranks AS
SELECT
  p.id AS perk_id,
  p.name AS perk_name,
  p.special,
  p.level AS min_level,
  p.race,
  pr.`rank`,
  pr.description AS rank_description,
  pr.form_id
FROM perks p
LEFT JOIN perk_ranks pr ON p.id = pr.perk_id
ORDER BY p.name, pr.`rank`;

-- View: Legendary perks with all ranks
CREATE OR REPLACE VIEW v_legendary_perks_all_ranks AS
SELECT
  lp.id AS legendary_perk_id,
  lp.name AS perk_name,
  lp.description AS base_description,
  lp.race,
  lpr.`rank`,
  lpr.description AS rank_description,
  lpr.effect_value,
  lpr.effect_type
FROM legendary_perks lp
LEFT JOIN legendary_perk_ranks lpr ON lp.id = lpr.legendary_perk_id
ORDER BY lp.name, lpr.`rank`;

-- ============================================================================
-- MUTATIONS TABLE
-- ============================================================================

CREATE TABLE mutations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  positive_effects TEXT,               -- Comma-separated or detailed positive effects
  negative_effects TEXT,               -- Comma-separated or detailed negative effects
  form_id CHAR(8),                     -- Game Form ID
  exclusive_with VARCHAR(128),         -- Name of mutually exclusive mutation (e.g., "Carnivore" for Herbivore)
  suppression_perk VARCHAR(128),       -- Perk that reduces negative effects (typically "Class Freak")
  enhancement_perk VARCHAR(128),       -- Perk that enhances positive effects (typically "Strange in Numbers")
  source_url TEXT,
  UNIQUE KEY uq_mutation_name (name),
  INDEX idx_mutation_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- MUTATIONS VIEW (RAG-OPTIMIZED)
-- ============================================================================

-- View: All mutations with effects
CREATE OR REPLACE VIEW v_mutations_complete AS
SELECT
  m.id AS mutation_id,
  m.name AS mutation_name,
  m.positive_effects,
  m.negative_effects,
  m.form_id,
  m.exclusive_with,
  m.suppression_perk,
  m.enhancement_perk,
  m.source_url
FROM mutations m
ORDER BY m.name;

-- ============================================================================
-- CONSUMABLES TABLE
-- ============================================================================

CREATE TABLE consumables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category ENUM('food', 'drink', 'chem', 'aid', 'alcohol', 'beverage') NOT NULL,
  subcategory VARCHAR(64),                -- 'cooked', 'raw', 'preserved', 'nuka-cola', 'stimpak', etc.
  effects TEXT,                           -- Stat buffs, healing, rad removal, etc.
  duration VARCHAR(64),                   -- Effect duration (e.g., "1 hour", "30 minutes", "instant")
  hp_restore VARCHAR(32),                 -- HP restoration amount
  rads VARCHAR(32),                       -- Radiation added/removed
  hunger_satisfaction VARCHAR(32),        -- Hunger meter fill
  thirst_satisfaction VARCHAR(32),        -- Thirst meter fill
  special_modifiers TEXT,                 -- SPECIAL stat changes (e.g., "+2 STR, -1 INT")
  addiction_risk VARCHAR(32),             -- Addiction chance (for chems)
  disease_risk VARCHAR(32),               -- Disease chance (for raw food)
  weight DECIMAL(5,2),                    -- Item weight
  value INT,                              -- Caps value
  form_id CHAR(8),                        -- Game Form ID
  crafting_station VARCHAR(64),           -- Where it's crafted (if applicable)
  source_url TEXT,
  UNIQUE KEY uq_consumable_name (name),
  INDEX idx_consumable_category (category),
  INDEX idx_consumable_subcategory (subcategory)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- CONSUMABLES VIEW (RAG-OPTIMIZED)
-- ============================================================================

-- View: All consumables with effects
CREATE OR REPLACE VIEW v_consumables_complete AS
SELECT
  c.id AS consumable_id,
  c.name AS consumable_name,
  c.category,
  c.subcategory,
  c.effects,
  c.duration,
  c.hp_restore,
  c.rads,
  c.hunger_satisfaction,
  c.thirst_satisfaction,
  c.special_modifiers,
  c.addiction_risk,
  c.disease_risk,
  c.weight,
  c.value,
  c.form_id,
  c.crafting_station,
  c.source_url
FROM consumables c
ORDER BY c.category, c.name;
