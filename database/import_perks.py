#!/usr/bin/env python3
"""
Import perks from CSV into normalized database schema.
"""
import csv
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_utils import get_db


def import_perks(csv_file: str = "data/input/perks.csv"):
    """Import perks from CSV into perks and perk_ranks tables."""
    print(f"\n=== Importing Perks from {csv_file} ===")

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
                    'special': row.get('special', '').strip() or None,
                    'level': int(row.get('level', 0)) if row.get('level', '').strip() else None,
                    'race': row.get('race', '').strip() or None,
                    'ranks': []
                }

            # Add this rank's data
            perk_data[perk_name]['ranks'].append({
                'rank': int(row.get('rank', 1)),
                'description': row.get('description', '').strip(),
                'form_id': row.get('form_id', '').strip() or None
            })

    print(f"Found {len(perk_data)} unique perks with {sum(len(p['ranks']) for p in perk_data.values())} total ranks")

    perks_inserted = 0
    ranks_inserted = 0

    for perk_name, data in perk_data.items():
        try:
            # Insert base perk
            insert_perk = """
                INSERT INTO perks (name, special, level, race)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    special = VALUES(special),
                    level = VALUES(level),
                    race = VALUES(race)
            """
            db.execute_query(insert_perk, (perk_name, data['special'], data['level'], data['race']))

            # Get perk ID
            perk_id_result = db.execute_query("SELECT id FROM perks WHERE name = %s", (perk_name,))
            perk_id = perk_id_result[0]['id']
            perks_inserted += 1

            # Delete existing ranks for this perk
            db.execute_query("DELETE FROM perk_ranks WHERE perk_id = %s", (perk_id,))

            # Insert all ranks for this perk
            for rank_data in data['ranks']:
                insert_rank = """
                    INSERT INTO perk_ranks (perk_id, `rank`, description, form_id)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute_query(insert_rank, (perk_id, rank_data['rank'], rank_data['description'], rank_data['form_id']))
                ranks_inserted += 1

        except Exception as e:
            print(f"✗ Error inserting perk '{perk_name}': {e}")
            continue

    print(f"\n✓ Import complete!")
    print(f"  Inserted/Updated: {perks_inserted} perks")
    print(f"  Inserted: {ranks_inserted} perk ranks")

    # Verify
    count_query = "SELECT COUNT(*) as count FROM perks"
    result = db.execute_query(count_query)
    total = result[0]['count']
    print(f"  Total in database: {total}")


if __name__ == "__main__":
    import_perks()
