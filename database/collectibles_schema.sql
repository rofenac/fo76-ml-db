-- ============================================================================
-- COLLECTIBLES TABLE (BOBBLEHEADS & MAGAZINES)
-- ============================================================================
-- Collectibles are distinct from consumables:
-- - Found in fixed world locations (not crafted/bought)
-- - Provide temporary buffs that can stack or extend duration
-- - Organized into series (e.g., "Guns and Bullets", "Live & Love")
-- - Limited quantity per server (respawn timers)
-- ============================================================================

-- Add to DROP section (if recreating)
-- DROP TABLE IF EXISTS collectible_special_modifiers;
-- DROP TABLE IF EXISTS collectible_effects;
-- DROP TABLE IF EXISTS collectibles;
-- DROP TABLE IF EXISTS collectible_types;
-- DROP TABLE IF EXISTS collectible_series;

-- ============================================================================
-- LOOKUP TABLES
-- ============================================================================

-- Collectible types (bobblehead or magazine)
CREATE TABLE collectible_types (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(32) NOT NULL UNIQUE,  -- 'bobblehead', 'magazine'
  INDEX idx_collectible_type_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Collectible series (Guns and Bullets, Live & Love, Astoundingly Awesome Tales, etc.)
CREATE TABLE collectible_series (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL UNIQUE,  -- 'Guns and Bullets', 'Live & Love', 'Bobbleheads'
  collectible_type_id INT NOT NULL,    -- FK to collectible_types
  description TEXT,                    -- Series description/theme
  total_issues INT,                    -- Total number in series (e.g., 10 magazines)
  FOREIGN KEY (collectible_type_id) REFERENCES collectible_types(id),
  INDEX idx_series_name (name),
  INDEX idx_series_type (collectible_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- MAIN COLLECTIBLES TABLE
-- ============================================================================

CREATE TABLE collectibles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  collectible_type_id INT NOT NULL,    -- FK to collectible_types (bobblehead/magazine)
  series_id INT,                       -- FK to collectible_series (NULL for standalone bobbleheads)
  issue_number INT,                    -- Magazine issue # (NULL for bobbleheads)
  duration_seconds INT,                -- How long the buff lasts (3600 = 1 hour)
  stacking_behavior ENUM(
    'no_stack',                        -- Cannot stack at all
    'duration_extends',                -- Same item extends duration
    'effect_stacks'                    -- Effect magnitude increases
  ) DEFAULT 'duration_extends',
  weight DECIMAL(5,2) DEFAULT 0.0,     -- Usually 0.0 for collectibles
  value INT,                           -- Vendor sell price
  form_id CHAR(8),                     -- Game ID
  source_url TEXT,                     -- Wiki URL
  spawn_locations TEXT,                -- Brief description of where to find
  UNIQUE KEY uq_collectible_name (name),
  FOREIGN KEY (collectible_type_id) REFERENCES collectible_types(id),
  FOREIGN KEY (series_id) REFERENCES collectible_series(id) ON DELETE SET NULL,
  INDEX idx_collectible_type (collectible_type_id),
  INDEX idx_collectible_series (series_id),
  INDEX idx_collectible_issue (issue_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- COLLECTIBLE EFFECTS (NORMALIZED)
-- ============================================================================

-- Collectible effects (normalized from effects TEXT)
CREATE TABLE collectible_effects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  collectible_id INT NOT NULL,
  effect_type_id INT NOT NULL,         -- FK to effect_types
  value DECIMAL(10,2),                 -- Effect magnitude (e.g., 20 for +20%)
  description TEXT,                    -- Human-readable effect description
  FOREIGN KEY (collectible_id) REFERENCES collectibles(id) ON DELETE CASCADE,
  FOREIGN KEY (effect_type_id) REFERENCES effect_types(id),
  INDEX idx_ceff_collectible (collectible_id),
  INDEX idx_ceff_type (effect_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Collectible SPECIAL modifiers (normalized from special_modifiers TEXT)
CREATE TABLE collectible_special_modifiers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  collectible_id INT NOT NULL,
  special_id INT NOT NULL,             -- FK to special_attributes (S/P/E/C/I/A/L)
  modifier INT NOT NULL,               -- Modifier value (can be negative)
  FOREIGN KEY (collectible_id) REFERENCES collectibles(id) ON DELETE CASCADE,
  FOREIGN KEY (special_id) REFERENCES special_attributes(id),
  INDEX idx_csm_collectible (collectible_id),
  INDEX idx_csm_special (special_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================================
-- SEED DATA FOR LOOKUP TABLES
-- ============================================================================

INSERT INTO collectible_types (name) VALUES
  ('bobblehead'),
  ('magazine');

INSERT INTO collectible_series (name, collectible_type_id, description, total_issues) VALUES
  -- Magazines
  ('Guns and Bullets', 2, 'Weapon damage and accuracy bonuses', 10),
  ('Live & Love', 2, 'Team and social bonuses', 9),
  ('Astoundingly Awesome Tales', 2, 'Various combat and exploration bonuses', 14),
  ('Backwoodsman', 2, 'Outdoor survival and melee bonuses', 10),
  ('Grognak the Barbarian', 2, 'Melee damage bonuses', 10),
  ('Scouts'' Life', 2, 'Survival and crafting bonuses', 10),
  ('Tales from the West Virginia Hills', 2, 'Creature-specific damage bonuses', 10),
  ('Tesla Science', 2, 'Energy weapon bonuses', 9),
  ('Tumblers Today', 2, 'Lockpicking and hacking bonuses', 5),
  ('U.S. Covert Operations Manual', 2, 'Stealth and sneaking bonuses', 10),
  ('Unstoppables', 2, 'Damage resistance and survival bonuses', 5),
  -- Bobbleheads (single series)
  ('Bobbleheads', 1, 'Temporary stat and skill bonuses', 20);

-- ============================================================================
-- RAG-OPTIMIZED VIEW
-- ============================================================================

CREATE OR REPLACE VIEW v_collectibles_complete AS
SELECT
  c.id AS collectible_id,
  c.name AS collectible_name,
  ct.name AS collectible_type,
  cs.name AS series_name,
  c.issue_number,
  c.duration_seconds,
  -- Format duration as human-readable
  CASE
    WHEN c.duration_seconds >= 3600 THEN CONCAT(c.duration_seconds / 3600, ' hour(s)')
    WHEN c.duration_seconds >= 60 THEN CONCAT(c.duration_seconds / 60, ' minute(s)')
    ELSE CONCAT(c.duration_seconds, ' second(s)')
  END AS duration,
  c.stacking_behavior,
  -- Aggregate all effects into a readable string
  GROUP_CONCAT(DISTINCT
    CONCAT(et.name, ': ', ce.description)
    ORDER BY et.name
    SEPARATOR '; '
  ) AS effects,
  -- Aggregate SPECIAL modifiers
  GROUP_CONCAT(DISTINCT
    CONCAT(
      CASE WHEN csm.modifier > 0 THEN '+' ELSE '' END,
      csm.modifier, ' ', sa.name
    )
    ORDER BY sa.name
    SEPARATOR ', '
  ) AS special_modifiers,
  c.weight,
  c.value,
  c.form_id,
  c.spawn_locations,
  c.source_url
FROM collectibles c
LEFT JOIN collectible_types ct ON c.collectible_type_id = ct.id
LEFT JOIN collectible_series cs ON c.series_id = cs.id
LEFT JOIN collectible_effects ce ON c.id = ce.collectible_id
LEFT JOIN effect_types et ON ce.effect_type_id = et.id
LEFT JOIN collectible_special_modifiers csm ON c.id = csm.collectible_id
LEFT JOIN special_attributes sa ON csm.special_id = sa.id
GROUP BY
  c.id,
  c.name,
  ct.name,
  cs.name,
  c.issue_number,
  c.duration_seconds,
  c.stacking_behavior,
  c.weight,
  c.value,
  c.form_id,
  c.spawn_locations,
  c.source_url;

-- ============================================================================
-- EXAMPLE QUERIES
-- ============================================================================

-- Find all Guns and Bullets magazines
-- SELECT * FROM v_collectibles_complete WHERE series_name = 'Guns and Bullets';

-- Find all bobbleheads
-- SELECT * FROM v_collectibles_complete WHERE collectible_type = 'bobblehead';

-- Find collectibles that boost specific SPECIAL stat
-- SELECT * FROM v_collectibles_complete WHERE special_modifiers LIKE '%STR%';

-- Find collectibles with damage bonuses
-- SELECT * FROM v_collectibles_complete WHERE effects LIKE '%damage%';
