#!/usr/bin/env python3
"""
Import armor from CSV into normalized database schema.
Handles armor_types, armor_classes, and armor_slots lookup tables properly.
"""
import csv
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import get_db


def import_armor(csv_file: str = "data/input/armor.csv"):
    """Import armor from CSV into armor table with proper FK relationships."""
    print(f"\n=== Importing Armor from {csv_file} ===")

    if not os.path.exists(csv_file):
        print(f"⚠ File not found: {csv_file}")
        sys.exit(1)

    db = get_db()

    # Read CSV and collect unique types/classes/slots
    armor_data = []
    armor_types = set()
    armor_classes = set()
    armor_slots = set()

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            armor_name = row['Name'].strip()
            armor_class = row.get('Class', '').strip()
            armor_slot = row.get('Slot', '').strip()
            armor_type = row.get('Armor Type', '').strip()

            if not armor_name:
                continue

            armor_data.append({
                'name': armor_name,
                'class': armor_class,
                'slot': armor_slot,
                'type': armor_type,
                'damage_resistance': row.get('Damage Resistance', '').strip() or None,
                'energy_resistance': row.get('Energy Resistance', '').strip() or None,
                'radiation_resistance': row.get('Radiation Resistance', '').strip() or None,
                'cryo_resistance': row.get('Cryo Resistance', '').strip() or None,
                'fire_resistance': row.get('Fire Resistance', '').strip() or None,
                'poison_resistance': row.get('Poison Resistance', '').strip() or None,
                'set_name': row.get('Set Name', '').strip() or None,
                'level': row.get('Level', '').strip() or None,
                'source_url': row.get('Source URL', '').strip() or None
            })

            if armor_type:
                armor_types.add(armor_type)
            if armor_class:
                armor_classes.add(armor_class)
            if armor_slot:
                armor_slots.add(armor_slot)

    print(f"Found {len(armor_data)} armor pieces")
    print(f"Found {len(armor_types)} unique armor types")
    print(f"Found {len(armor_classes)} unique armor classes")
    print(f"Found {len(armor_slots)} unique armor slots")

    # Insert armor types
    print("\n✓ Inserting armor types...")
    for atype in sorted(armor_types):
        insert_type = """
            INSERT INTO armor_types (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_type, (atype,))

    # Insert armor classes
    print("✓ Inserting armor classes...")
    for aclass in sorted(armor_classes):
        insert_class = """
            INSERT INTO armor_classes (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_class, (aclass,))

    # Insert armor slots
    print("✓ Inserting armor slots...")
    for aslot in sorted(armor_slots):
        insert_slot = """
            INSERT INTO armor_slots (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_slot, (aslot,))

    # Build lookup maps
    type_map = {}
    class_map = {}
    slot_map = {}

    types_result = db.execute_query("SELECT id, name FROM armor_types")
    for row in types_result:
        type_map[row['name']] = row['id']

    classes_result = db.execute_query("SELECT id, name FROM armor_classes")
    for row in classes_result:
        class_map[row['name']] = row['id']

    slots_result = db.execute_query("SELECT id, name FROM armor_slots")
    for row in slots_result:
        slot_map[row['name']] = row['id']

    print(f"✓ Loaded {len(type_map)} armor type IDs")
    print(f"✓ Loaded {len(class_map)} armor class IDs")
    print(f"✓ Loaded {len(slot_map)} armor slot IDs")

    # Import armor
    print("\n✓ Inserting armor...")
    inserted = 0
    skipped = 0

    for armor in armor_data:
        armor_type_id = type_map.get(armor['type']) if armor['type'] else None
        armor_class_id = class_map.get(armor['class']) if armor['class'] else None
        armor_slot_id = slot_map.get(armor['slot']) if armor['slot'] else None

        insert_armor = """
            INSERT INTO armor
            (name, armor_type_id, armor_class_id, armor_slot_id,
             damage_resistance, energy_resistance, radiation_resistance,
             cryo_resistance, fire_resistance, poison_resistance,
             set_name, level, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                armor_type_id = VALUES(armor_type_id),
                armor_class_id = VALUES(armor_class_id),
                armor_slot_id = VALUES(armor_slot_id),
                damage_resistance = VALUES(damage_resistance),
                energy_resistance = VALUES(energy_resistance),
                radiation_resistance = VALUES(radiation_resistance),
                cryo_resistance = VALUES(cryo_resistance),
                fire_resistance = VALUES(fire_resistance),
                poison_resistance = VALUES(poison_resistance),
                set_name = VALUES(set_name),
                level = VALUES(level),
                source_url = VALUES(source_url)
        """

        try:
            db.execute_query(insert_armor, (
                armor['name'],
                armor_type_id,
                armor_class_id,
                armor_slot_id,
                armor['damage_resistance'],
                armor['energy_resistance'],
                armor['radiation_resistance'],
                armor['cryo_resistance'],
                armor['fire_resistance'],
                armor['poison_resistance'],
                armor['set_name'],
                armor['level'],
                armor['source_url']
            ))
            inserted += 1

            if inserted % 50 == 0:
                print(f"  Inserted {inserted} armor pieces...")

        except Exception as e:
            print(f"✗ Error inserting armor '{armor['name']}': {e}")
            skipped += 1
            continue

    print(f"\n✓ Import complete!")
    print(f"  Inserted/Updated: {inserted}")
    print(f"  Skipped: {skipped}")

    # Verify
    count_query = "SELECT COUNT(*) as count FROM armor"
    result = db.execute_query(count_query)
    total = result[0]['count']
    print(f"  Total in database: {total}")

    # Show breakdown
    breakdown_query = """
        SELECT
            at.name as type,
            ac.name as class,
            COUNT(*) as count
        FROM armor a
        LEFT JOIN armor_types at ON a.armor_type_id = at.id
        LEFT JOIN armor_classes ac ON a.armor_class_id = ac.id
        GROUP BY at.name, ac.name
        ORDER BY at.name, ac.name
    """
    breakdown = db.execute_query(breakdown_query)
    print("\nBreakdown by type and class:")
    for row in breakdown:
        atype = row['type'] or 'NULL'
        aclass = row['class'] or 'NULL'
        print(f"  {atype:15s} / {aclass:15s}: {row['count']:3d} pieces")

    return inserted


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import armor from CSV')
    parser.add_argument('csv_file', nargs='?',
                       default='data/input/armor.csv',
                       help='CSV file to import (default: data/input/armor.csv)')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    import_armor(args.csv_file)
