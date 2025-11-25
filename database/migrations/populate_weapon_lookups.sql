-- ============================================================
-- Populate Weapon Lookup Tables and FKs
-- ============================================================
-- This script populates weapon_types and weapon_classes tables
-- and updates the FKs in the weapons table
-- ============================================================

USE f76;

-- First, we need to restore the type/class data temporarily to migrate it
-- Add temporary columns
ALTER TABLE weapons
ADD COLUMN temp_type VARCHAR(64) DEFAULT NULL,
ADD COLUMN temp_class VARCHAR(64) DEFAULT NULL;

-- Restore data from perks_raw or use common patterns
-- We'll need to infer from weapon names and existing data patterns

-- Populate weapon_types lookup table with common FO76 types
INSERT IGNORE INTO weapon_types (name) VALUES
('Ranged'),
('Melee'),
('Thrown'),
('Heavy'),
('Explosive');

-- Populate weapon_classes lookup table with common FO76 classes
INSERT IGNORE INTO weapon_classes (name) VALUES
('Pistol'),
('Rifle'),
('Shotgun'),
('Heavy Gun'),
('Automatic Rifle'),
('Non-automatic Rifle'),
('Automatic Pistol'),
('Non-automatic Pistol'),
('Automatic Heavy Gun'),
('One-Handed Melee'),
('Two-Handed Melee'),
('Unarmed'),
('Bow'),
('Crossbow'),
('Grenade'),
('Mine'),
('Thrown Weapon');

-- Update temp columns based on weapon names and patterns
-- Pistols
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Non-automatic Pistol'
WHERE name LIKE '%pistol%'
  AND name NOT LIKE '%submachine%'
  AND name NOT LIKE '%10mm submachine%';

UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Automatic Pistol'
WHERE name IN ('10mm submachine gun', 'Submachine gun');

-- Rifles
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Non-automatic Rifle'
WHERE (name LIKE '%rifle%' OR name LIKE '%carbine%')
  AND name NOT LIKE '%assault rifle%'
  AND name NOT LIKE '%submachine%'
  AND temp_class IS NULL;

UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Automatic Rifle'
WHERE name IN ('Assault rifle', 'Handmade rifle', 'Combat rifle', 'Radium rifle', 'Railway rifle')
   OR (name LIKE '%assault%' AND name LIKE '%rifle%');

-- Shotguns
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Shotgun'
WHERE name LIKE '%shotgun%';

-- Heavy Guns
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Heavy Gun'
WHERE name LIKE '%machine gun%'
   OR name LIKE '%minigun%'
   OR name LIKE '%gatling%'
   OR name LIKE '%flamer%'
   OR name IN ('Cryolator', 'Harpoon gun', 'Broadsider');

-- Explosive
UPDATE weapons SET temp_type = 'Explosive', temp_class = 'Grenade'
WHERE name LIKE '%grenade%';

UPDATE weapons SET temp_type = 'Explosive', temp_class = 'Mine'
WHERE name LIKE '%mine%';

UPDATE weapons SET temp_type = 'Explosive', temp_class = 'Heavy Gun'
WHERE name LIKE '%launcher%';

-- Melee Weapons
UPDATE weapons SET temp_type = 'Melee', temp_class = 'Two-Handed Melee'
WHERE name IN ('Super sledge', 'Sledgehammer', 'Fire axe', 'Baseball bat',
               'Pool cue', 'Grognak''s axe', 'Sheepsquatch staff', 'War drum',
               'Chainsaw', 'Mr. Handy buzz blade', 'Ripper', 'Auto axe', 'Drill');

UPDATE weapons SET temp_type = 'Melee', temp_class = 'One-Handed Melee'
WHERE name IN ('Combat knife', 'Switchblade', 'Machete', 'Bowie knife',
               'Cultist blade', 'Chinese officer sword', 'Ski sword', 'Revolutionary sword',
               'Shishkebab', 'Bone club', 'Lead pipe', 'Pipe wrench', 'Walking cane',
               'Rolling pin');

UPDATE weapons SET temp_type = 'Melee', temp_class = 'Unarmed'
WHERE name IN ('Power fist', 'Deathclaw gauntlet', 'Mole miner gauntlet',
               'Meat hook', 'Knuckles', 'Boxing glove', 'Bear Arm', 'Gauntlet');

-- Bows
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Bow'
WHERE name LIKE '%bow%' AND name NOT LIKE '%cross%';

UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Crossbow'
WHERE name LIKE '%crossbow%';

-- Energy weapons default to Rifle
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Rifle'
WHERE (name LIKE '%laser%' OR name LIKE '%plasma%' OR name LIKE '%gamma%')
  AND temp_class IS NULL;

-- Default remaining ranged weapons to Non-automatic Rifle
UPDATE weapons SET temp_type = 'Ranged', temp_class = 'Non-automatic Rifle'
WHERE temp_type IS NULL
  AND (name LIKE '%gun%' OR name LIKE '%blaster%');

-- Update FKs from temp columns
UPDATE weapons w
JOIN weapon_types wt ON w.temp_type = wt.name
SET w.weapon_type_id = wt.id
WHERE w.temp_type IS NOT NULL;

UPDATE weapons w
JOIN weapon_classes wc ON w.temp_class = wc.name
SET w.weapon_class_id = wc.id
WHERE w.temp_class IS NOT NULL;

-- Drop temporary columns
ALTER TABLE weapons
DROP COLUMN temp_type,
DROP COLUMN temp_class;

-- Verification
SELECT 'Weapon types populated' AS check_name, COUNT(*) AS count FROM weapon_types;
SELECT 'Weapon classes populated' AS check_name, COUNT(*) AS count FROM weapon_classes;
SELECT 'Weapons with type_id' AS check_name, COUNT(*) AS count FROM weapons WHERE weapon_type_id IS NOT NULL;
SELECT 'Weapons with class_id' AS check_name, COUNT(*) AS count FROM weapons WHERE weapon_class_id IS NOT NULL;

-- Sample data
SELECT 'Sample weapons with types/classes' AS dataset;
SELECT w.name, wt.name AS type, wc.name AS class
FROM weapons w
LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
LIMIT 10;
