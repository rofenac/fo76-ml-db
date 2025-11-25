-- ============================================================
-- 3NF Normalization Migration
-- ============================================================
-- This script removes transitive dependencies and normalizes
-- the f76 database to Third Normal Form (3NF)
-- ============================================================

USE f76;

-- Disable foreign key checks temporarily for migration
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- PHASE 1: Populate Lookup Tables
-- ============================================================

-- Populate races table from perks data
INSERT IGNORE INTO races (name)
SELECT DISTINCT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(race, ',', numbers.n), ',', -1)) AS race_name
FROM perks
CROSS JOIN (
    SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3
) AS numbers
WHERE race IS NOT NULL
  AND CHAR_LENGTH(race) - CHAR_LENGTH(REPLACE(race, ',', '')) >= numbers.n - 1
ORDER BY race_name;

-- Add more races from legendary_perks if any
INSERT IGNORE INTO races (name)
SELECT DISTINCT TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(race, ',', numbers.n), ',', -1)) AS race_name
FROM legendary_perks
CROSS JOIN (
    SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3
) AS numbers
WHERE race IS NOT NULL
  AND CHAR_LENGTH(race) - CHAR_LENGTH(REPLACE(race, ',', '')) >= numbers.n - 1
ORDER BY race_name;

-- Populate special_attributes table if empty
INSERT IGNORE INTO special_attributes (code, name) VALUES
('S', 'Strength'),
('P', 'Perception'),
('E', 'Endurance'),
('C', 'Charisma'),
('I', 'Intelligence'),
('A', 'Agility'),
('L', 'Luck');

-- ============================================================
-- PHASE 2: Add Foreign Key Columns Where Needed
-- ============================================================

-- Add special_id to perks table
ALTER TABLE perks
ADD COLUMN special_id INT DEFAULT NULL AFTER special,
ADD KEY idx_perk_special_id (special_id),
ADD CONSTRAINT fk_perk_special FOREIGN KEY (special_id)
    REFERENCES special_attributes(id) ON DELETE SET NULL;

-- Update special_id from special code
UPDATE perks p
JOIN special_attributes sa ON p.special = sa.code
SET p.special_id = sa.id
WHERE p.special IS NOT NULL;

-- ============================================================
-- PHASE 3: Normalize Mutations Table
-- ============================================================

-- Create mutation_effects table for normalized effects
CREATE TABLE IF NOT EXISTS mutation_effects (
    id INT NOT NULL AUTO_INCREMENT,
    mutation_id INT NOT NULL,
    effect_type ENUM('positive', 'negative') NOT NULL,
    description TEXT NOT NULL,
    PRIMARY KEY (id),
    KEY idx_me_mutation (mutation_id),
    KEY idx_me_type (effect_type),
    CONSTRAINT fk_me_mutation FOREIGN KEY (mutation_id)
        REFERENCES mutations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Migrate positive effects
INSERT INTO mutation_effects (mutation_id, effect_type, description)
SELECT id, 'positive', positive_effects
FROM mutations
WHERE positive_effects IS NOT NULL AND positive_effects != '';

-- Migrate negative effects
INSERT INTO mutation_effects (mutation_id, effect_type, description)
SELECT id, 'negative', negative_effects
FROM mutations
WHERE negative_effects IS NOT NULL AND negative_effects != '';

-- Add FK columns for perks in mutations table
ALTER TABLE mutations
ADD COLUMN suppression_perk_id INT DEFAULT NULL AFTER suppression_perk,
ADD COLUMN enhancement_perk_id INT DEFAULT NULL AFTER enhancement_perk,
ADD KEY idx_mutation_suppression (suppression_perk_id),
ADD KEY idx_mutation_enhancement (enhancement_perk_id),
ADD CONSTRAINT fk_mutation_suppression FOREIGN KEY (suppression_perk_id)
    REFERENCES perks(id) ON DELETE SET NULL,
ADD CONSTRAINT fk_mutation_enhancement FOREIGN KEY (enhancement_perk_id)
    REFERENCES perks(id) ON DELETE SET NULL;

-- Update FK values from perk names
UPDATE mutations m
LEFT JOIN perks p ON m.suppression_perk = p.name
SET m.suppression_perk_id = p.id
WHERE m.suppression_perk IS NOT NULL;

UPDATE mutations m
LEFT JOIN perks p ON m.enhancement_perk = p.name
SET m.enhancement_perk_id = p.id
WHERE m.enhancement_perk IS NOT NULL;

-- Add self-referencing FK for exclusive mutations
ALTER TABLE mutations
ADD COLUMN exclusive_with_id INT DEFAULT NULL AFTER exclusive_with,
ADD KEY idx_mutation_exclusive (exclusive_with_id),
ADD CONSTRAINT fk_mutation_exclusive FOREIGN KEY (exclusive_with_id)
    REFERENCES mutations(id) ON DELETE SET NULL;

-- Update exclusive_with_id from name
UPDATE mutations m1
LEFT JOIN mutations m2 ON m1.exclusive_with = m2.name
SET m1.exclusive_with_id = m2.id
WHERE m1.exclusive_with IS NOT NULL;

-- ============================================================
-- PHASE 4: Remove Redundant Columns (3NF Violations)
-- ============================================================

-- Drop redundant columns from weapons table
ALTER TABLE weapons
DROP COLUMN type,
DROP COLUMN class,
DROP INDEX idx_weapons_type,
DROP INDEX idx_weapons_class;

-- Drop redundant columns from armor table
ALTER TABLE armor
DROP COLUMN class,
DROP COLUMN slot,
DROP COLUMN armor_type,
DROP INDEX idx_armor_slot,
DROP INDEX idx_armor_class,
DROP INDEX idx_armor_type;

-- Drop redundant columns from perks table
-- Keep 'special' for backward compatibility but it's now denormalized
-- In the future, can drop it after all queries use special_id

-- Drop redundant text columns from mutations table
-- Keep for backward compatibility initially
-- ALTER TABLE mutations
-- DROP COLUMN positive_effects,
-- DROP COLUMN negative_effects,
-- DROP COLUMN exclusive_with,
-- DROP COLUMN suppression_perk,
-- DROP COLUMN enhancement_perk;

-- ============================================================
-- PHASE 5: Update Views to Use Normalized Schema
-- ============================================================

-- Recreate v_weapons_with_perks view
DROP VIEW IF EXISTS v_weapons_with_perks;
CREATE VIEW v_weapons_with_perks AS
SELECT
    w.id,
    w.name AS weapon_name,
    wt.name AS weapon_type,
    wc.name AS weapon_class,
    w.level,
    w.damage,
    GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR '; ') AS regular_perks,
    GROUP_CONCAT(DISTINCT lp.name ORDER BY lp.name SEPARATOR '; ') AS legendary_perks,
    w.source_url
