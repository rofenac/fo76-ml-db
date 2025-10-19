#!/bin/bash
# Master import script - restores all data to database

set -e  # Exit on error

echo "=========================================="
echo "MASTER DATA IMPORT - RESTORING ALL DATA"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

echo "[1/5] Importing Weapons & Perks..."
source .venv/bin/activate && python database/import_to_db.py
echo "✓ Weapons & Perks imported"
echo ""

echo "[2/5] Importing Armor..."
source .venv/bin/activate && python database/import_armor.py
echo "✓ Armor imported"
echo ""

echo "[3/5] Importing Mutations..."
source .venv/bin/activate && python database/import_mutations.py
echo "✓ Mutations imported"
echo ""

echo "[4/5] Importing Consumables..."
source .venv/bin/activate && python database/import_consumables.py
echo "✓ Consumables imported"
echo ""

echo "[5/5] Verifying data..."
mysql -u root -psecret f76 -e "
SELECT
  'Weapons' as DataType, COUNT(*) as Count FROM weapons
UNION ALL
SELECT 'Armor', COUNT(*) FROM armor
UNION ALL
SELECT 'Perks', COUNT(*) FROM perks
UNION ALL
SELECT 'Legendary Perks', COUNT(*) FROM legendary_perks
UNION ALL
SELECT 'Mutations', COUNT(*) FROM mutations
UNION ALL
SELECT 'Consumables', COUNT(*) FROM consumables;
" 2>/dev/null

echo ""
echo "=========================================="
echo "✓ ALL DATA RESTORED SUCCESSFULLY"
echo "=========================================="
