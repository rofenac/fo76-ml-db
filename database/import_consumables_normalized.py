#!/usr/bin/env python3
"""
Import consumables from Consumables.csv into NORMALIZED MySQL database

UPDATED FOR NORMALIZED SCHEMA - Use this instead of import_consumables.py

Key changes:
- duration converted to INT (seconds)
- numeric fields converted to DECIMAL
- effects stored in consumable_effects table
- special_modifiers stored in consumable_special_modifiers table
"""

import csv
import mysql.connector
import os
import re
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


def build_caches(conn):
    """Build caches for lookup tables"""
    cursor = conn.cursor(dictionary=True)
    caches = {}

    # SPECIAL attributes
    cursor.execute("SELECT id, code FROM special_attributes")
    caches['special'] = {row['code']: row['id'] for row in cursor.fetchall()}

    # Effect types
    cursor.execute("SELECT id, name FROM effect_types")
    caches['effect_types'] = {row['name']: row['id'] for row in cursor.fetchall()}

    cursor.close()
    return caches


def get_or_create_effect_type(conn, name: str, category: str, caches: dict) -> int:
    """Get or create effect type"""
    if name in caches['effect_types']:
        return caches['effect_types'][name]

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO effect_types (name, category) VALUES (%s, %s)", (name, category))
        conn.commit()
        effect_type_id = cursor.lastrowid
        caches['effect_types'][name] = effect_type_id
        cursor.close()
        return effect_type_id
    except:
        # Already exists, fetch it
        cursor.execute("SELECT id FROM effect_types WHERE name = %s", (name,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            caches['effect_types'][name] = result[0]
            return result[0]
        return None


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds"""
    if not duration_str or duration_str.strip() == '':
        return None

    # Look for patterns like "1 hour", "30 minutes", "60 seconds"
    match = re.search(r'(\d+)\s*(hour|minute|second|min|sec|hr)', duration_str, re.IGNORECASE)
    if match:
        value = int(match.group(1))
        unit = match.group(2).lower()

        if unit in ['hour', 'hr']:
            return value * 3600
        elif unit in ['minute', 'min']:
            return value * 60
        elif unit in ['second', 'sec']:
            return value

    # Try to extract just a number (assume seconds)
    match = re.search(r'(\d+)', duration_str)
    if match:
        return int(match.group(1))

    return None


def parse_numeric(value_str: str) -> float:
    """Parse numeric value from string"""
    if not value_str or value_str.strip() == '':
        return None

    # Handle negative values (like rads)
    match = re.search(r'(-?\d+\.?\d*)', value_str)
    if match:
        return float(match.group(1))
    return None


def parse_special_modifiers(modifiers_str: str, caches: dict):
    """
    Parse SPECIAL modifiers string into list of (special_id, modifier) tuples.

    Examples:
    - "+2 STR, -1 INT" -> [(STR_id, 2), (INT_id, -1)]
    - "+3 S, +2 P" -> [(S_id, 3), (P_id, 2)]
    """
    if not modifiers_str or modifiers_str.strip() == '':
        return []

    modifiers = []
    parts = modifiers_str.split(',')

    for part in parts:
        # Match patterns like "+2 STR", "-1 I", "+3 S"
        match = re.match(r'([+-]?\d+)\s*([SPECIALSNG])', part.strip(), re.IGNORECASE)
        if match:
            value = int(match.group(1))
            special_code = match.group(2).upper()

            # Handle full names vs codes
            if len(special_code) > 1:
                # Try to map full names (this is rare, usually just single letter)
                code_map = {
                    'STR': 'S', 'STRENGTH': 'S',
                    'PER': 'P', 'PERCEPTION': 'P',
                    'END': 'E', 'ENDURANCE': 'E',
                    'CHA': 'C', 'CHARISMA': 'C',
                    'INT': 'I', 'INTELLIGENCE': 'I',
                    'AGI': 'A', 'AGILITY': 'A',
                    'LUC': 'L', 'LUCK': 'L'
                }
                special_code = code_map.get(special_code, special_code[0])

            special_id = caches['special'].get(special_code)
            if special_id:
                modifiers.append((special_id, value))

    return modifiers


def import_consumables(conn, caches):
    """Import consumables from CSV"""
    cursor = conn.cursor()

    # Read consumables CSV
    with open(CONSUMABLES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        consumables = list(reader)

    print(f"\nImporting {len(consumables)} consumables...")

    imported_count = 0
    for consumable in consumables:
        try:
            # Parse numeric fields
            duration_seconds = parse_duration(consumable.get('duration', ''))
            hp_restore = parse_numeric(consumable.get('hp_restore', ''))
            rads = parse_numeric(consumable.get('rads', ''))
            hunger = parse_numeric(consumable.get('hunger_satisfaction', ''))
            thirst = parse_numeric(consumable.get('thirst_satisfaction', ''))
            addiction_risk = parse_numeric(consumable.get('addiction_risk', ''))
            disease_risk = parse_numeric(consumable.get('disease_risk', ''))

            # Insert consumable
            insert_sql = """
                INSERT INTO consumables (
                    name, category, subcategory, duration_seconds, hp_restore, rads,
                    hunger_satisfaction, thirst_satisfaction, addiction_risk, disease_risk,
                    weight, value, form_id, crafting_station, source_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    category = VALUES(category),
                    subcategory = VALUES(subcategory),
                    duration_seconds = VALUES(duration_seconds),
                    hp_restore = VALUES(hp_restore),
                    rads = VALUES(rads),
                    hunger_satisfaction = VALUES(hunger_satisfaction),
                    thirst_satisfaction = VALUES(thirst_satisfaction),
                    addiction_risk = VALUES(addiction_risk),
                    disease_risk = VALUES(disease_risk),
                    weight = VALUES(weight),
                    value = VALUES(value),
                    form_id = VALUES(form_id),
                    crafting_station = VALUES(crafting_station),
                    source_url = VALUES(source_url)
            """

            cursor.execute(insert_sql, (
                consumable['name'],
                consumable['category'],
                consumable.get('subcategory') or None,
                duration_seconds,
                hp_restore,
                rads,
                hunger,
                thirst,
                addiction_risk,
                disease_risk,
                float(consumable['weight']) if consumable.get('weight') else None,
                int(consumable['value']) if consumable.get('value') else None,
                consumable.get('form_id') or None,
                consumable.get('crafting_station') or None,
                consumable['source_url']
            ))

            # Get consumable ID
            if cursor.lastrowid > 0:
                consumable_id = cursor.lastrowid
            else:
                # Updated existing, fetch ID
                cursor.execute("SELECT id FROM consumables WHERE name = %s", (consumable['name'],))
                consumable_id = cursor.fetchone()[0]

            # Clear existing effects and modifiers
            cursor.execute("DELETE FROM consumable_effects WHERE consumable_id = %s", (consumable_id,))
            cursor.execute("DELETE FROM consumable_special_modifiers WHERE consumable_id = %s", (consumable_id,))

            # Insert effects
            if consumable.get('effects'):
                effect_type_id = get_or_create_effect_type(conn, 'consumable_effect', 'buff', caches)
                if effect_type_id:
                    cursor.execute("""
                        INSERT INTO consumable_effects (consumable_id, effect_type_id, description)
                        VALUES (%s, %s, %s)
                    """, (consumable_id, effect_type_id, consumable['effects']))

            # Parse and insert SPECIAL modifiers
            if consumable.get('special_modifiers'):
                modifiers = parse_special_modifiers(consumable['special_modifiers'], caches)
                for special_id, modifier_value in modifiers:
                    cursor.execute("""
                        INSERT INTO consumable_special_modifiers
                        (consumable_id, special_id, modifier)
                        VALUES (%s, %s, %s)
                    """, (consumable_id, special_id, modifier_value))

            imported_count += 1

        except Exception as e:
            print(f"ERROR importing {consumable['name']}: {e}")

    conn.commit()
    cursor.close()

    print(f"✓ Successfully imported {imported_count}/{len(consumables)} consumables")
    return imported_count


def verify_import(conn):
    """Verify consumables were imported correctly"""
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

    cursor.execute("SELECT COUNT(*) as count FROM consumable_special_modifiers")
    result = cursor.fetchone()
    modifier_count = result['count']

    cursor.close()

    print(f"\nVerification:")
    print(f"  Total consumables: {total_count}")
    print(f"  - Chems: {chem_count}")
    print(f"  - Food: {food_count}")
    print(f"  - Alcohol: {alcohol_count}")
    print(f"  - Aid: {aid_count}")
    print(f"  SPECIAL modifiers: {modifier_count}")

    return total_count


def main():
    print("="*60)
    print("CONSUMABLE IMPORT SCRIPT (NORMALIZED SCHEMA)")
    print("="*60)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"✓ Connected to database '{DB_CONFIG['database']}'")

        # Build caches
        print("\nBuilding lookup caches...")
        caches = build_caches(conn)

        # Import consumables
        imported = import_consumables(conn, caches)

        # Verify
        total = verify_import(conn)

        print("\n" + "="*60)
        print("IMPORT COMPLETE")
        print("="*60)
        print(f"Consumables in database: {total}")
        print("="*60)

        conn.close()

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
