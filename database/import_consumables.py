#!/usr/bin/env python3
"""
Import consumables from Consumables.csv into MySQL database

Usage:
    python import_consumables.py
"""

import csv
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection config
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'secret'),
    'database': os.getenv('DB_NAME', 'f76')
}

# File paths
CONSUMABLES_CSV = 'data/input/Consumables.csv'


def import_consumables():
    """Import consumables from CSV"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Read consumables CSV
    with open(CONSUMABLES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        consumables = list(reader)

    print(f"\nImporting {len(consumables)} consumables...")

    insert_sql = """
        INSERT INTO consumables (
            name, category, subcategory, effects, duration, hp_restore, rads,
            hunger_satisfaction, thirst_satisfaction, special_modifiers, addiction_risk,
            disease_risk, weight, value, form_id, crafting_station, source_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            category = VALUES(category),
            subcategory = VALUES(subcategory),
            effects = VALUES(effects),
            duration = VALUES(duration),
            hp_restore = VALUES(hp_restore),
            rads = VALUES(rads),
            hunger_satisfaction = VALUES(hunger_satisfaction),
            thirst_satisfaction = VALUES(thirst_satisfaction),
            special_modifiers = VALUES(special_modifiers),
            addiction_risk = VALUES(addiction_risk),
            disease_risk = VALUES(disease_risk),
            weight = VALUES(weight),
            value = VALUES(value),
            form_id = VALUES(form_id),
            crafting_station = VALUES(crafting_station),
            source_url = VALUES(source_url)
    """

    imported_count = 0
    for consumable in consumables:
        try:
            cursor.execute(insert_sql, (
                consumable['name'],
                consumable['category'],
                consumable['subcategory'] or None,
                consumable['effects'] or None,
                consumable['duration'] or None,
                consumable['hp_restore'] or None,
                consumable['rads'] or None,
                consumable['hunger_satisfaction'] or None,
                consumable['thirst_satisfaction'] or None,
                consumable['special_modifiers'] or None,
                consumable['addiction_risk'] or None,
                consumable['disease_risk'] or None,
                float(consumable['weight']) if consumable['weight'] else None,
                int(consumable['value']) if consumable['value'] else None,
                consumable['form_id'] or None,
                consumable['crafting_station'] or None,
                consumable['source_url']
            ))
            imported_count += 1
        except Exception as e:
            print(f"ERROR importing {consumable['name']}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✓ Successfully imported {imported_count}/{len(consumables)} consumables")
    return imported_count


def verify_import():
    """Verify consumables were imported correctly"""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as count FROM consumables")
    result = cursor.fetchone()
    total_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM consumables WHERE category = 'chem'")
    result = cursor.fetchone()
    chem_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM consumables WHERE category = 'food'")
    result = cursor.fetchone()
    food_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM consumables WHERE category = 'alcohol'")
    result = cursor.fetchone()
    alcohol_count = result['count']

    cursor.execute("SELECT COUNT(*) as count FROM consumables WHERE category = 'aid'")
    result = cursor.fetchone()
    aid_count = result['count']

    cursor.close()
    conn.close()

    print(f"\nVerification:")
    print(f"  Total consumables: {total_count}")
    print(f"  - Chems: {chem_count}")
    print(f"  - Food: {food_count}")
    print(f"  - Alcohol: {alcohol_count}")
    print(f"  - Aid: {aid_count}")

    return total_count


def main():
    print("="*60)
    print("CONSUMABLE IMPORT SCRIPT")
    print("="*60)

    try:
        # Import consumables
        imported = import_consumables()

        # Verify
        total = verify_import()

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Consumables in database: {total}")
        print("="*60)

    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        print(f"Make sure {CONSUMABLES_CSV} exists")
        exit(1)
    except mysql.connector.Error as e:
        print(f"\nDATABASE ERROR: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
