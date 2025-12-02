#!/usr/bin/env python3
"""
Import legendary perks from CSV into legendary_perks and legendary_perk_ranks tables
"""
import csv
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import get_db


def import_legendary_perks(csv_file: str = "data/input/legendary_perks.csv"):
    """Import legendary perks from CSV into legendary_perks and legendary_perk_ranks tables."""
    print(f"\n=== Importing Legendary Perks from {csv_file} ===")

    if not os.path.exists(csv_file):
        print(f"⚠ File not found: {csv_file}")
        sys.exit(1)

    db = get_db()

    # Read all rows and group by perk name
    perk_data = {}

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            perk_name = row['name'].strip()

            if not perk_name:
                continue

            # Group all ranks for this perk
            if perk_name not in perk_data:
                perk_data[perk_name] = {
                    'race': row.get('race', '').strip() or 'Human, Ghoul',
                    'ranks': []
                }

            # Add this rank's data
            perk_data[perk_name]['ranks'].append({
                'rank': int(row.get('rank', 1)),
                'description': row.get('description', '').strip(),
                'effect_value': row.get('effect_value', '').strip() or None,
                'effect_type': row.get('effect_type', '').strip() or None,
                'form_id': row.get('form_id', '').strip() or None
            })

    print(f"Found {len(perk_data)} unique legendary perks with {sum(len(p['ranks']) for p in perk_data.values())} total ranks")

    perks_inserted = 0
    ranks_inserted = 0

    for perk_name, data in perk_data.items():
        try:
            # Create a base description from rank 1
            base_description = data['ranks'][0]['description'] if data['ranks'] else None

            # Insert base legendary perk
            insert_perk = """
                INSERT INTO legendary_perks (name, description, race)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    description = VALUES(description),
                    race = VALUES(race)
            """
            db.execute_query(insert_perk, (perk_name, base_description, data['race']))

            # Get the legendary_perk_id
            get_id = "SELECT id FROM legendary_perks WHERE name = %s"
            result = db.execute_query(get_id, (perk_name,))
            legendary_perk_id = result[0]['id']

            perks_inserted += 1

            # Insert all ranks for this legendary perk
            for rank_data in data['ranks']:
                insert_rank = """
                    INSERT INTO legendary_perk_ranks
                    (legendary_perk_id, `rank`, description, effect_value, effect_type)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        description = VALUES(description),
                        effect_value = VALUES(effect_value),
                        effect_type = VALUES(effect_type)
                """
                db.execute_query(insert_rank, (
                    legendary_perk_id,
                    rank_data['rank'],
                    rank_data['description'],
                    rank_data['effect_value'],
                    rank_data['effect_type']
                ))
                ranks_inserted += 1

        except Exception as e:
            print(f"✗ Error inserting legendary perk '{perk_name}': {e}")
            continue

    print(f"✓ Inserted/Updated {perks_inserted} legendary perks")
    print(f"✓ Inserted/Updated {ranks_inserted} legendary perk ranks")

    # Verify
    count_query = "SELECT COUNT(*) as count FROM legendary_perks"
    result = db.execute_query(count_query)
    total_perks = result[0]['count']

    ranks_count_query = "SELECT COUNT(*) as count FROM legendary_perk_ranks"
    result = db.execute_query(ranks_count_query)
    total_ranks = result[0]['count']

    print(f"\nDatabase totals:")
    print(f"  Legendary perks: {total_perks}")
    print(f"  Legendary perk ranks: {total_ranks}")

    return perks_inserted


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import legendary perks from CSV')
    parser.add_argument('csv_file', nargs='?',
                       default='data/input/legendary_perks.csv',
                       help='CSV file to import (default: data/input/legendary_perks.csv)')

    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)

    import_legendary_perks(args.csv_file)
