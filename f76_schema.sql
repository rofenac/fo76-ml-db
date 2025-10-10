USE f76;

-- ============================================================================
-- DROP ALL TABLES (CLEAN SLATE)
-- ============================================================================

DROP TABLE IF EXISTS weapon_perk_rules;
DROP TABLE IF EXISTS power_armor_legendary_perk_effects;
DROP TABLE IF EXISTS power_armor_perks;
DROP TABLE IF EXISTS armor_legendary_perk_effects;
DROP TABLE IF EXISTS armor_perks;
DROP TABLE IF EXISTS weapon_legendary_perk_effects;
DROP TABLE IF EXISTS weapon_perks;
DROP TABLE IF EXISTS legendary_perk_ranks;
DROP TABLE IF EXISTS perk_ranks;
DROP TABLE IF EXISTS legendary_perks;
DROP TABLE IF EXISTS perks;
DROP TABLE IF EXISTS power_armor;
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
  damage VARCHAR(64),
  projectile VARCHAR(128),
  form_id CHAR(8),
  editor_id VARCHAR(128),
  perks_raw TEXT,
  source_url TEXT,
  UNIQUE KEY uq_weapon_name (name),
  INDEX idx_weapons_form (form_id),
  INDEX idx_weapons_type (type),
  INDEX idx_weapons_class (class)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- ARMOR TABLES
-- ============================================================================

CREATE TABLE armor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(64),                    -- "Light", "Sturdy", "Heavy", "Outfit", etc.
  slot VARCHAR(64),                    -- "Chest", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Helmet"
  armor_rating VARCHAR(64),
  energy_resistance VARCHAR(64),
  radiation_resistance VARCHAR(64),
  set_name VARCHAR(128),               -- Armor set name (for matching set bonuses)
  level VARCHAR(64),
  weight VARCHAR(64),
  value VARCHAR(64),
  form_id CHAR(8),
  editor_id VARCHAR(128),
  perks_raw TEXT,
  source_url TEXT,
  UNIQUE KEY uq_armor_name (name),
  INDEX idx_armor_set (set_name),
  INDEX idx_armor_slot (slot),
  INDEX idx_armor_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- POWER ARMOR TABLES
-- ============================================================================

CREATE TABLE power_armor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(64),                    -- "Frame", "Torso", "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Helmet"
  set_name VARCHAR(128),               -- Power armor set (T-45, T-51, T-60, X-01, Ultracite, etc.)
  armor_rating VARCHAR(64),
  energy_resistance VARCHAR(64),
  radiation_resistance VARCHAR(64),
  level VARCHAR(64),
  weight VARCHAR(64),
  value VARCHAR(64),
  durability VARCHAR(64),
  fusion_core_drain VARCHAR(128),      -- For frames: AP drain rate
  form_id CHAR(8),
  editor_id VARCHAR(128),
  perks_raw TEXT,
  source_url TEXT,
  UNIQUE KEY uq_pa_name (name),
  INDEX idx_pa_set (set_name),
  INDEX idx_pa_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
-- ARMOR PERK JUNCTION TABLES
-- ============================================================================

-- Armor to regular perks that can affect them
CREATE TABLE armor_perks (
  armor_id INT NOT NULL,
  perk_id INT NOT NULL,
  PRIMARY KEY (armor_id, perk_id),
  CONSTRAINT fk_ap_armor FOREIGN KEY (armor_id) REFERENCES armor(id) ON DELETE CASCADE,
  CONSTRAINT fk_ap_perk  FOREIGN KEY (perk_id)  REFERENCES perks(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Armor to legendary perks that can affect them
CREATE TABLE armor_legendary_perk_effects (
  armor_id INT NOT NULL,
  legendary_perk_id INT NOT NULL,
  PRIMARY KEY (armor_id, legendary_perk_id),
  CONSTRAINT fk_alpe_armor FOREIGN KEY (armor_id) REFERENCES armor(id) ON DELETE CASCADE,
  CONSTRAINT fk_alpe_perk  FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- POWER ARMOR PERK JUNCTION TABLES
-- ============================================================================

-- Power armor to regular perks that can affect them
CREATE TABLE power_armor_perks (
  power_armor_id INT NOT NULL,
  perk_id INT NOT NULL,
  PRIMARY KEY (power_armor_id, perk_id),
  CONSTRAINT fk_pap_pa   FOREIGN KEY (power_armor_id) REFERENCES power_armor(id) ON DELETE CASCADE,
  CONSTRAINT fk_pap_perk FOREIGN KEY (perk_id)        REFERENCES perks(id)       ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Power armor to legendary perks that can affect them
CREATE TABLE power_armor_legendary_perk_effects (
  power_armor_id INT NOT NULL,
  legendary_perk_id INT NOT NULL,
  PRIMARY KEY (power_armor_id, legendary_perk_id),
  CONSTRAINT fk_palpe_pa   FOREIGN KEY (power_armor_id)   REFERENCES power_armor(id)     ON DELETE CASCADE,
  CONSTRAINT fk_palpe_perk FOREIGN KEY (legendary_perk_id) REFERENCES legendary_perks(id) ON DELETE CASCADE
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
  w.damage,
  w.projectile,
  w.form_id,
  w.editor_id,
  GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
  GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
  w.source_url
FROM weapons w
LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
LEFT JOIN perks p ON wp.perk_id = p.id
LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
LEFT JOIN legendary_perks lp ON wlpe.legendary_perk_id = lp.id
GROUP BY w.id;

-- View: Complete armor info with all affecting perks
CREATE OR REPLACE VIEW v_armor_with_perks AS
SELECT
  a.id,
  a.name AS armor_name,
  a.type AS armor_type,
  a.slot AS armor_slot,
  a.set_name,
  a.armor_rating,
  a.energy_resistance,
  a.radiation_resistance,
  GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
  GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
  a.source_url
FROM armor a
LEFT JOIN armor_perks ap ON a.id = ap.armor_id
LEFT JOIN perks p ON ap.perk_id = p.id
LEFT JOIN armor_legendary_perk_effects alpe ON a.id = alpe.armor_id
LEFT JOIN legendary_perks lp ON alpe.legendary_perk_id = lp.id
GROUP BY a.id;

-- View: Power armor with all affecting perks
CREATE OR REPLACE VIEW v_power_armor_with_perks AS
SELECT
  pa.id,
  pa.name AS pa_name,
  pa.type AS pa_type,
  pa.set_name,
  pa.armor_rating,
  pa.energy_resistance,
  pa.radiation_resistance,
  GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
  GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
  pa.source_url
FROM power_armor pa
LEFT JOIN power_armor_perks pap ON pa.id = pap.power_armor_id
LEFT JOIN perks p ON pap.perk_id = p.id
LEFT JOIN power_armor_legendary_perk_effects palpe ON pa.id = palpe.power_armor_id
LEFT JOIN legendary_perks lp ON palpe.legendary_perk_id = lp.id
GROUP BY pa.id;

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
