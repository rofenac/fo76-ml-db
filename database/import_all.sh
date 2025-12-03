#!/bin/bash
# Master import script - restores all data to NORMALIZED database
# 
# NOTE: Database now uses normalized schema with lookup tables:
#   - weapon_types, weapon_classes (FK from weapons table)
#   - armor_types, armor_classes, armor_slots (FK from armor table)
#   - Old VARCHAR fields remain for backward compatibility
#   - Views use FK joins for optimal performance

set -e  # Exit on error

# Check if .env exists
if [ ! -f .env ]; then
  echo "Error: .env file not found in project root"
  echo "Please create a .env file with DB_USER, DB_PASSWORD, DB_NAME, and DB_HOST"
  exit 1
fi

set -a
source .env
set +a

echo "=========================================="
echo "MASTER DATA IMPORT - RESTORING ALL DATA"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

echo "[1/10] Importing Perks..."
source .venv/bin/activate && python database/import_perks.py
echo "✓ Perks imported"
echo ""

echo "[2/10] Importing Legendary Perks..."
source .venv/bin/activate && python database/import_legendary_perks.py
echo "✓ Legendary Perks imported"
echo ""

echo "[3/10] Importing Weapons..."
source .venv/bin/activate && python database/import_weapons.py
echo "✓ Weapons imported"
echo ""

echo "[4/10] Importing Armor..."
source .venv/bin/activate && python database/import_armor.py
echo "✓ Armor imported"
echo ""

echo "[5/10] Importing Weapon Mods..."
source .venv/bin/activate && python database/import_weapon_mods.py
echo "✓ Weapon Mods imported"
echo ""

echo "[6/10] Importing Weapon Mechanics..."
source .venv/bin/activate && python database/import_weapon_mechanics.py
echo "✓ Weapon Mechanics imported"
echo ""

echo "[7/10] Importing Legendary Effects..."
source .venv/bin/activate && python database/import_legendary_effects.py
echo "✓ Legendary Effects imported"
echo ""

echo "[8/10] Importing Mutations..."
source .venv/bin/activate && python database/import_mutations.py
echo "✓ Mutations imported"
echo ""

echo "[9/10] Importing Consumables..."
source .venv/bin/activate && python database/import_consumables.py
echo "✓ Consumables imported"
echo ""

echo "[10/10] Importing Collectibles..."
source .venv/bin/activate && python database/import_collectibles.py
echo "✓ Collectibles imported"
echo ""

echo "Verifying data..."
# Load environment variables from .env if not already set
if [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
  fi
fi

mysql -u "${DB_USER:-root}" -p"${DB_PASSWORD}" "${DB_NAME:-f76}" -e "
SELECT
  'Weapons' as DataType, COUNT(*) as Count FROM weapons
UNION ALL
SELECT 'Armor', COUNT(*) FROM armor
UNION ALL
SELECT 'Perks', COUNT(*) FROM perks
UNION ALL
SELECT 'Legendary Perks', COUNT(*) FROM legendary_perks
UNION ALL
SELECT 'Weapon Mods', COUNT(*) FROM weapon_mods
UNION ALL
SELECT 'Legendary Effects', COUNT(*) FROM legendary_effects
UNION ALL
SELECT 'Mutations', COUNT(*) FROM mutations
UNION ALL
SELECT 'Consumables', COUNT(*) FROM consumables
UNION ALL
SELECT 'Collectibles', COUNT(*) FROM collectibles;
" 2>/dev/null

echo ""
echo "=========================================="
echo "✓ ALL DATA RESTORED SUCCESSFULLY"
echo "=========================================="
