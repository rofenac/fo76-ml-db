#!/usr/bin/env python3
"""
Import legendary effects from scraped CSV into database
"""
import csv
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import get_db

def import_legendary_effects(csv_file: str):
    """Import legendary effects from CSV"""
    db = get_db()

    # Read CSV and deduplicate
    effects_map = {}  # Key: (name, item_type), Value: effect data

    print(f"Reading CSV: {csv_file}")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name'].strip()
            item_type = row['item_type'].strip()

            # Skip header rows or empty names
            if not name or name == 'Name' or len(name) < 2:
                continue

            # Use the row with form_id if available (prefer the more complete entry)
            key = (name, item_type)
            if key not in effects_map or row.get('form_id'):
                effects_map[key] = row

    print(f"Found {len(effects_map)} unique legendary effects after deduplication")

    # Ensure categories exist
    standard_categories = ['Prefix', 'Major', 'Minor', 'Additional']
    for category_name in standard_categories:
        insert_cat = """
            INSERT INTO legendary_effect_categories (name)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE name = name
        """
        db.execute_query(insert_cat, (category_name,))

    print(f"✓ Ensured legendary effect categories exist")

    # Get category IDs
    category_map = {}
    categories = db.execute_query("SELECT id, name FROM legendary_effect_categories")
    for cat in categories:
        category_map[cat['name']] = cat['id']

    print(f"Category mapping: {category_map}")

    # Insert effects
    inserted = 0
    skipped = 0

    for (name, item_type), row in effects_map.items():
        category = row['category'].strip()
        category_id = category_map.get(category)

        if not category_id:
            print(f"Warning: Unknown category '{category}' for {name}, defaulting to Prefix")
            category_id = category_map['Prefix']

        star_level = int(row['star_level']) if row['star_level'] else 1
        description = row['description'].strip() if row['description'] else None
        effect_value = row['effect_value'].strip() if row['effect_value'] else None
        notes = row['notes'].strip() if row['notes'] and row['notes'] != '–' else None
        form_id = row['form_id'].strip() if row['form_id'] and row['form_id'] != '' else None
        source_url = row['source_url'].strip() if row['source_url'] else None

        # Insert effect
        insert_query = """
            INSERT INTO legendary_effects
            (name, category_id, star_level, item_type, description, effect_value, notes, form_id, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category_id = VALUES(category_id),
                star_level = VALUES(star_level),
                description = VALUES(description),
                effect_value = VALUES(effect_value),
                notes = VALUES(notes),
                form_id = VALUES(form_id),
                source_url = VALUES(source_url)
        """

        try:
            db.execute_query(insert_query, (
                name, category_id, star_level, item_type,
                description, effect_value, notes, form_id, source_url
            ))

            # Insert condition if present
            condition_type = row.get('condition_type', '').strip()
            condition_description = row.get('condition_description', '').strip()

            if condition_type and condition_description:
                # Get the effect_id
                effect_id_query = "SELECT id FROM legendary_effects WHERE name = %s AND item_type = %s"
                effect_result = db.execute_query(effect_id_query, (name, item_type))

                if effect_result:
                    effect_id = effect_result[0]['id']

                    # Insert condition
                    condition_query = """
                        INSERT INTO legendary_effect_conditions
                        (effect_id, condition_type, condition_description)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            condition_description = VALUES(condition_description)
                    """
                    db.execute_query(condition_query, (effect_id, condition_type, condition_description))

            inserted += 1
            if inserted % 50 == 0:
                print(f"Inserted {inserted} effects...")

        except Exception as e:
            print(f"Error inserting {name} ({item_type}): {e}")
            skipped += 1
            continue

    print(f"\nImport complete!")
    print(f"  Inserted/Updated: {inserted}")
    print(f"  Skipped: {skipped}")

    # Verify
    count_query = "SELECT COUNT(*) as count FROM legendary_effects"
    result = db.execute_query(count_query)
    total = result[0]['count']
    print(f"  Total in database: {total}")

    # Show breakdown by type and star level
    breakdown_query = """
        SELECT item_type, star_level, COUNT(*) as count
        FROM legendary_effects
        GROUP BY item_type, star_level
        ORDER BY item_type, star_level
    """
    breakdown = db.execute_query(breakdown_query)
    print("\nBreakdown by type and star level:")
    for row in breakdown:
        print(f"  {row['item_type']:8s} {row['star_level']}-star: {row['count']:3d} effects")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import legendary effects from CSV')
    parser.add_argument('csv_file', nargs='?',
                       default='data/input/legendary_effects.csv',
                       help='CSV file to import (default: data/input/legendary_effects.csv)')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    import_legendary_effects(args.csv_file)
