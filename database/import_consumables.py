#!/usr/bin/env python3
"""
Import all consumables from individual CSV files into normalized database.
Authoritative sources: Chem_scraped.csv, Drink_scraped.csv, Food_scraped.csv, Soup_scraped.csv

Usage:
    python import_consumables.py
"""
import sys
import os
import csv
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from database.db_utils import get_db


def normalize_category(item_name, csv_category, csv_source):
    """
    Normalize category based on item name and source CSV.
    Database categories: 'food', 'drink', 'chem', 'aid', 'alcohol', 'beverage'
    """
    item_lower = item_name.lower()

    # Source-based normalization
    if csv_source == 'Chem':
        # Aid items that might be in chem CSV
        if any(x in item_lower for x in ['stimpak', 'radaway', 'rad-x', 'med-x']):
            return 'aid'
        return 'chem'

    elif csv_source == 'Drink':
        # Alcoholic beverages
        if csv_category == 'alcohol':
            return 'alcohol'
        # Nuka-Cola items
        if 'nuka-cola' in item_lower or 'nukashine' in item_lower:
            return 'beverage'
        # Everything else is a drink
        return 'drink'

    elif csv_source in ['Food', 'Soup']:
        return 'food'

    # Fallback to CSV category if valid
    valid_categories = ['food', 'drink', 'chem', 'aid', 'alcohol', 'beverage']
    if csv_category and csv_category in valid_categories:
        return csv_category

    return 'food'


def clean_field(value):
    """Clean and normalize field values."""
    if not value or value.strip() == '':
        return None
    return value.strip()


def clean_numeric(value):
    """Clean numeric fields."""
    if not value or value.strip() == '':
        return None
    value = value.strip().replace('%', '')
    try:
        return float(value) if '.' in value else int(value)
    except ValueError:
        return None


def import_csv(csv_path, csv_source):
    """Import consumables from a single CSV file."""
    print(f"\n📦 Importing {csv_source}...")

    if not os.path.exists(csv_path):
        print(f"  ❌ File not found: {csv_path}")
        return 0

    db = get_db()
    imported = 0
    skipped = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = clean_field(row.get('name'))
            if not name:
                continue

            # Check if exists
            existing = db.execute_query(
                "SELECT id FROM consumables WHERE name = %s", (name,)
            )

            if existing:
                print(f"  ⏭️  Skipping: {name}")
                skipped += 1
                continue

            # Normalize category
            csv_category = clean_field(row.get('category'))
            category = normalize_category(name, csv_category, csv_source)
            subcategory = 'soup' if csv_source == 'Soup' else clean_field(row.get('subcategory'))

            # Insert
            query = """
                INSERT INTO consumables (
                    name, category, subcategory, effects, duration, hp_restore, rads,
                    hunger_satisfaction, thirst_satisfaction, special_modifiers,
                    addiction_risk, disease_risk, weight, value, form_id,
                    crafting_station, source_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            try:
                db.execute_query(query, (
                    name,
                    category,
                    subcategory,
                    clean_field(row.get('effects')),
                    clean_field(row.get('duration')),
                    clean_field(row.get('hp_restore')),
                    clean_field(row.get('rads')),
                    clean_field(row.get('hunger_satisfaction')),
                    clean_field(row.get('thirst_satisfaction')),
                    clean_field(row.get('special_modifiers')),
                    clean_field(row.get('addiction_risk')),
                    clean_field(row.get('disease_risk')),
                    clean_numeric(row.get('weight')),
                    clean_numeric(row.get('value')),
                    clean_field(row.get('form_id')),
                    clean_field(row.get('crafting_station')),
                    clean_field(row.get('source_url'))
                ))
                imported += 1
                print(f"  ✅ {name} [{category}]")
            except Exception as e:
                print(f"  ❌ Error: {name} - {e}")

    print(f"  📊 Imported: {imported}, Skipped: {skipped}")
    return imported


def main():
    print("=" * 80)
    print("FALLOUT 76 CONSUMABLES IMPORT")
    print("=" * 80)
    print("\nAuthoritative sources:")
    print("  - Chem_scraped.csv")
    print("  - Drink_scraped.csv")
    print("  - Food_scraped.csv")
    print("  - Soup_scraped.csv")

    db = get_db()

    # Current count
    current = db.execute_query("SELECT COUNT(*) as count FROM consumables")
    current_count = current[0]['count'] if current else 0
    print(f"\n📊 Current database: {current_count} consumables\n")

    # Import from each CSV
    base_path = Path(__file__).parent.parent / 'data' / 'input'
    csv_files = [
        (base_path / 'chems.csv', 'Chem'),
        (base_path / 'drinks.csv', 'Drink'),
        (base_path / 'food.csv', 'Food'),
        (base_path / 'soup.csv', 'Soup'),
    ]

    total_imported = 0
    for csv_path, source in csv_files:
        total_imported += import_csv(csv_path, source)

    # Final count
    final = db.execute_query("SELECT COUNT(*) as count FROM consumables")
    final_count = final[0]['count'] if final else 0

    # Category breakdown
    categories = db.execute_query("""
        SELECT category, COUNT(*) as count
        FROM consumables
        GROUP BY category
        ORDER BY count DESC
    """)

    print("\n" + "=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"  Before:  {current_count} consumables")
    print(f"  After:   {final_count} consumables")
    print(f"  Added:   {total_imported} new items")
    print(f"\nCategory breakdown:")
    for cat in categories:
        print(f"  {cat['category']:15} {cat['count']:4} items")
    print("\n✅ Import complete!\n")


if __name__ == "__main__":
    main()
