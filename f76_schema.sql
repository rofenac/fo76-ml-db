USE f76;

-- Core table that matches your CSV exactly
CREATE TABLE weapons (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(64),
  projectile VARCHAR(128),
  form_id CHAR(8),
  editor_id VARCHAR(128),
  perks_raw TEXT,
  source_url TEXT,
  UNIQUE KEY uq_weapon_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Canonical perk names
CREATE TABLE perks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  UNIQUE KEY uq_perk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Simple many to many between weapons and perks
-- This captures that a perk applies to a weapon, no qualifiers yet
CREATE TABLE weapon_perks (
  weapon_id INT NOT NULL,
  perk_id INT NOT NULL,
  PRIMARY KEY (weapon_id, perk_id),
  CONSTRAINT fk_wp_weapon FOREIGN KEY (weapon_id) REFERENCES weapons(id) ON DELETE CASCADE,
  CONSTRAINT fk_wp_perk   FOREIGN KEY (perk_id)   REFERENCES perks(id)   ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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

-- Helpful indexes
CREATE INDEX ix_weapons_form ON weapons(form_id);
CREATE INDEX ix_weapons_type ON weapons(type);

