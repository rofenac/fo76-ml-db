-- ============================================================================
-- TEST QUERIES FOR WEAPON MECHANICS
-- ============================================================================
-- This file contains test queries to verify the weapon mechanics system
-- Run these after importing mechanics to validate the data
-- ============================================================================

USE f76;

-- ============================================================================
-- VERIFICATION TESTS
-- ============================================================================

-- Test 1: Check if mechanic types were created
SELECT '=== Test 1: Mechanic Types ===' AS test;
SELECT id, name, LEFT(description, 60) AS description
FROM weapon_mechanic_types
ORDER BY name;

-- Test 2: Count weapons by mechanic type
SELECT '=== Test 2: Weapons per Mechanic Type ===' AS test;
SELECT
    wmt.name AS mechanic_type,
    COUNT(DISTINCT w.id) AS weapon_count,
    GROUP_CONCAT(DISTINCT w.name ORDER BY w.name SEPARATOR ', ') AS weapons
FROM weapon_mechanics wm
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
JOIN weapons w ON wm.weapon_id = w.id
GROUP BY wmt.name
ORDER BY weapon_count DESC;

-- Test 3: Gauss weapons with charge mechanic (should be 3, NOT including Gauss minigun)
SELECT '=== Test 3: Gauss Weapons with Charge Mechanic (3 weapons) ===' AS test;
SELECT
    w.name AS weapon_name,
    wmt.name AS mechanic_type,
    wm.numeric_value,
    wm.unit,
    LEFT(wm.notes, 80) AS notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
WHERE w.name LIKE 'Gauss%' AND wmt.name = 'charge'
ORDER BY w.name;

-- Test 4: Verify Gauss rifle has BOTH charge and explosive_aoe
SELECT '=== Test 4: Gauss Rifle Mechanics (should have 2) ===' AS test;
SELECT
    w.name AS weapon_name,
    wmt.name AS mechanic_type,
    wm.numeric_value,
    wm.string_value,
    LEFT(wm.notes, 60) AS notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
WHERE w.name = 'Gauss rifle'
ORDER BY wmt.name;

-- Test 5: Tesla rifle chain lightning
SELECT '=== Test 5: Tesla Rifle Chain Lightning ===' AS test;
SELECT
    w.name AS weapon_name,
    wmt.name AS mechanic_type,
    wm.numeric_value AS first_chain_multiplier,
    wm.numeric_value_2 AS damage_reduction_per_hop,
    wm.unit,
    ROUND(wm.numeric_value * wm.numeric_value, 4) AS second_chain_multiplier,
    LEFT(wm.notes, 80) AS notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
WHERE w.name = 'Tesla rifle' AND wmt.name = 'chain_lightning';

-- Test 6: All weapons with spin-up mechanic (should include Gauss minigun and Pepper Shaker)
SELECT '=== Test 6: Weapons with Spin-Up Delay (7 weapons) ===' AS test;
SELECT
    w.name AS weapon_name,
    wc.name AS weapon_class,
    wm.notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
WHERE wmt.name = 'spin_up'
ORDER BY w.name;

-- Test 7: Explosive AOE weapons
SELECT '=== Test 7: Weapons with Explosive AOE ===' AS test;
SELECT
    w.name AS weapon_name,
    wc.name AS weapon_class,
    wm.string_value AS damage_type,
    LEFT(wm.notes, 60) AS notes
FROM weapons w
JOIN weapon_mechanics wm ON w.id = wm.weapon_id
JOIN weapon_mechanic_types wmt ON wm.mechanic_type_id = wmt.id
LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
WHERE wmt.name = 'explosive_aoe'
ORDER BY w.name;

-- Test 8: Using the view
SELECT '=== Test 8: View Test (Gauss weapons) ===' AS test;
SELECT
    weapon_name,
    mechanic_type,
    numeric_value,
    numeric_value_2,
    string_value,
    unit,
    LEFT(mechanic_notes, 60) AS notes
FROM v_weapons_with_mechanics
WHERE weapon_name LIKE 'Gauss%'
ORDER BY weapon_name, mechanic_type;

-- Test 9: Check for duplicate mechanics (should be 0)
SELECT '=== Test 9: Duplicate Mechanics Check (should be 0) ===' AS test;
SELECT
    weapon_id,
    mechanic_type_id,
    COUNT(*) AS duplicate_count
FROM weapon_mechanics
GROUP BY weapon_id, mechanic_type_id
HAVING COUNT(*) > 1;

-- Test 10: Summary statistics
SELECT '=== Test 10: Summary Statistics ===' AS test;
SELECT
    'Total mechanic types' AS metric,
    COUNT(*) AS value
FROM weapon_mechanic_types
UNION ALL
SELECT
    'Total weapon-mechanic mappings',
    COUNT(*)
FROM weapon_mechanics
UNION ALL
SELECT
    'Weapons with at least one mechanic',
    COUNT(DISTINCT weapon_id)
FROM weapon_mechanics
UNION ALL
SELECT
    'Weapons with multiple mechanics',
    COUNT(*)
FROM (
    SELECT weapon_id
    FROM weapon_mechanics
    GROUP BY weapon_id
    HAVING COUNT(*) > 1
) AS multi_mechanic_weapons;

-- ============================================================================
-- EXPECTED RESULTS SUMMARY
-- ============================================================================
/*
Expected results (if all weapons are imported):

Test 1: Should show 7 mechanic types
Test 2: Should show distribution of mechanics across weapons
Test 3: Should show 3 Gauss weapons with numeric_value = 0.50, unit = 'multiplier'
        (Gauss rifle, Gauss shotgun, Gauss pistol - NOT Gauss minigun!)
Test 4: Gauss rifle should have BOTH 'charge' and 'explosive_aoe' (2 rows)
Test 5: Tesla rifle should show chain_lightning with numeric_value = 0.65,
        numeric_value_2 = 0.35, second_chain = 0.4225
Test 6: Should show 7 weapons with spin-up:
        (Minigun, Gauss minigun, Gatling gun, Gatling laser, Gatling plasma, Ultracite Gatling laser, Pepper Shaker)
Test 7: Should show multiple explosive weapons (Gauss rifle, Fat Man, etc.)
Test 8: View should work and show same data as direct queries
Test 9: Should return 0 rows (no duplicates)
Test 10: Should show:
         - 7 mechanic types
         - Multiple weapon-mechanic mappings
         - Several weapons with mechanics
         - At least 1 weapon with multiple mechanics (Gauss rifle)
*/
