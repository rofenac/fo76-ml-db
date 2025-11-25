-- ============================================================
-- Legendary Effects Schema
-- ============================================================
-- Adds legendary weapon and armor effects to the database
-- These are RNG drop effects (Bloodied, Anti-armor, etc.)
-- NOT crafted mods
-- ============================================================

USE f76;

-- ============================================================
-- Legendary Effect Categories
-- ============================================================

CREATE TABLE IF NOT EXISTS legendary_effect_categories (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL,
    description TEXT,
    PRIMARY KEY (id),
    UNIQUE KEY uq_category_name (name),
    KEY idx_category_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT IGNORE INTO legendary_effect_categories (name, description) VALUES
('Prefix', 'Primary legendary effect (1st star)'),
('Major', 'Secondary legendary effect (2nd star)'),
('Minor', 'Tertiary legendary effect (3rd star)'),
('Additional', '4th and 5th star effects');

-- ============================================================
-- Legendary Effects (Weapon & Armor)
-- ============================================================

CREATE TABLE IF NOT EXISTS legendary_effects (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL,
    category_id INT NOT NULL,
    star_level INT NOT NULL DEFAULT 1,
    item_type ENUM('weapon', 'armor', 'both') NOT NULL DEFAULT 'weapon',
    description TEXT,
    effect_value VARCHAR(255) DEFAULT NULL,
    notes TEXT,
    form_id CHAR(8) DEFAULT NULL,
    source_url TEXT,
    PRIMARY KEY (id),
    UNIQUE KEY uq_legendary_effect (name, item_type),
    KEY idx_le_name (name),
    KEY idx_le_category (category_id),
    KEY idx_le_star_level (star_level),
    KEY idx_le_item_type (item_type),
    CONSTRAINT fk_le_category FOREIGN KEY (category_id)
        REFERENCES legendary_effect_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Legendary Effect Conditions
-- ============================================================
-- Some effects have conditions (e.g., "at night", "in VATS", "at low health")

CREATE TABLE IF NOT EXISTS legendary_effect_conditions (
    id INT NOT NULL AUTO_INCREMENT,
    effect_id INT NOT NULL,
    condition_type ENUM('health_threshold', 'time_of_day', 'combat_state', 'vats', 'aiming', 'movement', 'target_health', 'consecutive_hits', 'other') NOT NULL,
    condition_description VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    KEY idx_lec_effect (effect_id),
    KEY idx_lec_type (condition_type),
    CONSTRAINT fk_lec_effect FOREIGN KEY (effect_id)
        REFERENCES legendary_effects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================
-- Views for Legendary Effects
-- ============================================================

-- Complete view of legendary effects with categories
CREATE OR REPLACE VIEW v_legendary_effects_complete AS
SELECT
    le.id AS effect_id,
    le.name AS effect_name,
    lec.name AS category,
    le.star_level,
    le.item_type,
    le.description,
    le.effect_value,
    GROUP_CONCAT(DISTINCT CONCAT(lecon.condition_type, ': ', lecon.condition_description)
                 ORDER BY lecon.condition_type SEPARATOR '; ') AS conditions,
    le.notes,
    le.form_id,
    le.source_url
FROM legendary_effects le
JOIN legendary_effect_categories lec ON le.category_id = lec.id
LEFT JOIN legendary_effect_conditions lecon ON le.id = lecon.effect_id
GROUP BY le.id, le.name, lec.name, le.star_level, le.item_type,
         le.description, le.effect_value, le.notes, le.form_id, le.source_url
ORDER BY le.item_type, le.star_level, le.name;

-- Weapon-only legendary effects
CREATE OR REPLACE VIEW v_weapon_legendary_effects AS
SELECT * FROM v_legendary_effects_complete
WHERE item_type IN ('weapon', 'both')
ORDER BY star_level, effect_name;

-- Armor-only legendary effects
CREATE OR REPLACE VIEW v_armor_legendary_effects AS
SELECT * FROM v_legendary_effects_complete
WHERE item_type IN ('armor', 'both')
ORDER BY star_level, effect_name;

-- ============================================================
-- Sample Data (Common Legendary Effects)
-- ============================================================

-- Add some well-known effects as examples (will be replaced by scraper data)
INSERT INTO legendary_effects (name, category_id, star_level, item_type, description, effect_value) VALUES
('Bloodied', 1, 1, 'weapon', 'Damage increases as health decreases', 'Up to +95% damage at low health'),
('Anti-armor', 1, 1, 'weapon', 'Ignores armor', '50% armor penetration'),
('Two Shot', 1, 1, 'weapon', 'Shoots an additional projectile', '+100% ammo consumption, +25% damage per projectile'),
('Furious', 1, 1, 'weapon', 'Damage increased after each consecutive hit on the same target', '+5% per hit, up to +45%'),
('Unyielding', 1, 1, 'armor', 'Gain up to +3 to all stats except END when low health', '+15 total SPECIAL at low health'),
('Vanguards', 1, 1, 'armor', 'Grants up to +35 Damage and Energy Resistance the higher your health', 'Max +35 DR/ER at full health')
ON DUPLICATE KEY UPDATE description = VALUES(description);

SELECT 'Legendary effects schema created' AS status;
SELECT 'Sample effects added' AS status, COUNT(*) AS count FROM legendary_effects;