FROM weapons w
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
LEFT JOIN weapon_perks wp ON w.id = wp.weapon_id
LEFT JOIN perks p ON wp.perk_id = p.id
LEFT JOIN weapon_legendary_perk_effects wlpe ON w.id = wlpe.weapon_id
LEFT JOIN legendary_perks lp ON wlpe.legendary_perk_id = lp.id
GROUP BY w.id, w.name, wt.name, wc.name, w.level, w.damage, w.source_url
ORDER BY w.name;

-- Recreate v_mutations_complete view with normalized data
DROP VIEW IF EXISTS v_mutations_complete;
CREATE VIEW v_mutations_complete AS
SELECT
    m.id AS mutation_id,
    m.name AS mutation_name,
    GROUP_CONCAT(DISTINCT CASE WHEN me.effect_type = 'positive' THEN me.description END SEPARATOR '; ') AS positive_effects,
    GROUP_CONCAT(DISTINCT CASE WHEN me.effect_type = 'negative' THEN me.description END SEPARATOR '; ') AS negative_effects,
    m.form_id,
    m2.name AS exclusive_with,
    ps.name AS suppression_perk,
    pe.name AS enhancement_perk,
    m.source_url
FROM mutations m
LEFT JOIN mutation_effects me ON m.id = me.mutation_id
LEFT JOIN mutations m2 ON m.exclusive_with_id = m2.id
LEFT JOIN perks ps ON m.suppression_perk_id = ps.id
LEFT JOIN perks pe ON m.enhancement_perk_id = pe.id
GROUP BY m.id, m.name, m.form_id, m2.name, ps.name, pe.name, m.source_url
ORDER BY m.name;

-- Create new view for perks with special attribute names
DROP VIEW IF EXISTS v_perks_all_ranks;
CREATE VIEW v_perks_all_ranks AS
SELECT
    p.id AS perk_id,
    p.name AS perk_name,
    sa.name AS special_attribute,
    p.special AS special_code,
    p.level AS min_level,
    p.race,
    pr.rank,
    pr.description AS rank_description,
    pr.form_id
FROM perks p
LEFT JOIN special_attributes sa ON p.special_id = sa.id
LEFT JOIN perk_ranks pr ON p.id = pr.perk_id
ORDER BY p.name, pr.rank;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- PHASE 6: Create Indexes for Optimized Queries
-- ============================================================

-- Add composite indexes for common query patterns
CREATE INDEX idx_weapon_type_class ON weapons(weapon_type_id, weapon_class_id);
CREATE INDEX idx_armor_type_class_slot ON armor(armor_type_id, armor_class_id, armor_slot_id);
CREATE INDEX idx_mutation_effects_type ON mutation_effects(mutation_id, effect_type);

-- ============================================================
-- Verification Queries
-- ============================================================

SELECT '=== 3NF NORMALIZATION COMPLETE ===' AS status;

SELECT 'Races populated' AS check_name, COUNT(*) AS count FROM races;
SELECT 'Special attributes populated' AS check_name, COUNT(*) AS count FROM special_attributes;
SELECT 'Mutation effects migrated' AS check_name, COUNT(*) AS count FROM mutation_effects;
SELECT 'Perks with special_id' AS check_name, COUNT(*) AS count FROM perks WHERE special_id IS NOT NULL;

-- Show sample normalized data
SELECT 'Sample weapons (normalized)' AS dataset;
SELECT w.name, wt.name AS type, wc.name AS class
FROM weapons w
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
LIMIT 5;

SELECT 'Sample mutations (normalized)' AS dataset;
SELECT * FROM v_mutations_complete LIMIT 3;
