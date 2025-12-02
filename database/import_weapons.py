#!/usr/bin/env python3
"""
Import weapons from CSV into normalized database schema.
Handles weapon_types and weapon_classes lookup tables properly.
"""
import csv
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import get_db


def import_weapons(csv_file: str = "data/input/weapons.csv"):
    """Import weapons from CSV into weapons table with proper FK relationships."""
    print(f"\n=== Importing Weapons from {csv_file} ===")

    if not os.path.exists(csv_file):
        print(f"⚠ File not found: {csv_file}")
        sys.exit(1)

    db = get_db()

    # Read CSV and collect unique types/classes
    weapons_data = []
    weapon_types = set()
    weapon_classes = set()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            weapon_name = row['Name'].strip()
            weapon_type = row.get('Type', '').strip()
            weapon_class = row.get('Class', '').strip()

            if not weapon_name:
                continue

            weapons_data.append({
                'name': weapon_name,
                'type': weapon_type,
                'class': weapon_class,
                'level': row.get('Level', '').strip() or None,
                'damage': row.get('Damage', '').strip() or None,
                'perks_raw': row.get('Perks', '').strip() or None,
                'source_url': row.get('Source URL', '').strip() or None
            })

            if weapon_type:
                weapon_types.add(weapon_type)
            if weapon_class:
                weapon_classes.add(weapon_class)

    print(f"Found {len(weapons_data)} weapons")
    print(f"Found {len(weapon_types)} unique weapon types")
    print(f"Found {len(weapon_classes)} unique weapon classes")

    # Insert weapon types
    print("\n✓ Inserting weapon types...")
    for wtype in sorted(weapon_types):
        insert_type = """
            INSERT INTO weapon_types (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_type, (wtype,))

    # Insert weapon classes
    print("✓ Inserting weapon classes...")
    for wclass in sorted(weapon_classes):
        insert_class = """
            INSERT INTO weapon_classes (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_class, (wclass,))

    # Build lookup maps for types and classes
    type_map = {}
    class_map = {}

    types_result = db.execute_query("SELECT id, name FROM weapon_types")
    for row in types_result:
        type_map[row['name']] = row['id']

    classes_result = db.execute_query("SELECT id, name FROM weapon_classes")
    for row in classes_result:
        class_map[row['name']] = row['id']

    print(f"✓ Loaded {len(type_map)} weapon type IDs")
    print(f"✓ Loaded {len(class_map)} weapon class IDs")

    # Import weapons
    print("\n✓ Inserting weapons...")
    inserted = 0
    skipped = 0

    for weapon in weapons_data:
        weapon_type_id = type_map.get(weapon['type']) if weapon['type'] else None
        weapon_class_id = class_map.get(weapon['class']) if weapon['class'] else None

        insert_weapon = """
            INSERT INTO weapons
            (name, weapon_type_id, weapon_class_id, level, damage, perks_raw, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                weapon_type_id = VALUES(weapon_type_id),
                weapon_class_id = VALUES(weapon_class_id),
                level = VALUES(level),
                damage = VALUES(damage),
                perks_raw = VALUES(perks_raw),
                source_url = VALUES(source_url)
        """

        try:
            db.execute_query(insert_weapon, (
                weapon['name'],
                weapon_type_id,
                weapon_class_id,
                weapon['level'],
                weapon['damage'],
                weapon['perks_raw'],
                weapon['source_url']
            ))
            inserted += 1

            if inserted % 50 == 0:
                print(f"  Inserted {inserted} weapons...")

        except Exception as e:
            print(f"✗ Error inserting weapon '{weapon['name']}': {e}")
            skipped += 1
            continue

    print(f"\n✓ Import complete!")
    print(f"  Inserted/Updated: {inserted}")
    print(f"  Skipped: {skipped}")

    # Verify
    count_query = "SELECT COUNT(*) as count FROM weapons"
    result = db.execute_query(count_query)
    total = result[0]['count']
    print(f"  Total in database: {total}")

    # Show breakdown by type and class
    breakdown_query = """
        SELECT
            wt.name as type,
            wc.name as class,
            COUNT(*) as count
        FROM weapons w
        LEFT JOIN weapon_types wt ON w.weapon_type_id = wt.id
        LEFT JOIN weapon_classes wc ON w.weapon_class_id = wc.id
        GROUP BY wt.name, wc.name
        ORDER BY wt.name, wc.name
    """
    breakdown = db.execute_query(breakdown_query)
    print("\nBreakdown by type and class:")
    for row in breakdown:
        wtype = row['type'] or 'NULL'
        wclass = row['class'] or 'NULL'
        print(f"  {wtype:10s} / {wclass:30s}: {row['count']:3d} weapons")

    return inserted


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import weapons from CSV')
    parser.add_argument('csv_file', nargs='?',
                       default='data/input/weapons.csv',
                       help='CSV file to import (default: data/input/weapons.csv)')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    import_weapons(args.csv_file)
